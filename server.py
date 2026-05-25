8
"""
Flask + Flask-SocketIO server module — Layer 2 of the dependency DAG.

Serves static/index.html and handles WebSocket events from the phone
browser. Routes validated commands to keyboard.execute(). Does NOT
import voice.py (avoids circular dependency).

WebSocket protocol: docs/ws_protocol.md
"""

from __future__ import annotations

import socket
import time
from typing import Callable, Optional

from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit

import keyboard
from config import Config

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "slidecommander-dev"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

ALLOWED_ACTIONS: frozenset[str] = frozenset({"next", "back", "first", "last", "pause"})

# Module-level config set by start_server() before socketio.run()
_config: Optional[Config] = None
# Callback injected by main.py — called after a voice command fires
_keyboard_callback: Optional[Callable[[str], None]] = None


def get_local_ip() -> str:
    """
    Return the machine's LAN IP address (never 127.0.0.1).

    Uses a UDP connect trick from Algorithm 10.3 in SlideCommander_Project_Plan.md:
    connecting a datagram socket to an external address forces the OS to select
    the correct outbound interface — no packet is actually sent.
    Falls back to 127.0.0.1 if no network is available.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _now_ms() -> int:
    return int(time.time() * 1000)


# ── HTTP routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ── WebSocket event handlers ──────────────────────────────────────────────────

@socketio.on("connect")
def handle_connect():
    print(f"  [WS] client connected    sid={request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"  [WS] client disconnected sid={request.sid}")


@socketio.on("command")
def handle_command(data: dict):
    """
    Client → Server.  Schema: docs/ws_protocol.md §1.
    Validates action, calls keyboard callback, emits ack.
    """
    action = data.get("action", "")
    source = data.get("source", "button")
    client_ts = data.get("ts")

    if action not in ALLOWED_ACTIONS:
        emit("error", {
            "code":    "unknown_action",
            "message": f"Unknown action {action!r}. Allowed: {', '.join(sorted(ALLOWED_ACTIONS))}.",
            "ts":      _now_ms(),
            "action":  action,
        })
        return

    if _keyboard_callback:
        _keyboard_callback(action)

    server_ts = _now_ms()
    ack_payload: dict = {"action": action, "source": source, "ts": server_ts}
    if client_ts is not None:
        ack_payload["latency_ms"] = server_ts - int(client_ts)

    emit("ack", ack_payload)
    print(f"  [CMD] {action:<6s}  source={source}  ts={server_ts}")


# ── Public API ────────────────────────────────────────────────────────────────

def broadcast_voice_event(action: str) -> None:
    """
    Broadcast a voice-triggered ack to ALL connected clients.
    Called via callback from main.py after voice.py detects a keyword.
    """
    socketio.emit("ack", {
        "action": action,
        "source": "voice",
        "ts":     _now_ms(),
    })
    print(f"  [VOICE] broadcast {action}")6
    6

6


def start_server(cfg: Config, keyboard_callback: Optional[Callable[[str], None]] = None) -> None:
    """
    Initialise module state and start the Flask-SocketIO server.
    Binds to 0.0.0.0 so LAN clients (phones) can reach it.
    This call blocks until the server is stopped (Ctrl+C).
    """
    global _config, _keyboard_callback
    _config = cfg
    _keyboard_callback = keyboard_callback

    local_ip = get_local_ip()
    print(f"  [SERVER] LAN IP detected: {local_ip}")
    print(f"  [SERVER] listening on 0.0.0.0:{cfg.port}")
    socketio.run(
        app,
        host="0.0.0.0",
        port=cfg.port,
        use_reloader=False,
        log_output=False,
    )
