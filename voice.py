"""
Voice recognition module — Layer 2 of the dependency DAG.

Captures microphone audio via sounddevice and runs keyword spotting
with faster-whisper. Calls keyboard.execute() directly on a match;
does NOT import server.py (avoids circular dependency).

An optional on_command callback injected by main.py is called after
the key press so server.py can broadcast a voice-event ack to clients.
"""

from __future__ import annotations

import queue as _queue
import re
import threading
import time
from typing import Callable, Optional

import keyboard
from config import Config

_SAMPLE_RATE = 16_000
_BLOCK_DURATION_S = 0.5
_BLOCK_SAMPLES = int(_SAMPLE_RATE * _BLOCK_DURATION_S)
_WINDOW_BLOCKS = 4          # 2-second audio window per Whisper call
_STEP_BLOCKS = 2            # slide by 1 s — inference runs every ~1 s
_COMMAND_COOLDOWN_S = 0.5   # 500 ms debounce (Algorithm 10.1)

_PUNCT_RE = re.compile(r"[^\w\s]")  # strip everything that isn't a word char or space

# Voice phrase → SlideCommander action.  Multi-word phrases checked via subset match.
_KEYWORD_MAP: dict[str, str] = {
    "next":      "next",
    "forward":   "next",
    "back":      "back",
    "previous":  "back",
    "prev":      "back",
    "start":     "first",
    "first":     "first",
    "beginning": "first",
    "end":       "last",
    "last":      "last",
    "final":     "last",
    "pause":     "pause",
    "stop":      "pause",
    "resume":    "pause",
}


def _clean(raw: str) -> str:
    """Lowercase and strip punctuation from a Whisper transcript segment."""
    return _PUNCT_RE.sub("", raw.lower()).strip()


def _dispatch(
    text: str,
    last_command_time: dict[str, float],
    on_command: Optional[Callable[[str], None]],
) -> bool:
    """
    Scan cleaned *text* for a trigger keyword, apply 500 ms debounce
    (Algorithm 10.1), then fire keyboard.execute() and *on_command*.

    Returns True if a command was dispatched, False if suppressed or not found.
    Exposed at module level so unit tests can drive it directly.
    """
    word_set = set(text.split())
    for keyword, command in _KEYWORD_MAP.items():
        if all(w in word_set for w in keyword.split()):
            now = time.time()
            # Default sentinel is (now - cooldown) so the very first call always passes.
            since = now - last_command_time.get(command, now - _COMMAND_COOLDOWN_S)
            if since < _COMMAND_COOLDOWN_S:
                print("  [VOICE] Ignored (debouncing)")
                return False
            last_command_time[command] = now
            print(f"  [VOICE] Command detected: {keyword.upper()}")
            keyboard.execute(command)
            if on_command:
                on_command(command)
            return True
    return False


def _worker(cfg: Config, on_command: Optional[Callable[[str], None]]) -> None:
    """Background thread body: load model → open mic → transcribe → dispatch."""
    import numpy as np
    import sounddevice as sd
    from faster_whisper import WhisperModel

    # ── Load Whisper model ─────────────────────────────────────────────────────
    try:
        model = WhisperModel(cfg.model_path, device="cpu", compute_type="int8")
        print(f"  [VOICE] Whisper model '{cfg.model_path}' loaded.")
    except Exception as exc:
        print(f"  [VOICE][ERROR] Failed to load Whisper model: {exc}")
        return

    # ── Audio queue filled by the sounddevice callback ─────────────────────────
    audio_q: _queue.Queue[np.ndarray] = _queue.Queue()

    def _audio_callback(
        indata: np.ndarray, frames: int, time_info, status
    ) -> None:
        if status:
            print(f"  [VOICE][WARN] {status}")
        audio_q.put(indata[:, 0].copy())  # mono: channel 0, shape (BLOCK_SAMPLES,)

    # ── Open microphone stream ─────────────────────────────────────────────────
    try:
        stream = sd.InputStream(
            samplerate=_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=_BLOCK_SAMPLES,
            callback=_audio_callback,
        )
    except Exception:
        print(
            "  [WARNING] Microphone unavailable or access denied. "
            "Voice mode disabled. Web remote remains fully functional."
        )
        return

    buffer: list[np.ndarray] = []
    last_command_time: dict[str, float] = {}

    print("  [VOICE] Listening... (say: next, back, first, last, pause)")

    try:
        with stream:
            while True:
                try:
                    block = audio_q.get(timeout=1.0)
                except _queue.Empty:
                    continue

                buffer.append(block)
                if len(buffer) < _WINDOW_BLOCKS:
                    continue

                # Concatenate the current window and slide forward by STEP_BLOCKS
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

                print(f'  [VOICE] Heard: "{text}"')
                _dispatch(text, last_command_time, on_command)
    except Exception:
        print(
            "  [WARNING] Microphone unavailable or access denied. "
            "Voice mode disabled. Web remote remains fully functional."
        )


def start_listening(
    cfg: Config,
    on_command: Optional[Callable[[str], None]] = None,
) -> threading.Thread:
    """
    Start the voice recognition loop in a daemon thread.

    *on_command* is called with the matched command string after the key is
    pressed.  Pass server.broadcast_voice_event here from main.py.
    Returns the thread so the caller can join or monitor it.
    """
    t = threading.Thread(
        target=_worker,
        args=(cfg, on_command),
        daemon=True,
        name="voice-worker",
    )
    t.start()
    return t
