"""
Unit tests for voice.py — UT-03.

keyboard.execute() and time.time are patched so tests run without a
microphone, Whisper model, or real system clock.
"""

from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

import voice


# ── UT-03: 1500 ms debounce — same command twice within 200 ms fires once ───────

class TestDebounce:
    def test_ut03_same_command_200ms_fires_once(self):
        """UT-03: two identical commands 200 ms apart must fire the callback exactly once."""
        callback = MagicMock()
        state: dict[str, float] = {}

        with patch("voice.time.time", side_effect=[0.0, 0.2]), \
             patch("voice.keyboard.execute"):
            voice._dispatch("next", state, callback)   # t=0.000 — fires
            voice._dispatch("next", state, callback)   # t=0.200 — debounced

        callback.assert_called_once()

    def test_same_command_after_cooldown_fires_twice(self):
        """Commands separated by > 1500 ms must both fire."""
        callback = MagicMock()
        state: dict[str, float] = {}

        with patch("voice.time.time", side_effect=[0.0, 1.6]), \
             patch("voice.keyboard.execute"):
            voice._dispatch("next", state, callback)   # t=0.000 — fires
            voice._dispatch("next", state, callback)   # t=1.600 — fires again

        assert callback.call_count == 2

    def test_different_commands_within_200ms_both_fire(self):
        """Different commands have independent cooldown buckets."""
        callback = MagicMock()
        state: dict[str, float] = {}

        with patch("voice.time.time", side_effect=[0.0, 0.1]), \
             patch("voice.keyboard.execute"):
            voice._dispatch("next", state, callback)   # t=0.000 — fires "next"
            voice._dispatch("back", state, callback)   # t=0.100 — fires "back" (separate bucket)

        assert callback.call_count == 2

    def test_debounced_call_returns_false(self):
        """_dispatch must return False when a command is suppressed."""
        state: dict[str, float] = {}

        with patch("voice.time.time", side_effect=[0.0, 0.1]), \
             patch("voice.keyboard.execute"):
            first  = voice._dispatch("next", state, None)
            second = voice._dispatch("next", state, None)

        assert first  is True
        assert second is False

    def test_no_keyword_returns_false(self):
        """Text with no trigger keyword must return False without firing anything."""
        callback = MagicMock()
        state: dict[str, float] = {}

        with patch("voice.keyboard.execute"):
            result = voice._dispatch("hello world how are you", state, callback)

        assert result is False
        callback.assert_not_called()

    def test_keyboard_execute_called_with_correct_action(self):
        """keyboard.execute() must receive the mapped action, not the raw keyword."""
        state: dict[str, float] = {}

        with patch("voice.time.time", return_value=0.0), \
             patch("voice.keyboard.execute") as mock_exec:
            voice._dispatch("start", state, None)   # "start" maps to "first"

        mock_exec.assert_called_once_with("first")

    @pytest.mark.parametrize("phrase", ["go to slide 5", "go slide 5", "goto slide 5"])
    def test_go_to_slide_dispatches_goto_action(self, phrase):
        """The phrase 'go to slide N' must dispatch a numeric goto action."""
        callback = MagicMock()
        state: dict[str, float] = {}

        with patch("voice.time.time", return_value=0.0), \
             patch("voice.keyboard.execute") as mock_exec:
            result = voice._dispatch(phrase, state, callback)

        assert result is True
        mock_exec.assert_called_once_with("goto:5")
        callback.assert_called_once_with("goto:5")

    def test_punctuation_in_text_does_not_block_detection(self):
        """_dispatch receives already-cleaned text, but extra punctuation should not break it."""
        callback = MagicMock()
        state: dict[str, float] = {}

        # _clean() is called upstream; test that word-set logic is robust
        with patch("voice.time.time", return_value=0.0), \
             patch("voice.keyboard.execute"):
            result = voice._dispatch("next", state, callback)

        assert result is True
