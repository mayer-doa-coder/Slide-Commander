"""
Keyboard simulation module — Layer 1 of the dependency DAG.

Translates command names into OS key-press events via PyAutoGUI.
This module has no knowledge of networking, voice, or the web layer.
All slide actions from both server.py and voice.py route through here.
"""

from __future__ import annotations

import platform

import pyautogui

# Disable the PyAutoGUI fail-safe corner (can be re-enabled via config in future)
pyautogui.FAILSAFE = False

# macOS uses the Command key for first/last slide; Windows and Linux use Ctrl.
_MODIFIER = "command" if platform.system() == "Darwin" else "ctrl"

# Command → (key, modifier) mapping.  Modifier is None when not needed.
_KEY_MAP: dict[str, tuple[str, str | None]] = {
    "next":  ("right", None),
    "back":  ("left",  None),
    "first": ("home",  _MODIFIER),
    "last":  ("end",   _MODIFIER),
    "pause": ("",      None),   # pause is a timer toggle — no key sent to OS
}


def execute(action: str) -> None:
    """Press the OS key corresponding to *action*. Raises ValueError for unknown actions."""
    if action not in _KEY_MAP:
        raise ValueError(f"Unknown action {action!r}. Allowed: {', '.join(sorted(_KEY_MAP))}.")

    key, modifier = _KEY_MAP[action]

    if not key:
        return  # pause has no OS key — handled by the UI timer

    if modifier:
        pyautogui.hotkey(modifier, key)
    else:
        pyautogui.press(key)
