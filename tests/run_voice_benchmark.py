"""
ST-06 Voice Accuracy Benchmark
================================
Drives the production faster-whisper + sounddevice pipeline through
100 live utterances (20 per keyword) and prints a pass/fail matrix.

Usage:
    python tests/run_voice_benchmark.py [--model tiny]

Run from the project root so that voice.py is importable.
"""

from __future__ import annotations

import argparse
import os
import queue
import sys
import time
from unittest.mock import patch

# Ensure the project root is on sys.path regardless of CWD.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from voice import (
    _BLOCK_SAMPLES,
    _SAMPLE_RATE,
    _STEP_BLOCKS,
    _WINDOW_BLOCKS,
    _clean,
    _dispatch,
)

# ── Constants ────────────────────────────────────────────────────────────────

# (display_keyword, expected_command_from_voice._KEYWORD_MAP)
TARGETS: list[tuple[str, str]] = [
    ("next",  "next"),
    ("back",  "back"),
    ("start", "first"),
    ("end",   "last"),
    ("pause", "pause"),
]

UTTERANCES_PER_KEYWORD = 20
LISTEN_TIMEOUT_S = 8.0          # seconds before a no-match is counted as FAIL
PASS_THRESHOLD    = 19           # ≥19/20 → ≥95 %


# ── Single-utterance capture ──────────────────────────────────────────────────

def listen_once(model: WhisperModel, timeout: float = LISTEN_TIMEOUT_S) -> str | None:
    """
    Open the microphone, run the same sliding-window Whisper loop used in
    production, and return the first dispatched command string (e.g. "next")
    or None if nothing is recognised within *timeout* seconds.

    keyboard.execute() is patched so no actual key presses occur.
    """
    audio_q: queue.Queue[np.ndarray] = queue.Queue()

    def _audio_cb(indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            print(f"  [WARN] {status}")
        audio_q.put(indata[:, 0].copy())

    detected: list[str | None] = [None]
    last_cmd_time: dict[str, float] = {}

    def _on_command(cmd: str) -> None:
        detected[0] = cmd

    buffer: list[np.ndarray] = []
    deadline = time.monotonic() + timeout

    try:
        stream = sd.InputStream(
            samplerate=_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=_BLOCK_SAMPLES,
            callback=_audio_cb,
        )
    except Exception as exc:
        print(f"  [ERROR] Cannot open microphone: {exc}")
        sys.exit(1)

    with stream, patch("voice.keyboard.execute"):
        while time.monotonic() < deadline and detected[0] is None:
            try:
                block = audio_q.get(timeout=0.5)
            except queue.Empty:
                continue

            buffer.append(block)
            if len(buffer) < _WINDOW_BLOCKS:
                continue

            audio = np.concatenate(buffer[:_WINDOW_BLOCKS])
            buffer = buffer[_STEP_BLOCKS:]

            segments, _ = model.transcribe(
                audio,
                language="en",
                beam_size=1,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 300},
            )
            text = _clean(" ".join(seg.text for seg in segments))
            if not text:
                continue

            print(f"  [Heard]: \"{text}\"")
            _dispatch(text, last_cmd_time, _on_command)

    return detected[0]


# ── Results table ─────────────────────────────────────────────────────────────

def _print_table(results: dict[str, dict[str, int]]) -> bool:
    """Print ASCII results matrix. Returns True if all keywords pass."""
    sep   = "+" + "-" * 12 + "+" + "-" * 10 + "+" + "-" * 10 + "+" + "-" * 8 + "+"
    hdr   = f"| {'Keyword':<10} | {'Correct':<8} | {'Rate':>7}  | {'Status':<6} |"

    print("\n" + sep)
    print(hdr)
    print(sep)

    all_pass = True
    for keyword, _expected in TARGETS:
        p = results[keyword]["pass"]
        rate = p / UTTERANCES_PER_KEYWORD * 100
        status = "PASS" if p >= PASS_THRESHOLD else "FAIL ✗"
        if p < PASS_THRESHOLD:
            all_pass = False
        print(f"| {keyword:<10} | {p:>2}/{UTTERANCES_PER_KEYWORD:<5}  | {rate:>6.1f} %  | {status:<6} |")

    print(sep)
    overall = sum(r["pass"] for r in results.values())
    overall_rate = overall / (len(TARGETS) * UTTERANCES_PER_KEYWORD) * 100
    verdict = "ALL PASS — ST-06 SATISFIED" if all_pass else "SOME KEYWORDS BELOW 95 % — ST-06 NOT YET SATISFIED"
    print(f"  Total: {overall}/{len(TARGETS) * UTTERANCES_PER_KEYWORD}  ({overall_rate:.1f} %)")
    print(f"  Verdict: {verdict}\n")
    return all_pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="ST-06 voice accuracy benchmark")
    parser.add_argument("--model", default="tiny",
                        help="faster-whisper model size (default: tiny)")
    args = parser.parse_args()

    print("\n====================================================")
    print("  SlideCommander  ST-06  Voice Accuracy Benchmark  ")
    print("====================================================")
    print(f"  Model      : {args.model}")
    print(f"  Keywords   : {', '.join(kw for kw, _ in TARGETS)}")
    print(f"  Utterances : {UTTERANCES_PER_KEYWORD} per keyword  ({UTTERANCES_PER_KEYWORD * len(TARGETS)} total)")
    print(f"  Timeout    : {LISTEN_TIMEOUT_S} s per attempt")
    print(f"  Threshold  : ≥{PASS_THRESHOLD}/{UTTERANCES_PER_KEYWORD} correct per keyword\n")
    print("  Loading Whisper model…", flush=True)

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("  Model loaded.  Quiet your surroundings and follow the prompts.\n")

    results: dict[str, dict[str, int]] = {
        kw: {"pass": 0, "fail": 0} for kw, _ in TARGETS
    }

    for keyword, expected_cmd in TARGETS:
        print(f"\n{'─' * 50}")
        print(f"  Keyword: {keyword.upper()}  (maps to command: {expected_cmd!r})")
        print(f"{'─' * 50}")

        for attempt in range(1, UTTERANCES_PER_KEYWORD + 1):
            print(f"\n  [Target: {keyword.upper()}] (Attempt {attempt}/{UTTERANCES_PER_KEYWORD})  ->  Speak now…")
            cmd = listen_once(model)

            if cmd == expected_cmd:
                results[keyword]["pass"] += 1
                print("  -> PASS")
            else:
                results[keyword]["fail"] += 1
                reason = f"got '{cmd}'" if cmd is not None else "timeout / no match"
                print(f"  -> FAIL  ({reason})")

    _print_table(results)


if __name__ == "__main__":
    main()
