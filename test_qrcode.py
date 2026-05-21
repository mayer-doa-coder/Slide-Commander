#!/usr/bin/env python3
"""
test_qrcode.py — QR Code Library Evaluation  (Task 1.4)

Generates a QR code for a SlideCommander URL, prints it in the terminal as
ASCII art (for phone scanning), and saves it as a PNG image.

Usage:
  pip install qrcode pillow

  python test_qrcode.py
  python test_qrcode.py --url http://192.168.1.100:5000
  python test_qrcode.py --url http://192.168.1.100:5000 --output qr.png

Acceptance criteria (Task 1.4):
  QR code is scannable by at least two mobile OS cameras from terminal output.
  Generation time recorded.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path


def get_local_ip() -> str:
    """Return this machine's LAN IP (not 127.0.0.1)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def generate_qr_terminal(url: str) -> float:
    """
    Print QR code as ASCII art to stdout.
    Returns generation time in ms.
    """
    try:
        import qrcode
    except ImportError:
        sys.exit("[ERROR] qrcode not installed.  Run: pip install qrcode pillow")

    t0 = time.perf_counter()
    qr = qrcode.QRCode(
        version=None,           # auto-fit
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% redundancy
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    elapsed_ms = (time.perf_counter() - t0) * 1_000

    # Print with ASCII characters that render clearly in most terminals
    # Using full-block characters for maximum scannability
    print("\n")
    qr.print_ascii(invert=True)  # invert=True gives dark-on-light (better contrast)
    print()
    return elapsed_ms


def save_qr_png(url: str, output_path: Path) -> None:
    """Save QR code as a PNG image."""
    try:
        import qrcode
    except ImportError:
        sys.exit("[ERROR] qrcode not installed.  Run: pip install qrcode pillow")

    img = qrcode.make(url)
    img.save(str(output_path))
    print(f"  PNG saved → {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="test_qrcode.py",
        description="QR code library evaluation for SlideCommander (Task 1.4)",
    )
    parser.add_argument(
        "--url", metavar="URL", default="",
        help="URL to encode.  Defaults to http://<local-ip>:5000",
    )
    parser.add_argument(
        "--output", metavar="FILE", type=Path, default=Path("qr_test.png"),
        help="Save PNG to this path (default: qr_test.png).",
    )
    parser.add_argument(
        "--results", metavar="FILE", type=Path, default=Path("qr_test_results.json"),
        help="Save results JSON (default: qr_test_results.json).",
    )
    args = parser.parse_args()

    url = args.url or f"http://{get_local_ip()}:5000"

    print(
        "\n─────────────────────────────────────────────────\n"
        "  SlideCommander — QR Code Library Test (Task 1.4)\n"
        "─────────────────────────────────────────────────\n"
        f"  URL encoded: {url}\n"
    )

    # Generate and print ASCII QR
    elapsed_ms = generate_qr_terminal(url)
    print(f"  URL: {url}\n")
    print(f"  Generation time: {elapsed_ms:.1f} ms")
    print(
        "\n  ── Scannability check ───────────────────────────\n"
        "  Scan the QR code above with your phone camera.\n"
        "  It should open (or copy) the URL shown above.\n"
    )

    # Save PNG as backup
    save_qr_png(url, args.output)

    # Collect user confirmation
    ios_ok     = input("\n  Did iOS camera scan successfully?     (Y/N): ").strip().upper() == "Y"
    android_ok = input("  Did Android camera scan successfully? (Y/N): ").strip().upper() == "Y"
    both_ok    = ios_ok and android_ok

    mark = "✓ PASS" if both_ok else ("✓ PARTIAL" if (ios_ok or android_ok) else "✗ FAIL")
    print(f"\n  Result: {mark}")
    if not both_ok:
        print(
            "  Tips for better terminal QR scannability:\n"
            "    • Increase terminal font size (Ctrl+= or Cmd+=)\n"
            "    • Ensure high contrast (white background / dark text)\n"
            "    • Step back from the screen\n"
        )

    results = {
        "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%S"),
        "url_encoded":     url,
        "generation_ms":   round(elapsed_ms, 1),
        "png_saved":       str(args.output),
        "scannable_ios":   ios_ok,
        "scannable_android": android_ok,
        "meets_criteria":  both_ok,
    }
    args.results.write_text(json.dumps(results, indent=2))
    print(f"  Results saved → {args.results}")
    print(
        "\n  Copy values into research_log.md §4.3\n"
        "  (Table: QR generated / iOS / Android / generation time)\n"
    )


if __name__ == "__main__":
    main()
