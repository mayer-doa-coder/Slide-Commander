#!/usr/bin/env python3
"""
benchmark_websocket.py — Flask-SocketIO Round-Trip Latency Benchmark  (Task 1.3)

Measures WebSocket round-trip latency to confirm ≤ 100 ms on a local network.

Modes
-----
  localhost  (default)
    Spins up a Flask-SocketIO server in a background thread on 127.0.0.1 and
    connects a Python SocketIO client from the same process.  No phone or
    second device needed.  Validates the stack and gives a lower-bound figure.

  server
    Starts the Flask-SocketIO server on the LAN interface.  Open
    http://<your-ip>:<port>/ping in a mobile browser, or run this script in
    --client mode from a second device on the same Wi-Fi.

  client
    Connects to an existing server (--server mode on another machine) and runs
    the full latency measurement from that endpoint.

Usage
-----
  pip install flask flask-socketio simple-websocket

  # Localhost benchmark (no phone required)
  python benchmark_websocket.py

  # LAN — step 1: start server on presenter's machine
  python benchmark_websocket.py --server --port 5001

  # LAN — step 2: run client on a second machine / phone (via Termux)
  python benchmark_websocket.py --client --host 192.168.1.100 --port 5001

Acceptance criteria (Task 1.3):
  Measured round-trip latency ≤ 100 ms confirmed and logged.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional

PING_COUNT = 100
WARMUP_PINGS = 5

# ─────────────────────────────────────────────────────────────────────────────
# Server
# ─────────────────────────────────────────────────────────────────────────────

def build_app(host_ip: str, port: int):
    """Create and return the Flask-SocketIO app."""
    try:
        from flask import Flask
        from flask_socketio import SocketIO, emit
    except ImportError:
        sys.exit(
            "[ERROR] Dependencies missing.  Run:\n"
            "  pip install flask flask-socketio simple-websocket"
        )

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sc-benchmark"
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    @app.route("/")
    def index():
        return (
            "<!DOCTYPE html><html><body>"
            "<h2>SlideCommander WebSocket Latency Test</h2>"
            "<p>Server running.  Use the Python client or the browser console:</p>"
            "<pre>"
            "const s = io();\n"
            "let t0;\n"
            "s.on('pong_ack', () => console.log('RTT:', Date.now() - t0, 'ms'));\n"
            "s.on('connect', () => { t0 = Date.now(); s.emit('ping_req', {t: t0}); });"
            "</pre>"
            "</body></html>"
        )

    @socketio.on("ping_req")
    def handle_ping(data):
        emit("pong_ack", {"t": data.get("t"), "server_ts": time.time()})

    return app, socketio


def start_server_thread(host: str, port: int):
    """Start Flask-SocketIO in a daemon thread; return (app, socketio)."""
    app, socketio = build_app(host, port)
    t = threading.Thread(
        target=lambda: socketio.run(app, host=host, port=port, log_output=False),
        daemon=True,
    )
    t.start()
    time.sleep(1.0)  # let the server bind
    return app, socketio


# ─────────────────────────────────────────────────────────────────────────────
# Client benchmark
# ─────────────────────────────────────────────────────────────────────────────

def run_client_benchmark(
    host: str,
    port: int,
    n_pings: int = PING_COUNT,
    warmup: int = WARMUP_PINGS,
) -> List[float]:
    """Connect a SocketIO client, fire n_pings, return list of RTTs (ms)."""
    try:
        import socketio as sio_lib
    except ImportError:
        sys.exit(
            "[ERROR] python-socketio client missing.  Run:\n"
            "  pip install 'python-socketio[client]'"
        )

    sio = sio_lib.SimpleClient()
    url = f"http://{host}:{port}"
    print(f"  Connecting to {url} …", end=" ", flush=True)
    sio.connect(url)
    print("connected.")

    rtts: List[float] = []
    total = warmup + n_pings

    for i in range(total):
        t0 = time.perf_counter()
        sio.emit("ping_req", {"t": t0})
        sio.receive()  # blocks until pong_ack arrives
        elapsed_ms = (time.perf_counter() - t0) * 1_000
        if i >= warmup:             # discard warm-up pings
            rtts.append(elapsed_ms)
        if i < warmup:
            print(f"  [warm-up {i + 1}/{warmup}]  {elapsed_ms:.1f} ms")
        elif (i - warmup + 1) % 10 == 0:
            print(f"  [{i - warmup + 1:>3d}/{n_pings}]  last={elapsed_ms:.1f} ms")

    sio.disconnect()
    return rtts


# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────

def _pct(data: List[float], p: float) -> float:
    idx = min(int(len(data) * p / 100), len(data) - 1)
    return sorted(data)[idx]


def print_report(rtts: List[float], mode: str) -> dict:
    med   = statistics.median(rtts)
    mean  = statistics.mean(rtts)
    p95   = _pct(rtts, 95)
    p99   = _pct(rtts, 99)
    worst = max(rtts)
    best  = min(rtts)
    pass_ = med <= 100.0

    sep = "═" * 56
    print(f"\n{sep}")
    print(f"  Flask-SocketIO Latency — {mode}")
    print(sep)
    print(f"  Pings      : {len(rtts)}")
    print(f"  Min        : {best:.1f} ms")
    print(f"  Median     : {med:.1f} ms   {'✓ PASS (≤ 100 ms)' if pass_ else '✗ FAIL (> 100 ms)'}")
    print(f"  Mean       : {mean:.1f} ms")
    print(f"  P95        : {p95:.1f} ms")
    print(f"  P99        : {p99:.1f} ms")
    print(f"  Max        : {worst:.1f} ms")
    print(sep)
    print(
        "\n  Copy these values into research_log.md §4.2\n"
        "  (Table: Mode / Median RTT / P95 / P99 / ≤ 100 ms?)\n"
    )
    return {
        "mode":       mode,
        "ping_count": len(rtts),
        "min_ms":     round(best,  1),
        "median_ms":  round(med,   1),
        "mean_ms":    round(mean,  1),
        "p95_ms":     round(p95,   1),
        "p99_ms":     round(p99,   1),
        "max_ms":     round(worst, 1),
        "meets_target": pass_,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def get_lan_ip() -> str:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="benchmark_websocket.py",
        description="Flask-SocketIO round-trip latency benchmark (Task 1.3)",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--server", action="store_true",
        help="Start LAN server and wait (do NOT run client — use a second device).",
    )
    mode.add_argument(
        "--client", action="store_true",
        help="Connect to an existing server started with --server.",
    )
    p.add_argument("--host", default="", metavar="IP",
                   help="Server host for --client mode (e.g. 192.168.1.100).")
    p.add_argument("--port", type=int, default=5001, metavar="PORT",
                   help="Port (default: 5001).")
    p.add_argument("--pings", type=int, default=PING_COUNT, metavar="N",
                   help=f"Number of pings after warm-up (default: {PING_COUNT}).")
    p.add_argument("--output", type=Path, default=Path("websocket_results.json"),
                   help="Save results JSON (default: websocket_results.json).")
    return p


def main() -> None:
    args = build_parser().parse_args()

    # ── server-only mode ──────────────────────────────────────────────────────
    if args.server:
        lan_ip = get_lan_ip()
        print(
            f"\n  Starting Flask-SocketIO server on {lan_ip}:{args.port}\n"
            f"  From a second device on the same Wi-Fi:\n"
            f"    Browser  → http://{lan_ip}:{args.port}/\n"
            f"    Terminal → python benchmark_websocket.py --client "
            f"--host {lan_ip} --port {args.port}\n"
            "  Press Ctrl+C to stop.\n"
        )
        app, socketio = build_app(lan_ip, args.port)
        socketio.run(app, host=lan_ip, port=args.port)
        return

    # ── client-only mode (connect to an existing --server) ────────────────────
    if args.client:
        if not args.host:
            sys.exit("[ERROR] --client requires --host <server-ip>")
        print(f"\n[CLIENT] Benchmarking {args.host}:{args.port} …\n")
        rtts = run_client_benchmark(args.host, args.port, args.pings)
        result = print_report(rtts, mode=f"LAN → {args.host}:{args.port}")
        args.output.write_text(json.dumps(result, indent=2))
        print(f"  Saved → {args.output}")
        return

    # ── localhost benchmark (default) ─────────────────────────────────────────
    print("\n[BENCH] Localhost Flask-SocketIO latency benchmark …\n")
    start_server_thread("127.0.0.1", args.port)

    print(
        f"  Server: http://127.0.0.1:{args.port}\n"
        f"  Warm-up pings: {WARMUP_PINGS}  |  Benchmark pings: {args.pings}\n"
    )
    rtts = run_client_benchmark("127.0.0.1", args.port, args.pings)
    result = print_report(rtts, mode="localhost")

    all_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "platform":  platform.system() + " " + platform.release(),
        "results":   [result],
    }
    args.output.write_text(json.dumps(all_results, indent=2))
    print(f"  Saved → {args.output}")


if __name__ == "__main__":
    main()
