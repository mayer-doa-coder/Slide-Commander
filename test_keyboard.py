#!/usr/bin/env python3
"""
test_keyboard.py — PyAutoGUI Key Simulation Test  (Task 1.2)

Validates that PyAutoGUI sends RIGHT / LEFT / CTRL+HOME / CTRL+END to the
active window without requiring administrator privileges.

Usage:
  pip install pyautogui
  python test_keyboard.py

  # Run a specific action only:
  python test_keyboard.py --action next

  # Skip the countdown (fire immediately — useful when you switch windows manually):
  python test_keyboard.py --delay 0

Acceptance criteria (Task 1.2):
  RIGHT/LEFT confirmed to advance/go back slides on Windows, macOS, Ubuntu
  without admin privileges.

How to use:
  1. Open PowerPoint / LibreOffice Impress / PDF viewer in slideshow mode.
  2. Run this script in a terminal.
  3. Switch to the presentation window when the countdown starts.
  4. Observe whether slides advance/go back.
  5. Answer the Y/N prompt.
  6. Results are saved to keyboard_test_results.json.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# ── key mappings per platform ─────────────────────────────────────────────────

def _modifier() -> str:
    """Return the correct modifier key for first/last slide shortcuts."""
    return "command" if platform.system() == "Darwin" else "ctrl"


ACTIONS: Dict[str, dict] = {
    "next":  {"description": "NEXT slide (RIGHT arrow)",          "key": "right",  "hotkey": None},
    "back":  {"description": "PREVIOUS slide (LEFT arrow)",       "key": "left",   "hotkey": None},
    "first": {"description": "FIRST slide (CTRL/CMD + HOME)",     "key": None,     "hotkey": (_modifier(), "home")},
    "last":  {"description": "LAST slide  (CTRL/CMD + END)",      "key": None,     "hotkey": (_modifier(), "end")},
}


def send_action(action: str) -> None:
    """Send the key press for the given action name."""
    try:
        import pyautogui
    except ImportError:
        sys.exit("[ERROR] PyAutoGUI not installed.  Run: pip install pyautogui")

    spec = ACTIONS[action]
    if spec["key"]:
        pyautogui.press(spec["key"])
    else:
        pyautogui.hotkey(*spec["hotkey"])


def run_test(
    actions: List[str],
    countdown: int,
    results_path: Path,
) -> None:
    try:
        import pyautogui  # noqa: F401 — validate import early
    except ImportError:
        sys.exit("[ERROR] PyAutoGUI not installed.  Run: pip install pyautogui")

    print(
        "\n─────────────────────────────────────────────────────────────\n"
        "  SlideCommander — PyAutoGUI Key Simulation Test  (Task 1.2)\n"
        "─────────────────────────────────────────────────────────────\n"
        f"  Platform : {platform.system()} {platform.release()}\n"
        f"  Modifier : {_modifier()}\n"
        f"  Actions  : {', '.join(actions)}\n"
        "\n  INSTRUCTIONS:\n"
        "    1. Open a presentation in slideshow mode (PowerPoint, Impress, Keynote, PDF).\n"
        "    2. Press ENTER here to start the countdown.\n"
        "    3. Switch to the presentation window BEFORE the countdown ends.\n"
        "    4. Observe whether the key presses work.\n"
        "    5. Answer the prompts.\n"
    )
    input("  Press ENTER to begin …")

    test_results: List[dict] = []

    for action in actions:
        spec = ACTIONS[action]
        print(f"\n  ─── Test: {spec['description']} ───")

        if countdown > 0:
            print(f"  Switching to presentation in ", end="", flush=True)
            for i in range(countdown, 0, -1):
                print(f"{i} … ", end="", flush=True)
                time.sleep(1)
            print("sending!")
        else:
            print("  Sending key press now …")

        send_action(action)
        time.sleep(0.5)  # let the key event register before prompting

        # Bring terminal back to foreground for user input
        print(f"\n  Did '{spec['description']}' work correctly in your presentation?")
        answer = input("  Enter Y (yes) or N (no): ").strip().upper()
        passed = answer == "Y"
        note   = ""
        if not passed:
            note = input("  Optional — describe what happened: ").strip()

        test_results.append({
            "action":      action,
            "description": spec["description"],
            "passed":      passed,
            "note":        note,
        })
        mark = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {mark}")

    # Summary
    passed_count = sum(1 for r in test_results if r["passed"])
    total = len(test_results)
    print(
        f"\n{'═' * 60}\n"
        f"  Results: {passed_count}/{total} actions passed\n"
        f"{'═' * 60}"
    )
    for r in test_results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark}  {r['description']}")
        if r["note"]:
            print(f"       Note: {r['note']}")

    # Save JSON
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "platform":  platform.system() + " " + platform.release(),
        "python":    platform.python_version(),
        "modifier":  _modifier(),
        "results":   test_results,
        "all_passed": passed_count == total,
    }
    results_path.write_text(json.dumps(output, indent=2))
    print(f"\n  Saved → {results_path}")
    print(
        "\n  Copy the per-action results into research_log.md §4.1\n"
        "  (Table: Platform / App tested / key results / Admin needed?)\n"
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="test_keyboard.py",
        description="PyAutoGUI key simulation test for SlideCommander (Task 1.2)",
    )
    p.add_argument(
        "--action", choices=list(ACTIONS.keys()),
        help="Test a single action instead of all four.",
    )
    p.add_argument(
        "--delay", type=int, default=5, metavar="SECS",
        help="Countdown seconds before each key press (default: 5).",
    )
    p.add_argument(
        "--output", type=Path, default=Path("keyboard_test_results.json"),
        help="Where to save results JSON (default: keyboard_test_results.json).",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    actions = [args.action] if args.action else list(ACTIONS.keys())
    run_test(actions, args.delay, args.output)


if __name__ == "__main__":
    main()
