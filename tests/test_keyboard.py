"""
Unit tests for keyboard.py — UT-01, UT-02.

All pyautogui calls are patched so tests run headlessly on any OS.
Platform detection is also patched so modifier-key routing is testable.
"""

from __future__ import annotations

import platform
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

    def test_first_uses_hotkey_with_modifier(self):
        with patch("pyautogui.hotkey") as mh, patch("pyautogui.press"):
            keyboard.execute("first")
            # modifier is platform-dependent; just check the key argument
            assert mh.call_count == 1
            args = mh.call_args[0]
            assert args[-1] == "home"

    def test_last_uses_hotkey_with_modifier(self):
        with patch("pyautogui.hotkey") as mh, patch("pyautogui.press"):
            keyboard.execute("last")
            assert mh.call_count == 1
            args = mh.call_args[0]
            assert args[-1] == "end"

    def test_pause_sends_no_key(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey") as mh:
            keyboard.execute("pause")
            mp.assert_not_called()
            mh.assert_not_called()

    @pytest.mark.parametrize("action", ["next", "back", "first", "last", "pause"])
    def test_all_valid_actions_do_not_raise(self, action):
        with patch("pyautogui.press"), patch("pyautogui.hotkey"):
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


# ── Platform modifier routing ─────────────────────────────────────────────────

class TestPlatformModifier:
    def test_macos_uses_command(self):
        with patch("platform.system", return_value="Darwin"):
            import importlib
            import keyboard as kb_mod
            importlib.reload(kb_mod)
            assert kb_mod._MODIFIER == "command"

    def test_windows_uses_ctrl(self):
        with patch("platform.system", return_value="Windows"):
            import importlib
            import keyboard as kb_mod
            importlib.reload(kb_mod)
            assert kb_mod._MODIFIER == "ctrl"

    def test_linux_uses_ctrl(self):
        with patch("platform.system", return_value="Linux"):
            import importlib
            import keyboard as kb_mod
            importlib.reload(kb_mod)
            assert kb_mod._MODIFIER == "ctrl"

    def test_first_on_macos_sends_command_home(self):
        with patch("platform.system", return_value="Darwin"):
            import importlib
            import keyboard as kb_mod
            importlib.reload(kb_mod)
            with patch("pyautogui.hotkey") as mh, patch("pyautogui.press"):
                kb_mod.execute("first")
                mh.assert_called_once_with("command", "home")

    def test_last_on_windows_sends_ctrl_end(self):
        with patch("platform.system", return_value="Windows"):
            import importlib
            import keyboard as kb_mod
            importlib.reload(kb_mod)
            with patch("pyautogui.hotkey") as mh, patch("pyautogui.press"):
                kb_mod.execute("last")
                mh.assert_called_once_with("ctrl", "end")
