"""
Keyboard simulation module — Layer 1 of the dependency DAG.

Translates command names into OS key-press events via PyAutoGUI.
This module has no knowledge of networking, voice, or the web layer.
All slide actions from both server.py and voice.py route through here.
"""

from __future__ import annotations
import threading
_pyautogui_lock = threading.Lock()
# Command → (key, modifier) mapping.  Modifier is None when not needed.
# Google Slides (and most presentation software) uses bare Home/End in presentation mode.
# Ctrl+Home/End are text-editor shortcuts that do NOT navigate slides.
_KEY_MAP: dict[str, tuple[str, str | None]] = {
    "next":  ("right", None),
    "back":  ("left",  None),
    "first": ("home",  None),
    "last":  ("end",   None),
    "pause": ("",      None),   # pause is a timer toggle — no key sent to OS
}


def execute(action: str) -> None:
    """Press the OS key corresponding to *action*. Raises ValueError for unknown actions."""

    if isinstance(action, str) and action.startswith("goto:"):
        _, slide_number = action.split(":", 1)
        if not slide_number.isdigit():
            raise ValueError(f"Invalid goto action {action!r}. Expected numeric slide number.")

        import pyautogui
        import time
        pyautogui.FAILSAFE = False
        with _pyautogui_lock:
            time.sleep(0.2)  # Give focus time to settle
            pyautogui.typewrite(slide_number, interval=0.05)
            pyautogui.press("enter")
        return

    if action not in _KEY_MAP:
        raise ValueError(f"Unknown action {action!r}. Allowed: {', '.join(sorted(_KEY_MAP))}.")

    key, modifier = _KEY_MAP[action]

    if not key:
        return  # pause has no OS key — handled by the UI timer

    import pyautogui
    pyautogui.FAILSAFE = False
    if modifier:
        pyautogui.hotkey(modifier, key)
    else:
        pyautogui.press(key)
