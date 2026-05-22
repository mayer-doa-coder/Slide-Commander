import sys
import os
from unittest.mock import MagicMock

# Ensure the project root is on sys.path so that `import voice`, `import keyboard`,
# etc. work regardless of which directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(__file__))

# ── pyautogui stub ────────────────────────────────────────────────────────────
# patch("pyautogui.press") requires the module to be importable even when the
# real package isn't installed (keyboard.py uses lazy imports at runtime).
try:
    import pyautogui
except ImportError:
    sys.modules["pyautogui"] = MagicMock()

# ── qrcode stub ───────────────────────────────────────────────────────────────
# qr_display.py imports qrcode lazily; tests need it importable so they can
# verify output. get_matrix() must return a real boolean matrix so that
# _half_block() renders ≥5 lines (satisfying test_qr_body_rendered).
try:
    import qrcode
except ImportError:
    _qrcode_mock = MagicMock()
    _qrcode_mock.constants.ERROR_CORRECT_L = 1
    _dummy_matrix = [[bool((i + j) % 2) for j in range(21)] for i in range(21)]
    _qr_instance = MagicMock()
    _qr_instance.get_matrix.return_value = _dummy_matrix
    _qrcode_mock.QRCode.return_value = _qr_instance
    sys.modules["qrcode"] = _qrcode_mock
    sys.modules["qrcode.constants"] = _qrcode_mock.constants

# ── flask stub (only when truly absent) ──────────────────────────────────────
try:
    import flask  # noqa: F401
except ImportError:
    sys.modules.setdefault("flask", MagicMock())

# ── flask_socketio stub ───────────────────────────────────────────────────────
# When absent, stub SocketIO so that @socketio.on("event") acts as a
# passthrough decorator — the original handler functions stay callable,
# which lets the WebSocket integration tests invoke them directly.
try:
    import flask_socketio  # noqa: F401
    FLASK_AVAILABLE = True
except ImportError:
    def _on_passthrough(*_args, **_kwargs):
        def _wrap(fn): return fn
        return _wrap

    _fsi_instance = MagicMock()
    _fsi_instance.on.side_effect = _on_passthrough

    _fsi_stub = MagicMock()
    _fsi_stub.SocketIO.return_value = _fsi_instance

    sys.modules["flask_socketio"] = _fsi_stub
    FLASK_AVAILABLE = False
