"""
Keyboard simulation module — Layer 1 of the dependency DAG.

Translates command names into OS key-press events via PyAutoGUI.
This module has no knowledge of networking, voice, or the web layer.
All slide actions from both server.py and voice.py route through here.
"""

from __future__ import annotations
import threading
_pyautogui_lock = threading.Lock()
# Hard cap on Right-arrow presses in edit-mode goto so an out-of-range voice
# command (e.g. "slide 40" on a 20-slide deck) completes in milliseconds
# rather than pressing Right dozens of extra times.  Presentations rarely
# exceed 500 slides, and Right-arrow stops naturally at the last slide anyway.
_MAX_EDIT_SLIDES = 500


def _is_presentation_mode() -> bool:
    """Return True when the foreground window is fullscreen (presentation heuristic).

    Uses Windows ctypes with a 1-px tolerance to handle taskbar-less fullscreen.
    Falls back to False on non-Windows platforms or if detection raises.
    """
    try:
        import ctypes
        import ctypes.wintypes
        user32 = ctypes.windll.user32          # AttributeError on non-Windows — caught below
        hwnd = user32.GetForegroundWindow()
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        sw = user32.GetSystemMetrics(0)        # SM_CXSCREEN
        sh = user32.GetSystemMetrics(1)        # SM_CYSCREEN
        return rect.left <= 1 and rect.top <= 1 and rect.right >= sw - 1 and rect.bottom >= sh - 1
    except Exception:
        return False


# Command → (key, modifier) mapping.  Modifier is None when not needed.
_KEY_MAP: dict[str, tuple[str, str | None]] = {
    "next":  ("right",  None),
    "back":  ("left",   None),
    "first": ("home",   None),
    "last":  ("end",    None),
    "pause": ("",       None),   # pause is a timer toggle — no key sent to OS
    "open":  ("f5",     None),   # enter slide-show mode (F5 = start presentation)
    "close": ("escape", None),   # exit slide-show mode
}


def execute(action: str) -> None:
    """Press the OS key corresponding to *action*. Raises ValueError for unknown actions."""

    if isinstance(action, str) and action.startswith("goto:"):
        _, slide_number = action.split(":", 1)
        if not slide_number.isdigit():
            raise ValueError(f"Invalid goto action {action!r}. Expected numeric slide number.")

        import pyautogui
        import time
        slide_num = int(slide_number)
        pyautogui.PAUSE = 0         # disable pyautogui's default 0.1 s per-call pause
        pyautogui.FAILSAFE = False
        with _pyautogui_lock:
            if _is_presentation_mode():
                # Slide-show: type number + Enter.  Works in PowerPoint and Google
                # Slides; the app clamps silently to the last slide when N > total.
                pyautogui.typewrite(str(slide_num), interval=0.05)
                time.sleep(0.1)
                pyautogui.press("enter")
            else:
                # Edit mode: Home then Right × (N−1), capped at _MAX_EDIT_SLIDES.
                # The cap means "slide 40" on a 20-slide deck fires only 39 rapid
                # presses and completes in <100 ms — Right stops at the last slide
                # automatically, so the result is correct regardless of total slides.
                pyautogui.press("home")
                time.sleep(0.05)    # brief settle so the app registers Home first
                for _ in range(min(slide_num - 1, _MAX_EDIT_SLIDES)):
                    pyautogui.press("right")
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
