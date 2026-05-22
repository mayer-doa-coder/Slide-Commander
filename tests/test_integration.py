"""
Integration tests — Phase 4.2.

IT-01 through IT-06: prove the two primary control pipelines are correctly
wired end-to-end without touching real hardware.

  Pipeline A: WebSocket command → keyboard callback → pyautogui
  Pipeline B: voice._dispatch()  → keyboard.execute() → pyautogui

All pyautogui calls are intercepted via the conftest.py stub so no ghost
keystrokes are sent to the host machine.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import server
import voice
import keyboard


# ── Fixture: direct handler testing (no flask_socketio test_client needed) ───
#
# handle_command() uses no request context after PIN removal, so we call it
# directly and capture what it emits by patching server.emit.

@pytest.fixture
def ws_env(monkeypatch):
    """
    Inject a mock keyboard callback and capture server.emit output.
    No network stack required — tests the handler logic directly.
    """
    mock_cb = MagicMock()
    emitted: list[dict] = []

    def _capture(event: str, payload: dict) -> None:
        emitted.append({"name": event, "args": [payload]})

    server._keyboard_callback = mock_cb
    monkeypatch.setattr(server, "emit", _capture)
    yield mock_cb, emitted
    server._keyboard_callback = None


# ── Pipeline A: WebSocket handler → keyboard callback ────────────────────────

class TestWebSocketIntegration:
    def test_it01_next_command_invokes_callback(self, ws_env):
        """IT-01: command(next) → keyboard_callback called with 'next'."""
        mock_cb, _ = ws_env
        server.handle_command({"action": "next", "source": "button"})
        mock_cb.assert_called_once_with("next")

    def test_it02_command_returns_ack(self, ws_env):
        """IT-02: valid command always emits an ack event."""
        _, emitted = ws_env
        server.handle_command({"action": "back", "source": "button"})
        assert any(e["name"] == "ack" for e in emitted)

    def test_it03_ack_echoes_action(self, ws_env):
        """IT-03: ack payload contains the original action string."""
        _, emitted = ws_env
        server.handle_command({"action": "first", "source": "button"})
        acks = [e for e in emitted if e["name"] == "ack"]
        assert acks
        assert acks[0]["args"][0]["action"] == "first"

    def test_it04_unknown_action_returns_error(self, ws_env):
        """IT-04: unknown action emits error event, callback never called."""
        mock_cb, emitted = ws_env
        server.handle_command({"action": "fly", "source": "button"})
        assert any(e["name"] == "error" for e in emitted)
        mock_cb.assert_not_called()

    def test_it05_all_valid_actions_invoke_callback(self, ws_env):
        """IT-05: every allowed action reaches the keyboard callback."""
        mock_cb, _ = ws_env
        for action in ("next", "back", "first", "last", "pause"):
            server.handle_command({"action": action, "source": "button"})
        assert mock_cb.call_count == 5
        dispatched = [c.args[0] for c in mock_cb.call_args_list]
        assert set(dispatched) == {"next", "back", "first", "last", "pause"}


# ── Pipeline B: voice._dispatch → keyboard.execute → pyautogui ───────────────

class TestVoiceIntegration:
    def test_it06_dispatch_back_calls_keyboard_execute(self):
        """IT-06: voice text 'back' → keyboard.execute('back') called."""
        with patch.object(keyboard, "execute") as mock_exec:
            result = voice._dispatch("back", {}, None)
        assert result is True
        mock_exec.assert_called_once_with("back")

    def test_it07_dispatch_next_calls_keyboard_execute(self):
        """IT-07: voice text 'next' → keyboard.execute('next') called."""
        with patch.object(keyboard, "execute") as mock_exec:
            result = voice._dispatch("next", {}, None)
        assert result is True
        mock_exec.assert_called_once_with("next")

    def test_it08_dispatch_triggers_on_command_callback(self):
        """IT-08: on_command callback receives the matched action string."""
        on_cmd = MagicMock()
        with patch.object(keyboard, "execute"):
            voice._dispatch("last", {}, on_cmd)
        on_cmd.assert_called_once_with("last")

    def test_it09_dispatch_no_match_returns_false(self):
        """IT-09: unrecognised text returns False and fires nothing."""
        on_cmd = MagicMock()
        with patch.object(keyboard, "execute") as mock_exec:
            result = voice._dispatch("hello world", {}, on_cmd)
        assert result is False
        mock_exec.assert_not_called()
        on_cmd.assert_not_called()

    def test_it10_full_pipeline_back_presses_left_arrow(self):
        """IT-10: full path — voice 'back' reaches pyautogui.press('left')."""
        import pyautogui
        pyautogui.press = MagicMock()
        pyautogui.hotkey = MagicMock()
        try:
            voice._dispatch("back", {}, None)
            pyautogui.press.assert_called_once_with("left")
        finally:
            pyautogui.press = MagicMock()
            pyautogui.hotkey = MagicMock()

    def test_it11_full_pipeline_next_presses_right_arrow(self):
        """IT-11: full path — voice 'next' reaches pyautogui.press('right')."""
        import pyautogui
        pyautogui.press = MagicMock()
        pyautogui.hotkey = MagicMock()
        try:
            voice._dispatch("next", {}, None)
            pyautogui.press.assert_called_once_with("right")
        finally:
            pyautogui.press = MagicMock()
            pyautogui.hotkey = MagicMock()
