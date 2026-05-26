"""
NFR-01 Latency Benchmark
=========================
Measures the full WebSocket round-trip time:
    Client emit  →  Server receive  →  Server emit ack  →  Client receive

Connects to a running SlideCommander server and fires 100 "pause" commands,
records each RTT, then reports Median and P95 against NFR-01 thresholds:
    Median < 100 ms   AND   P95 < 150 ms

Usage (from project root or any directory):
    python tests/run_latency_benchmark.py --host 192.168.1.42
    python tests/run_latency_benchmark.py --host 127.0.0.1 --port 5000

The server must already be running:
    python main.py
"""

from __future__ import annotations

import argparse
import statistics
import sys
import threading
import time

import socketio

# ── NFR-01 thresholds ────────────────────────────────────────────────────────

MEDIAN_THRESHOLD_MS = 100
P95_THRESHOLD_MS    = 150
SAMPLE_COUNT        = 100
INTER_PING_SLEEP_S  = 0.05   # 50 ms between pings — prevents buffer flooding
ACK_TIMEOUT_S       = 5.0    # per-ping timeout before marking as dropped


# ── Helpers ──────────────────────────────────────────────────────────────────

def _percentile(data: list[float], p: float) -> float:
    """Linear-interpolation percentile — identical to numpy percentile default."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * p / 100.0
    lo, hi = int(k), min(int(k) + 1, n - 1)
    return sorted_data[lo] + (k - lo) * (sorted_data[hi] - sorted_data[lo])


def _print_report(rtts: list[float], dropped: int) -> bool:
    """Print ASCII statistics table. Returns True if NFR-01 is satisfied."""
    med = statistics.median(rtts)
    p95 = _percentile(rtts, 95)
    p99 = _percentile(rtts, 99)
    minimum = min(rtts)
    maximum = max(rtts)
    mean    = statistics.mean(rtts)

    med_ok = med < MEDIAN_THRESHOLD_MS
    p95_ok = p95 < P95_THRESHOLD_MS
    passed  = med_ok and p95_ok

    sep = "+" + "-" * 28 + "+" + "-" * 14 + "+" + "-" * 12 + "+"
    print("\n" + sep)
    print(f"| {'Metric':<26} | {'Value':>12} | {'Status':<10} |")
    print(sep)
    print(f"| {'Samples':<26} | {len(rtts):>10}   | {'─':─<10} |")
    print(f"| {'Dropped / timed-out':<26} | {dropped:>10}   | {'─':─<10} |")
    print(sep)
    print(f"| {'Min RTT':<26} | {minimum:>9.2f} ms | {'─':─<10} |")
    print(f"| {'Mean RTT':<26} | {mean:>9.2f} ms | {'─':─<10} |")
    print(f"| {'Median RTT  (< 100 ms)':<26} | {med:>9.2f} ms | {'PASS' if med_ok else 'FAIL ✗':<10} |")
    print(f"| {'P95 RTT     (< 150 ms)':<26} | {p95:>9.2f} ms | {'PASS' if p95_ok else 'FAIL ✗':<10} |")
    print(f"| {'P99 RTT':<26} | {p99:>9.2f} ms | {'─':─<10} |")
    print(f"| {'Max RTT':<26} | {maximum:>9.2f} ms | {'─':─<10} |")
    print(sep)
    verdict = "[PASS] NFR-01 Satisfied" if passed else "[FAIL] NFR-01 NOT Satisfied"
    print(f"\n  {verdict}")
    if not passed:
        if not med_ok:
            print(f"  ✗ Median {med:.2f} ms exceeds {MEDIAN_THRESHOLD_MS} ms threshold.")
        if not p95_ok:
            print(f"  ✗ P95 {p95:.2f} ms exceeds {P95_THRESHOLD_MS} ms threshold.")
    print()
    return passed


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="SlideCommander NFR-01 latency benchmark"
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="Server LAN IP or hostname (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000,
                        help="Server port (default: 5000)")
    parser.add_argument("--count", type=int, default=SAMPLE_COUNT,
                        help=f"Number of pings (default: {SAMPLE_COUNT})")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    print("\n====================================================")
    print("  SlideCommander  NFR-01  Latency Benchmark        ")
    print("====================================================")
    print(f"  Target     : {url}")
    print(f"  Pings      : {args.count}")
    print(f"  Interval   : {int(INTER_PING_SLEEP_S * 1000)} ms between pings")
    print(f"  Thresholds : Median < {MEDIAN_THRESHOLD_MS} ms  |  P95 < {P95_THRESHOLD_MS} ms\n")

    sio = socketio.Client(logger=False, engineio_logger=False)

    # Per-ping synchronisation primitives shared with the ack callback.
    _ack_event   = threading.Event()
    _ack_payload: dict = {}

    @sio.on("ack")
    def _on_ack(data: dict) -> None:
        _ack_payload.clear()
        _ack_payload.update(data)
        _ack_event.set()

    @sio.on("error")
    def _on_error(data: dict) -> None:
        print(f"  [ERROR] Server returned: {data}")
        _ack_event.set()  # unblock the wait so the ping is counted as dropped

    print(f"  Connecting to {url} …", flush=True)
    try:
        sio.connect(url, transports=["websocket"])
    except Exception as exc:
        print(f"\n  [FATAL] Could not connect: {exc}")
        print("  Is `python main.py` running on the target machine?\n")
        sys.exit(1)

    print("  Connected.  Starting measurement loop…\n")

    rtts: list[float] = []
    dropped = 0

    for i in range(1, args.count + 1):
        _ack_event.clear()
        client_ts_ms = int(time.time() * 1000)

        t0 = time.perf_counter()
        sio.emit("command", {
            "action": "pause",
            "source": "benchmark",
            "ts":     client_ts_ms,
        })

        got_ack = _ack_event.wait(timeout=ACK_TIMEOUT_S)
        t1 = time.perf_counter()

        if not got_ack:
            dropped += 1
            print(f"  [{i:>3}/{args.count}]  TIMEOUT (dropped #{dropped})")
        else:
            rtt_ms = (t1 - t0) * 1000
            rtts.append(rtt_ms)
            server_one_way = _ack_payload.get("latency_ms", "n/a")
            print(f"  [{i:>3}/{args.count}]  RTT = {rtt_ms:6.2f} ms"
                  f"  (server one-way: {server_one_way} ms)")

        time.sleep(INTER_PING_SLEEP_S)

    sio.disconnect()

    if not rtts:
        print("\n  [FATAL] No successful pings — cannot compute statistics.\n")
        sys.exit(1)

    _print_report(rtts, dropped)


if __name__ == "__main__":
    main()
