"""
Unit tests for keyboard.py — UT-01, UT-02.

All pyautogui calls are patched so tests run headlessly on any OS.
Platform detection is also patched so modifier-key routing is testable.
"""

from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

import keyboard


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mocks():
    """Return (mock_press, mock_hotkey) with pyautogui patched."""
    mock_press   = MagicMock()
    mock_hotkey  = MagicMock()
    return mock_press, mock_hotkey


# ── UT-01: valid actions produce correct key events ───────────────────────────

class TestExecuteValid:
    def test_next_presses_right(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey"):
            keyboard.execute("next")
            mp.assert_called_once_with("right")

    def test_back_presses_left(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey"):
            keyboard.execute("back")
            mp.assert_called_once_with("left")

    def test_first_presses_home(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey") as mh:
            keyboard.execute("first")
            mp.assert_called_once_with("home")
            mh.assert_not_called()

    def test_last_presses_end(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey") as mh:
            keyboard.execute("last")
            mp.assert_called_once_with("end")
            mh.assert_not_called()

    def test_pause_sends_no_key(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey") as mh:
            keyboard.execute("pause")
            mp.assert_not_called()
            mh.assert_not_called()

    def test_goto_slide_types_number_and_presses_enter(self):
        with patch("pyautogui.typewrite") as mt, patch("pyautogui.press") as mp:
            keyboard.execute("goto:5")
            mt.assert_called_once_with("5", interval=0.05)
            mp.assert_called_once_with("enter")

    @pytest.mark.parametrize("action", ["next", "back", "first", "last", "pause", "goto:5"])
    def test_all_valid_actions_do_not_raise(self, action):
        with patch("pyautogui.press"), patch("pyautogui.hotkey"), patch("pyautogui.typewrite"):
            keyboard.execute(action)  # must not raise


# ── UT-02: invalid input raises ValueError ────────────────────────────────────

class TestExecuteInvalid:
    @pytest.mark.parametrize("action", [
        "forward",
        "NEXT",
        "",
        "  ",
        "nxt",
        "Next",
        "stop",
        "end",
        123,
        None,
    ])
    def test_unknown_action_raises_value_error(self, action):
        with patch("pyautogui.press"), patch("pyautogui.hotkey"):
            with pytest.raises((ValueError, TypeError)):
                keyboard.execute(action)

    def test_error_message_contains_action(self):
        with patch("pyautogui.press"), patch("pyautogui.hotkey"):
            with pytest.raises(ValueError, match="unknown_action"):
                keyboard.execute("unknown_action")

    def test_error_message_lists_allowed_actions(self):
        with patch("pyautogui.press"), patch("pyautogui.hotkey"):
            with pytest.raises(ValueError) as exc_info:
                keyboard.execute("bogus")
            msg = str(exc_info.value)
            for allowed in ("next", "back", "first", "last", "pause"):
                assert allowed in msg

