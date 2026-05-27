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

    def test_goto_slide_typewrite_then_enter_in_presentation_mode(self):
        """Presentation mode: goto:3 typewrite '3' + Enter — no Home/Escape."""
        with patch("keyboard._is_presentation_mode", return_value=True), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite") as mt, patch("time.sleep"):
            keyboard.execute("goto:3")
        mt.assert_called_once_with("3", interval=0.05)
        mp.assert_called_once_with("enter")
        pressed = [c.args[0] for c in mp.call_args_list]
        assert "home" not in pressed    # Home exits slide-show in browser apps
        assert "escape" not in pressed  # Escape exits slide-show mode

    def test_goto_slide_1_typewrite_in_presentation_mode(self):
        """Presentation mode: goto:1 typewrite '1' + Enter."""
        with patch("keyboard._is_presentation_mode", return_value=True), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite") as mt, patch("time.sleep"):
            keyboard.execute("goto:1")
        mt.assert_called_once_with("1", interval=0.05)
        mp.assert_called_once_with("enter")

    def test_goto_slide_home_right_in_edit_mode(self):
        """Edit mode: goto:3 presses home then right×2 — no typewrite."""
        with patch("keyboard._is_presentation_mode", return_value=False), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite") as mt, patch("time.sleep"):
            keyboard.execute("goto:3")
        pressed = [c.args[0] for c in mp.call_args_list]
        assert "home" in pressed
        assert pressed.count("right") == 2
        assert "escape" not in pressed
        mt.assert_not_called()

    def test_goto_slide_1_home_only_in_edit_mode(self):
        """Edit mode: goto:1 presses home only — zero right-arrow presses."""
        with patch("keyboard._is_presentation_mode", return_value=False), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite") as mt, patch("time.sleep"):
            keyboard.execute("goto:1")
        pressed = [c.args[0] for c in mp.call_args_list]
        assert "home" in pressed
        assert "right" not in pressed
        mt.assert_not_called()

    def test_goto_slide_out_of_range_caps_at_max_edit_slides(self):
        """Edit mode: slide N > _MAX_EDIT_SLIDES fires exactly _MAX_EDIT_SLIDES rights.

        Ensures 'slide 40' on a 20-slide deck completes quickly and correctly —
        Right-arrow stops at the last slide automatically, so the result is
        always the last slide regardless of how large N is.
        """
        big_n = keyboard._MAX_EDIT_SLIDES + 10
        with patch("keyboard._is_presentation_mode", return_value=False), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite"), patch("time.sleep"):
            keyboard.execute(f"goto:{big_n}")
        pressed = [c.args[0] for c in mp.call_args_list]
        assert pressed.count("right") == keyboard._MAX_EDIT_SLIDES

    def test_goto_slide_over_total_edit_mode_lands_on_last_slide(self):
        """Edit mode: 'slide 40' on a 20-slide deck fires right×39 (not right×40).

        The cap (slide_num - 1, not slide_num) and the natural stop-at-last-slide
        behaviour of Right-arrow guarantee the correct slide is reached.
        """
        with patch("keyboard._is_presentation_mode", return_value=False), \
             patch("pyautogui.press") as mp, patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite"), patch("time.sleep"):
            keyboard.execute("goto:40")
        pressed = [c.args[0] for c in mp.call_args_list]
        assert pressed.count("right") == 39   # slide_num - 1, capped at _MAX_EDIT_SLIDES
        assert "home" in pressed              # always starts from slide 1

    def test_open_presses_f5(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey"):
            keyboard.execute("open")
        mp.assert_called_once_with("f5")

    def test_close_presses_escape(self):
        with patch("pyautogui.press") as mp, patch("pyautogui.hotkey"):
            keyboard.execute("close")
        mp.assert_called_once_with("escape")

    @pytest.mark.parametrize("action", ["next", "back", "first", "last", "pause", "open", "close", "goto:5"])
    def test_all_valid_actions_do_not_raise(self, action):
        with patch("keyboard._is_presentation_mode", return_value=False), \
             patch("pyautogui.press"), patch("pyautogui.hotkey"), \
             patch("pyautogui.typewrite"), patch("time.sleep"):
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

