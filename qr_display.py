"""
QR code generation module — Layer 1 of the dependency DAG.

Generates and prints a terminal ASCII QR code encoding the server URL.
Used once at startup by main.py.
"""

from __future__ import annotations


def generate_and_print(url: str) -> None:
    """Print an ASCII QR code for *url* to stdout, followed by the plaintext URL."""
    try:
        import qrcode
        import qrcode.constants

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception:
        print("  (install 'qrcode' for QR display)")

    print(f"  {url}\n")
