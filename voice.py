"""
Voice recognition module — Layer 2 of the dependency DAG.

Captures microphone audio via sounddevice and runs keyword spotting
with faster-whisper. Calls keyboard.execute() directly on a match;
does NOT import server.py (avoids circular dependency).

An optional on_command callback injected by main.py is called after
the key press so server.py can broadcast a voice-event ack to clients.
"""

from __future__ import annotations

import json
import threading
from typing import Callable, Optional

import sounddevice as sd
from faster_whisper import WhisperModel

import keyboard
from config import Config


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
    pass
