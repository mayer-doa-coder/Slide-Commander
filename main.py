"""
SlideCommander — entry point.

Parses CLI arguments, builds Config, starts all subsystems, and blocks
until the user presses Ctrl+C.  This module is imported by nothing; it
is only ever run as __main__.
"""

from __future__ import annotations

import argparse
import sys

from config import Config
import keyboard
import server
import voice
import qr_display


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="slidecommander",
        description="SlideCommander — offline voice + phone presentation remote",
    )
    p.add_argument("--port",      type=int, default=5000, metavar="PORT",
                   help="Specify the port for the local web server (default: 5000).")
    p.add_argument("--model",     type=str, default="tiny", metavar="SIZE",
                   help="Set the faster-whisper model size (e.g., tiny, base, small). Defaults to 'tiny'.")
    p.add_argument("--no-voice",  action="store_true",
                   help="Disable the voice recognition module to save memory and CPU.")
    p.add_argument("--wake-word", action="store_true",
                   help="Require 'Hey Slide' before commands are accepted. Prevents false positives.")
    p.add_argument("--list-mics", action="store_true",
                   help="Display a numbered list of all available audio input devices and exit.")
    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.list_mics:
        import sounddevice as sd
        print("\nAvailable audio input devices:\n")
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                print(f"  [{i:2d}]  {dev['name']}")
        print()
        sys.exit(0)

    cfg = Config(
        port=args.port,
        model_path=args.model,
        no_voice=args.no_voice,
        wake_word=args.wake_word,
    )

    # ── Startup banner — printed before ANY blocking operation ───────────────
    # get_local_ip() is a fast stdlib socket call (<5ms); safe to call here.
    local_ip = server.get_local_ip()
    url = f"http://{local_ip}:{cfg.port}"

    print()
    print("=" * 34)
    print("  === SlideCommander ===")
    print("=" * 34)
    print(f"  URL:   {url}")
    print(f"  Voice: {'OFF' if cfg.no_voice else 'ON'}")
    if not cfg.no_voice and cfg.wake_word:
        print(f"  Wake:  ON / OFF")
    print(f"  Model: {cfg.model_path}")
    print("=" * 34)
    print("  Open the URL on your phone (same Wi-Fi).")
    print("  Press Ctrl+C to stop.")
    print()
    sys.stdout.flush()   # guarantee banner appears before any blocking subsystem
    # ── End banner ────────────────────────────────────────────────────────────

    # QR code (stub — fully implemented in Task 3.5)
    qr_display.generate_and_print(url)

    # Voice listener (stub — fully implemented in Task 3.3)
    # Heavy model load happens inside start_listening(), after the banner.
    if not cfg.no_voice:
        voice.start_listening(cfg, on_command=server.broadcast_voice_event)

    # Start server — blocks until Ctrl+C
    server.start_server(cfg, keyboard_callback=keyboard.execute)


if __name__ == "__main__":
    main()
