"""
UT-05: qr_display.generate_and_print() unit tests.

Physical scannability (iOS / Android camera) requires human verification.
These tests cover: output correctness, QR body presence, scan message,
no-exception guarantee, and graceful degradation without qrcode installed.
"""

import sys
import pytest
import qr_display


class TestUT05QRDisplay:
    """UT-05 — QR code terminal display."""

    def test_url_present_in_output(self, capsys):
        """URL string appears somewhere in stdout."""
        qr_display.generate_and_print("http://192.168.1.100:5000")
        assert "192.168.1.100:5000" in capsys.readouterr().out

    def test_scan_message_present(self, capsys):
        """'Scan to connect' prompt line is in output."""
        qr_display.generate_and_print("http://10.0.0.1:5000")
        assert "Scan to connect" in capsys.readouterr().out

    def test_qr_body_rendered(self, capsys):
        """Output has several non-empty lines — QR grid was printed, not just the URL."""
        qr_display.generate_and_print("http://192.168.0.1:5000")
        non_empty = [l for l in capsys.readouterr().out.split("\n") if l.strip()]
        assert len(non_empty) >= 5

    def test_no_exception_on_valid_url(self):
        """Function completes without raising for a typical LAN URL."""
        qr_display.generate_and_print("http://192.168.255.255:65535")

    def test_graceful_if_qrcode_missing(self, capsys, monkeypatch):
        """URL still printed to stdout even when the qrcode package is absent."""
        monkeypatch.setitem(sys.modules, "qrcode", None)
        qr_display.generate_and_print("http://fallback.test:5000")
        assert "fallback.test:5000" in capsys.readouterr().out

    def test_half_block_height(self):
        """_half_block() returns n/2 lines for an n-row (even) matrix."""
        matrix = [[True, False, True], [False, True, False]]   # 2×3
        result = qr_display._half_block(matrix)
        assert len(result.split("\n")) == 1   # 2 rows → 1 terminal line

    def test_half_block_odd_rows_padded(self):
        """_half_block() pads an odd-row matrix without raising."""
        matrix = [[True, False]] * 3   # 3 rows (odd)
        result = qr_display._half_block(matrix)
        assert isinstance(result, str)
