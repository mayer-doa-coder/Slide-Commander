"""
QR code generation module — Layer 1 of the dependency DAG.

Generates and prints a terminal QR code encoding the server URL.
Primary renderer: Unicode half-block characters (▀ ▄ █ ' ') — two QR rows
per terminal line, high contrast on dark terminals.
Fallback: qr.print_ascii(invert=True) if get_matrix() is unavailable.
Degrades gracefully with a hint message if qrcode is not installed at all.
Used once at startup by main.py.
"""

from __future__ import annotations


def _half_block(matrix: list[list[bool]]) -> str:
    """Render a QR boolean matrix using Unicode half-block characters.

    Two QR rows map to one terminal line, halving the height.
    Convention: dark module (True) → empty cell, light module (False) → filled.
    On a dark terminal, light QR modules appear as solid white blocks and
    dark modules blend into the background — correct polarity for scanning.

      both light  → '█'    top light / bot dark  → '▀'
      top dark / bot light → '▄'    both dark   → ' '
    """
    n_rows = len(matrix)
    n_cols = len(matrix[0]) if matrix else 0
    if n_rows % 2:
        matrix = matrix + [[False] * n_cols]
    rows = []
    for y in range(0, len(matrix), 2):
        row = []
        for x in range(n_cols):
            top = matrix[y][x]      # True = dark module
            bot = matrix[y + 1][x]
            if not top and not bot:
                row.append('█')
            elif not top and bot:
                row.append('▀')
            elif top and not bot:
                row.append('▄')
            else:
                row.append(' ')
        rows.append('  ' + ''.join(row))
    return '\n'.join(rows)


def generate_and_print(url: str) -> None:
    """Print a QR code for *url* to stdout, then a plaintext scan prompt."""
    try:
        import qrcode
        import qrcode.constants

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        try:
            print(_half_block(qr.get_matrix()))
        except AttributeError:
            qr.print_ascii(invert=True)

    except Exception:
        print("  (install 'qrcode[pil]' for QR display)")

    print(f"\n  Scan to connect: {url}\n")
