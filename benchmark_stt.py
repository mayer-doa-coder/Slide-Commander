#!/usr/bin/env python3
"""
benchmark_stt.py — SlideCommander STT / Keyword-Spotting Benchmark Suite

Exact workflow:
  pip install vosk faster-whisper pocketsphinx psutil pyaudio
  # (Optional) pip install torch torchaudio   ← adds Silero engine
  python benchmark_stt.py --record --samples 10 --audio-dir test_audio/
  python benchmark_stt.py --audio-dir test_audio/ --output results.json
  # Paste results.json into research_log.md §3.4 and complete §5.

Engines benchmarked by default (--engines all):
  vosk           — streaming Kaldi ASR, 40 MB model, lowest latency
  faster-whisper — CTranslate2 Whisper int8, auto-downloaded model
  pocketsphinx   — keyword-spotting mode, bundled en-US model

Optional engine (--engines silero):
  silero         — neural CTC STT via PyTorch Hub (~25 MB)
"""

from __future__ import annotations

import abc
import argparse
import dataclasses
import json
import math
import os
import platform
import sys
import tempfile
import time
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── vocabulary ────────────────────────────────────────────────────────────────
COMMANDS: List[str] = ["next", "back", "start", "end", "pause"]

# ── audio constants ───────────────────────────────────────────────────────────
SAMPLE_RATE:  int   = 16_000        # Hz — required by every engine
SAMPLE_WIDTH: int   = 2             # bytes (int16 PCM)
CHUNK_SAMPLES: int  = 4_000         # 250 ms per streaming chunk

# ── acceptance targets ────────────────────────────────────────────────────────
LATENCY_BUDGET_MS:   float = 300.0
ACCURACY_TARGET_PCT: float = 95.0

# ── default engine set ────────────────────────────────────────────────────────
DEFAULT_ENGINES: List[str] = ["vosk", "faster-whisper", "pocketsphinx"]

# ── optional psutil ───────────────────────────────────────────────────────────
try:
    import psutil as _psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


# ─────────────────────────────────────────────────────────────────────────────
# Data containers
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class RecognitionResult:
    keyword:      Optional[str]  # first COMMANDS word found in transcript, or None
    transcript:   str            # raw text from the engine
    inference_ms: float          # wall-clock inference time (ms)
    rtf:          float          # inference_ms / audio_duration_ms

    def matched(self, expected: str) -> bool:
        return self.keyword == expected


@dataclasses.dataclass
class FileRecord:
    path:     str
    expected: str
    result:   RecognitionResult

    @property
    def correct(self) -> bool:
        return self.result.matched(self.expected)


@dataclasses.dataclass
class EngineReport:
    engine_name:      str
    load_time_ms:     float
    memory_delta_mb:  float
    records:          List[FileRecord]
    error:            Optional[str] = None

    # ── derived metrics ───────────────────────────────────────────────────────

    @property
    def accuracy_pct(self) -> float:
        if not self.records:
            return 0.0
        return sum(1 for r in self.records if r.correct) / len(self.records) * 100

    @property
    def median_latency_ms(self) -> float:
        vals = sorted(r.result.inference_ms for r in self.records)
        if not vals:
            return 0.0
        return vals[len(vals) // 2]

    @property
    def p95_latency_ms(self) -> float:
        vals = sorted(r.result.inference_ms for r in self.records)
        if not vals:
            return 0.0
        return vals[min(int(len(vals) * 0.95), len(vals) - 1)]

    @property
    def mean_rtf(self) -> float:
        vals = [r.result.rtf for r in self.records]
        return sum(vals) / len(vals) if vals else 0.0

    def per_keyword_accuracy(self) -> Dict[str, float]:
        buckets: Dict[str, List[bool]] = {c: [] for c in COMMANDS}
        for r in self.records:
            buckets.setdefault(r.expected, []).append(r.correct)
        return {k: (sum(v) / len(v) * 100 if v else 0.0) for k, v in buckets.items()}

    @property
    def meets_latency(self) -> bool:
        return self.median_latency_ms < LATENCY_BUDGET_MS

    @property
    def meets_accuracy(self) -> bool:
        return self.accuracy_pct >= ACCURACY_TARGET_PCT

    def to_dict(self) -> dict:
        return {
            "engine":              self.engine_name,
            "load_time_ms":        round(self.load_time_ms, 1),
            "memory_delta_mb":     round(self.memory_delta_mb, 1),
            "accuracy_pct":        round(self.accuracy_pct, 1),
            "median_latency_ms":   round(self.median_latency_ms, 1),
            "p95_latency_ms":      round(self.p95_latency_ms, 1),
            "mean_rtf":            round(self.mean_rtf, 3),
            "per_keyword_accuracy": {
                k: round(v, 1) for k, v in self.per_keyword_accuracy().items()
            },
            "sample_count":  len(self.records),
            "meets_latency": self.meets_latency,
            "meets_accuracy": self.meets_accuracy,
            "error":         self.error,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Abstract engine base
# ─────────────────────────────────────────────────────────────────────────────

class EngineBase(abc.ABC):
    """
    Common interface for every STT / keyword-spotting engine wrapper.

    All engines receive raw int16 PCM bytes at SAMPLE_RATE and return a
    RecognitionResult.  Each engine times itself internally.
    """

    NAME: str = "base"

    @abc.abstractmethod
    def load(self, **kwargs) -> None:
        """Initialise model, allocate resources."""

    @abc.abstractmethod
    def recognize(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> RecognitionResult:
        """Run recognition on raw 16-bit PCM mono bytes."""

    def teardown(self) -> None:
        """Release resources after the benchmark run."""

    # ── shared helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _extract_keyword(text: str) -> Optional[str]:
        text = text.lower()
        # Whole-word match first (avoids 'end' matching inside 'pretend')
        words = text.split()
        for cmd in COMMANDS:
            if cmd in words:
                return cmd
        # Substring fallback for partial transcripts
        for cmd in COMMANDS:
            if cmd in text:
                return cmd
        return None

    @staticmethod
    def _audio_ms(audio_bytes: bytes, sample_rate: int) -> float:
        return len(audio_bytes) / SAMPLE_WIDTH / sample_rate * 1000

    @staticmethod
    def _write_tmp_wav(audio_bytes: bytes, sample_rate: int) -> str:
        """Write PCM bytes to a named temp file (caller must delete it)."""
        fd, path = tempfile.mkstemp(suffix=".wav")
        with os.fdopen(fd, "wb") as raw:
            with wave.open(raw, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_bytes)
        return path


# ─────────────────────────────────────────────────────────────────────────────
# Engine 1 — Vosk
# ─────────────────────────────────────────────────────────────────────────────

class VoskEngine(EngineBase):
    """
    Vosk offline streaming STT.

    Install : pip install vosk
    Model   : Download vosk-model-en-us-0.22.zip (~40 MB) from
              https://alphacephei.com/vosk/models  then extract it.
    Run     : python benchmark_stt.py --vosk-model vosk-model-en-us-0.22 ...
    """

    NAME = "vosk"

    def __init__(self):
        self._model = None
        self._vosk  = None

    def load(self, vosk_model: str = "vosk-model-en-us-0.22", **_) -> None:
        try:
            import vosk
            vosk.SetLogLevel(-1)
            self._vosk  = vosk
            self._model = vosk.Model(vosk_model)
        except ImportError:
            raise ImportError("pip install vosk")
        except Exception as exc:
            raise RuntimeError(
                f"Vosk model not found at '{vosk_model}'.\n"
                "  Download: https://alphacephei.com/vosk/models\n"
                f"  Original error: {exc}"
            ) from exc

    def recognize(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> RecognitionResult:
        rec = self._vosk.KaldiRecognizer(self._model, sample_rate)
        rec.SetWords(False)
        parts: List[str] = []

        t0 = time.perf_counter()
        for off in range(0, len(audio_bytes), CHUNK_SAMPLES * SAMPLE_WIDTH):
            chunk = audio_bytes[off : off + CHUNK_SAMPLES * SAMPLE_WIDTH]
            if rec.AcceptWaveform(chunk):
                t = json.loads(rec.Result()).get("text", "")
                if t:
                    parts.append(t)
        final = json.loads(rec.FinalResult()).get("text", "")
        if final:
            parts.append(final)
        elapsed = (time.perf_counter() - t0) * 1_000

        transcript = " ".join(parts)
        return RecognitionResult(
            keyword=self._extract_keyword(transcript),
            transcript=transcript,
            inference_ms=elapsed,
            rtf=elapsed / max(self._audio_ms(audio_bytes, sample_rate), 1.0),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Engine 2 — Faster-Whisper
# ─────────────────────────────────────────────────────────────────────────────

class FasterWhisperEngine(EngineBase):
    """
    Faster-Whisper: CTranslate2-optimised Whisper running on CPU with int8.

    Install : pip install faster-whisper
    Model   : Auto-downloaded from Hugging Face on first run.
              --whisper-model tiny  (~39 MB)  — fastest
              --whisper-model base  (~74 MB)  — recommended accuracy/speed balance
    """

    NAME = "faster-whisper"

    def __init__(self):
        self._model = None

    def load(self, whisper_model: str = "tiny", **_) -> None:
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(whisper_model, device="cpu", compute_type="int8")
        except ImportError:
            raise ImportError("pip install faster-whisper")

    def recognize(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> RecognitionResult:
        tmp = self._write_tmp_wav(audio_bytes, sample_rate)
        try:
            t0 = time.perf_counter()
            segments, _ = self._model.transcribe(
                tmp,
                language="en",
                beam_size=1,           # beam=1 is fastest; negligible loss on 5-word vocab
                vad_filter=True,       # skip silent frames
                word_timestamps=False,
            )
            transcript = " ".join(s.text.strip() for s in segments)
            elapsed = (time.perf_counter() - t0) * 1_000
        finally:
            os.unlink(tmp)

        return RecognitionResult(
            keyword=self._extract_keyword(transcript),
            transcript=transcript,
            inference_ms=elapsed,
            rtf=elapsed / max(self._audio_ms(audio_bytes, sample_rate), 1.0),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Engine 3 — PocketSphinx
# ─────────────────────────────────────────────────────────────────────────────

class PocketSphinxEngine(EngineBase):
    """
    PocketSphinx 5.x in keyword-spotting (KWS) mode.
    No model download required — bundled en-US acoustic model is used.

    Install : pip install pocketsphinx
    Tuning  : Decrease KWS_THRESHOLD (e.g. 1e-30) to reduce false positives.
              Increase (e.g. 1e-10) to improve recall at cost of false triggers.
    """

    NAME = "pocketsphinx"
    KWS_THRESHOLD = "1e-20"

    def __init__(self):
        self._Decoder  = None
        self._kws_path: Optional[str] = None

    def load(self, **_) -> None:
        try:
            from pocketsphinx import Decoder
            self._Decoder = Decoder
        except ImportError:
            raise ImportError("pip install pocketsphinx")

        # Write the keyword list file
        content = "\n".join(f"{cmd} /{self.KWS_THRESHOLD}/" for cmd in COMMANDS)
        fd, self._kws_path = tempfile.mkstemp(suffix=".kws", text=True)
        with os.fdopen(fd, "w") as f:
            f.write(content)

    def teardown(self) -> None:
        if self._kws_path and os.path.exists(self._kws_path):
            os.unlink(self._kws_path)
            self._kws_path = None

    def recognize(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> RecognitionResult:
        decoder = self._Decoder(kws=self._kws_path, samprate=sample_rate)

        t0 = time.perf_counter()
        decoder.start_utt()
        for off in range(0, len(audio_bytes), CHUNK_SAMPLES * SAMPLE_WIDTH):
            chunk = audio_bytes[off : off + CHUNK_SAMPLES * SAMPLE_WIDTH]
            decoder.process_raw(chunk, no_search=False, full_utt=False)
        decoder.end_utt()
        elapsed = (time.perf_counter() - t0) * 1_000

        hyp = decoder.hyp()
        transcript = hyp.hypstr.lower() if hyp else ""
        return RecognitionResult(
            keyword=self._extract_keyword(transcript),
            transcript=transcript,
            inference_ms=elapsed,
            rtf=elapsed / max(self._audio_ms(audio_bytes, sample_rate), 1.0),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Engine 4 — Silero STT  (optional — requires torch)
# ─────────────────────────────────────────────────────────────────────────────

class SileroEngine(EngineBase):
    """
    Silero STT via PyTorch Hub.  Compact (~25 MB) neural CTC model.

    Install : pip install torch torchaudio
    Model   : Auto-downloaded from GitHub on first run (~25 MB, then cached).
              Pre-cache: python -c "import torch; torch.hub.load(
                  'snakers4/silero-models','silero_stt',language='en',
                  device='cpu',verbose=False)"
    Note    : First run requires internet.  All subsequent runs are offline.
    """

    NAME = "silero"

    def __init__(self):
        self._model   = None
        self._decoder = None
        self._torch   = None
        self._ta      = None

    def load(self, **_) -> None:
        try:
            import torch
            import torchaudio
            self._torch = torch
            self._ta    = torchaudio
        except ImportError:
            raise ImportError("pip install torch torchaudio")

        model, decoder, utils = self._torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_stt",
            language="en",
            device=self._torch.device("cpu"),
            verbose=False,
        )
        self._model   = model.eval()
        self._decoder = decoder
        # utils = (read_batch, split_into_batches, read_audio, prepare_model_input)
        self._prepare = utils[3]

    def recognize(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> RecognitionResult:
        import io
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
        buf.seek(0)

        t0 = time.perf_counter()
        waveform, sr = self._ta.load(buf)
        if sr != SAMPLE_RATE:
            waveform = self._ta.functional.resample(waveform, sr, SAMPLE_RATE)
        inp = self._prepare(waveform.unsqueeze(0), device=self._torch.device("cpu"))
        with self._torch.no_grad():
            out = self._model(inp)
        transcript = self._decoder(out[0].cpu())
        elapsed = (time.perf_counter() - t0) * 1_000

        return RecognitionResult(
            keyword=self._extract_keyword(transcript),
            transcript=transcript,
            inference_ms=elapsed,
            rtf=elapsed / max(self._audio_ms(audio_bytes, sample_rate), 1.0),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Engine registry
# ─────────────────────────────────────────────────────────────────────────────

ALL_ENGINES: Dict[str, type] = {
    VoskEngine.NAME:          VoskEngine,
    FasterWhisperEngine.NAME: FasterWhisperEngine,
    PocketSphinxEngine.NAME:  PocketSphinxEngine,
    SileroEngine.NAME:        SileroEngine,
}


# ─────────────────────────────────────────────────────────────────────────────
# Audio utilities
# ─────────────────────────────────────────────────────────────────────────────

def load_wav(path: Path) -> Tuple[bytes, int]:
    """
    Load a WAV file.  Returns (raw_pcm_bytes, sample_rate).
    Raises ValueError with a helpful ffmpeg command if the format is wrong.
    """
    with wave.open(str(path), "rb") as wf:
        ch  = wf.getnchannels()
        sw  = wf.getsampwidth()
        sr  = wf.getframerate()
        if ch != 1:
            raise ValueError(
                f"{path.name}: expected mono — got {ch} channels.  "
                f"Fix: ffmpeg -i \"{path}\" -ac 1 \"{path}\""
            )
        if sw != SAMPLE_WIDTH:
            raise ValueError(
                f"{path.name}: expected 16-bit PCM — got {sw * 8}-bit.  "
                f"Fix: ffmpeg -i \"{path}\" -sample_fmt s16 \"{path}\""
            )
        if sr != SAMPLE_RATE:
            raise ValueError(
                f"{path.name}: expected {SAMPLE_RATE} Hz — got {sr} Hz.  "
                f"Fix: ffmpeg -i \"{path}\" -ar {SAMPLE_RATE} \"{path}\""
            )
        return wf.readframes(wf.getnframes()), sr


def collect_test_files(audio_dir: Path) -> List[Tuple[Path, str]]:
    """
    Collect (wav_path, expected_keyword) pairs from audio_dir.
    Supports two layouts:
      • audio_dir/{keyword}/{n}.wav  (subdirectory per keyword)
      • audio_dir/{keyword}_{n}.wav  (flat with keyword prefix)
    """
    found: List[Tuple[Path, str]] = []
    for cmd in COMMANDS:
        subdir = audio_dir / cmd
        if subdir.is_dir():
            found.extend((p, cmd) for p in sorted(subdir.glob("*.wav")))
        found.extend((p, cmd) for p in sorted(audio_dir.glob(f"{cmd}_*.wav")))
    if not found:
        print(
            f"\n[WARN] No WAV files found in '{audio_dir}'.\n"
            "  Create samples with:  python benchmark_stt.py --record --audio-dir "
            f"{audio_dir}\n"
        )
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark runner
# ─────────────────────────────────────────────────────────────────────────────

def _rss_mb() -> float:
    if not _HAS_PSUTIL:
        return 0.0
    return _psutil.Process().memory_info().rss / 1_048_576


def run_engine(
    cls: type,
    test_files: List[Tuple[Path, str]],
    load_kwargs: dict,
) -> EngineReport:
    """Load one engine, process all test files, return an EngineReport."""
    engine: EngineBase = cls()
    print(f"\n{'─' * 62}")
    print(f"  [{cls.NAME}]")
    print(f"{'─' * 62}")

    # Load phase
    mb_before = _rss_mb()
    t0 = time.perf_counter()
    try:
        engine.load(**load_kwargs)
        load_ms = (time.perf_counter() - t0) * 1_000
        mem_delta = _rss_mb() - mb_before
        print(f"  Loaded  {load_ms:,.0f} ms   Δmem {mem_delta:+.1f} MB")
    except Exception as exc:  # noqa: BLE001
        load_ms = (time.perf_counter() - t0) * 1_000
        print(f"  FAILED  {exc}")
        return EngineReport(cls.NAME, load_ms, 0.0, [], error=str(exc))

    # Inference phase
    records: List[FileRecord] = []
    for wav_path, expected in test_files:
        try:
            audio, sr = load_wav(wav_path)
        except ValueError as exc:
            print(f"  skip  {wav_path.name}: {exc}")
            continue
        try:
            result = engine.recognize(audio, sr)
        except Exception as exc:  # noqa: BLE001
            print(f"  err   {wav_path.name}: {exc}")
            continue

        mark = "✓" if result.matched(expected) else "✗"
        print(
            f"  {mark}  {wav_path.parent.name}/{wav_path.name:<20s}"
            f"  exp={expected:<6s}  got={str(result.keyword):<6s}"
            f"  {result.inference_ms:6.0f} ms  RTF={result.rtf:.2f}"
        )
        records.append(FileRecord(str(wav_path), expected, result))

    engine.teardown()
    report = EngineReport(cls.NAME, load_ms, mem_delta, records)
    print(
        f"\n  → accuracy={report.accuracy_pct:.1f}%"
        f"   median={report.median_latency_ms:.0f} ms"
        f"   p95={report.p95_latency_ms:.0f} ms"
        f"   RTF={report.mean_rtf:.2f}"
        f"   {'PASS ✓' if report.meets_latency and report.meets_accuracy else 'FAIL ✗'}"
    )
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Results reporter
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(reports: List[EngineReport]) -> None:
    w = 18
    sep = "═" * 74
    print(f"\n{sep}")
    print("  BENCHMARK SUMMARY — SlideCommander Voice Engine Selection")
    print(sep)
    print(
        f"  {'ENGINE':<{w}}  {'LOAD ms':>8}  {'MEM MB':>6}  "
        f"{'ACCUR %':>7}  {'MED ms':>7}  {'P95 ms':>7}  {'RTF':>5}  PASS?"
    )
    print("─" * 74)
    for r in reports:
        if r.error:
            print(f"  {r.engine_name:<{w}}  {'ERROR — ' + r.error[:35]}")
            continue
        tag = "✓ PASS" if (r.meets_latency and r.meets_accuracy) else "✗ FAIL"
        print(
            f"  {r.engine_name:<{w}}"
            f"  {r.load_time_ms:>8.0f}"
            f"  {r.memory_delta_mb:>6.1f}"
            f"  {r.accuracy_pct:>7.1f}"
            f"  {r.median_latency_ms:>7.0f}"
            f"  {r.p95_latency_ms:>7.0f}"
            f"  {r.mean_rtf:>5.2f}"
            f"  {tag}"
        )
    print("─" * 74)
    print(f"  Targets: latency < {LATENCY_BUDGET_MS:.0f} ms  |  accuracy ≥ {ACCURACY_TARGET_PCT:.0f} %")
    print(sep)

    winners = [
        r for r in reports
        if not r.error and r.meets_latency and r.meets_accuracy
    ]
    if winners:
        best = min(winners, key=lambda r: r.median_latency_ms)
        print(
            f"\n  ► Recommended: {best.engine_name}"
            f"  (latency={best.median_latency_ms:.0f} ms,"
            f" accuracy={best.accuracy_pct:.1f} %)\n"
        )
    else:
        print(
            "\n  ► No engine met both targets on this hardware.\n"
            "    Consider: smaller Vosk model, vosk-model-small-en-us-0.15\n"
        )


def save_json(reports: List[EngineReport], path: Path) -> None:
    data = {
        "benchmark_version": "1.1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hardware": {
            "os":      platform.system() + " " + platform.release(),
            "machine": platform.machine(),
            "python":  platform.python_version(),
            "cpu":     platform.processor() or "unknown",
        },
        "targets": {
            "latency_budget_ms":  LATENCY_BUDGET_MS,
            "accuracy_target_pct": ACCURACY_TARGET_PCT,
        },
        "results": [r.to_dict() for r in reports],
    }
    # Winner field
    winners = [
        r for r in reports
        if not r.error and r.meets_latency and r.meets_accuracy
    ]
    data["recommended_engine"] = (
        min(winners, key=lambda r: r.median_latency_ms).engine_name
        if winners else None
    )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n  Results saved → {path}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Recording helper
# ─────────────────────────────────────────────────────────────────────────────

def _record_clip_sounddevice(record_seconds: float) -> bytes:
    """Record one clip using sounddevice (no C compiler needed on Windows)."""
    import sounddevice as sd
    import numpy as np
    audio = sd.rec(
        int(record_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    return audio.tobytes()


def _record_clip_pyaudio(record_seconds: float) -> bytes:
    """Record one clip using PyAudio."""
    import pyaudio
    pa = pyaudio.PyAudio()
    frames_per_clip = math.ceil(record_seconds * SAMPLE_RATE / CHUNK_SAMPLES)
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SAMPLES,
    )
    frames = [
        stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
        for _ in range(frames_per_clip)
    ]
    stream.stop_stream()
    stream.close()
    pa.terminate()
    return b"".join(frames)


def _get_record_fn(record_seconds: float):
    """Return whichever recording backend is available."""
    try:
        import pyaudio  # noqa: F401
        return lambda: _record_clip_pyaudio(record_seconds)
    except ImportError:
        pass
    try:
        import sounddevice  # noqa: F401
        return lambda: _record_clip_sounddevice(record_seconds)
    except ImportError:
        pass
    sys.exit(
        "[ERROR] No audio backend found.\n"
        "  Install one of:\n"
        "    pip install sounddevice\n"
        "    pip install pyaudio\n"
    )


def record_samples(
    audio_dir: Path,
    samples_per_command: int,
    record_seconds: float = 2.5,
) -> None:
    """
    Interactive terminal recorder.  Prompts the user to speak each command word
    and saves correctly formatted WAV files under audio_dir/{keyword}/{n:03d}.wav.
    Uses PyAudio if available, falls back to sounddevice.
    """
    record_fn = _get_record_fn(record_seconds)

    print(
        f"\n[RECORD] Capturing {samples_per_command} × {record_seconds:.1f}s"
        f" samples for {len(COMMANDS)} commands → {audio_dir}\n"
        f"         Each clip: say the word clearly, ~{record_seconds:.1f}s after the prompt.\n"
    )

    for cmd in COMMANDS:
        cmd_dir = audio_dir / cmd
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, samples_per_command + 1):
            out_path = cmd_dir / f"{i:03d}.wav"
            input(f"  [{cmd}  {i}/{samples_per_command}]  Press ENTER then say \"{cmd}\" … ")

            audio_bytes = record_fn()

            with wave.open(str(out_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_bytes)
            print(f"           Saved {out_path}")

    print(
        f"\n[RECORD] Done.  {samples_per_command * len(COMMANDS)} clips saved.\n"
        f"         Next: python benchmark_stt.py --audio-dir {audio_dir}\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Live smoke-test
# ─────────────────────────────────────────────────────────────────────────────

def run_live(engines: List[EngineBase], duration: float) -> None:
    """Record {duration}s from the mic and run each loaded engine once."""
    record_fn = _get_record_fn(duration)

    print(f"\n[LIVE] Recording {duration:.1f}s — speak a command now …")
    audio = record_fn()
    print()
    for eng in engines:
        r = eng.recognize(audio)
        print(
            f"  {eng.NAME:<20s}  keyword={str(r.keyword):<8s}"
            f"  '{r.transcript}'  {r.inference_ms:.0f} ms"
        )
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="benchmark_stt.py",
        description="SlideCommander STT engine benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── mode flags (non-exclusive so --record can coexist with --audio-dir) ──
    p.add_argument(
        "--record", action="store_true",
        help="Record test samples from the microphone into --audio-dir.",
    )
    p.add_argument(
        "--live", action="store_true",
        help="Record from mic and run each engine once (smoke-test, no files needed).",
    )
    p.add_argument(
        "--list-engines", action="store_true",
        help="Print available engine names and exit.",
    )

    # ── shared options ────────────────────────────────────────────────────────
    p.add_argument(
        "--audio-dir", metavar="DIR", type=Path, default=Path("test_audio"),
        help="Directory of test WAV files / recording destination (default: test_audio/).",
    )
    p.add_argument(
        "--output", metavar="FILE", type=Path, default=Path("results.json"),
        help="Write JSON results here (default: results.json).",
    )
    p.add_argument(
        "--engines", nargs="+", metavar="NAME", default=["all"],
        choices=list(ALL_ENGINES.keys()) + ["all"],
        help=(
            f"Engines to run.  'all' = {DEFAULT_ENGINES} + silero if torch available. "
            f"Choices: {', '.join(ALL_ENGINES)}. (default: all)"
        ),
    )
    p.add_argument(
        "--samples", type=int, default=5, metavar="N",
        help="Samples per command to record with --record (default: 5).",
    )
    p.add_argument(
        "--duration", type=float, default=3.0, metavar="SECS",
        help="Mic recording length for --live mode (default: 3).",
    )

    # ── model overrides ───────────────────────────────────────────────────────
    p.add_argument(
        "--vosk-model", metavar="PATH", default="vosk-model-en-us-0.22",
        help="Path to Vosk model directory (default: vosk-model-en-us-0.22).",
    )
    p.add_argument(
        "--whisper-model", metavar="SIZE", default="tiny",
        choices=["tiny", "base", "small"],
        help="Faster-Whisper model size — tiny/base/small (default: tiny).",
    )

    return p


def resolve_engine_classes(names: List[str]) -> List[type]:
    if "all" in names:
        return [ALL_ENGINES[n] for n in DEFAULT_ENGINES]
    return [ALL_ENGINES[n] for n in names]


def main() -> None:
    args = build_parser().parse_args()

    if args.list_engines:
        print("\nAvailable engines:\n")
        for name, cls in ALL_ENGINES.items():
            default_tag = " [default]" if name in DEFAULT_ENGINES else " [optional]"
            print(f"  {name:<20s}{default_tag}")
            doc = [l.strip() for l in (cls.__doc__ or "").splitlines() if l.strip()]
            if doc:
                print(f"  {'':20s}{doc[0]}\n")
        sys.exit(0)

    # ── record mode ───────────────────────────────────────────────────────────
    if args.record:
        record_samples(args.audio_dir, args.samples)
        sys.exit(0)

    engine_classes = resolve_engine_classes(args.engines)
    load_kwargs = {
        "vosk_model":    args.vosk_model,
        "whisper_model": args.whisper_model,
    }

    # ── live smoke-test ───────────────────────────────────────────────────────
    if args.live:
        loaded: List[EngineBase] = []
        for cls in engine_classes:
            eng = cls()
            try:
                eng.load(**load_kwargs)
                loaded.append(eng)
            except Exception as exc:  # noqa: BLE001
                print(f"  [skip] {cls.NAME}: {exc}")
        if loaded:
            run_live(loaded, args.duration)
        for e in loaded:
            e.teardown()
        sys.exit(0)

    # ── file benchmark (default) ──────────────────────────────────────────────
    test_files = collect_test_files(args.audio_dir)
    print(
        f"\n[BENCH] {len(test_files)} test files"
        f"  |  engines: {[c.NAME for c in engine_classes]}"
        f"\n        targets: latency < {LATENCY_BUDGET_MS:.0f} ms"
        f"  |  accuracy ≥ {ACCURACY_TARGET_PCT:.0f} %"
    )

    reports: List[EngineReport] = []
    for cls in engine_classes:
        reports.append(run_engine(cls, test_files, load_kwargs))

    print_summary(reports)

    if reports:
        save_json(reports, args.output)


if __name__ == "__main__":
    main()
