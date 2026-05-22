"""
QR code generation module — Layer 1 of the dependency DAG.

Generates and prints a terminal ASCII QR code encoding the server URL.
Used once at startup by main.py.
"""

from __future__ import annotations

import qrcode

from config import Config


def generate_and_print(url: str) -> None:
    """Print an ASCII QR code for *url* to stdout and save a PNG alongside it."""
    pass
