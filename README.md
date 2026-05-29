# SlideCommander

**Control any presentation from across the room — with your voice, your phone, and nothing else.**

No hardware remotes. No cloud accounts. No app installation on your phone. No internet required during presentations. Just Python running on your laptop and any smartphone browser on the same Wi-Fi.

---

## Table of Contents

1. [What Is SlideCommander?](#1-what-is-slidecommander)
2. [How It Works (Simple Overview)](#2-how-it-works-simple-overview)
3. [What You Need Before Starting](#3-what-you-need-before-starting)
4. [Installation](#4-installation)
   - [Step 1 — Get Python](#step-1--get-python)
   - [Step 2 — Download SlideCommander](#step-2--download-slidecommander)
   - [Step 3 — Install Dependencies](#step-3--install-dependencies)
5. [Quick Start (First Run)](#5-quick-start-first-run)
6. [The Phone Remote UI](#6-the-phone-remote-ui)
   - [Buttons](#buttons)
   - [Timer](#timer)
   - [Slide Counter](#slide-counter)
   - [Voice Indicator](#voice-indicator)
   - [Swipe Gestures](#swipe-gestures)
   - [Visual Feedback](#visual-feedback)
7. [Voice Control](#7-voice-control)
   - [Supported Voice Commands](#supported-voice-commands)
   - [Wake-Word Mode](#wake-word-mode)
   - [Tips for Best Accuracy](#tips-for-best-accuracy)
8. [All Command-Line Options](#8-all-command-line-options)
9. [Usage Examples](#9-usage-examples)
10. [Supported Presentation Software](#10-supported-presentation-software)
11. [Project Architecture (For Developers)](#11-project-architecture-for-developers)
    - [File Structure](#file-structure)
    - [Module Roles](#module-roles)
    - [Dependency Graph](#dependency-graph)
    - [Thread Model](#thread-model)
12. [WebSocket Protocol](#12-websocket-protocol)
    - [Events: Client → Server](#events-client--server)
    - [Events: Server → Client](#events-server--client)
    - [Error Codes](#error-codes)
13. [Configuration Reference](#13-configuration-reference)
14. [Running the Test Suite](#14-running-the-test-suite)
    - [Test Coverage Summary](#test-coverage-summary)
15. [Troubleshooting](#15-troubleshooting)
16. [Platform Notes](#16-platform-notes)
17. [License](#17-license)

---

## 1. What Is SlideCommander?

SlideCommander turns your smartphone into a wireless presentation remote. Once you start the program on your laptop, it:

- Hosts a tiny web page on your local Wi-Fi network.
- Displays a QR code in the terminal so you can connect your phone instantly.
- Accepts tap commands from the phone browser and translates them into real keyboard key presses on the laptop (arrow keys, Home, End, F5, Escape).
- Simultaneously listens to your laptop microphone and responds to spoken commands like "next", "back", or "go to slide 12".

Everything runs on your local network. No data ever leaves your laptop or phone. The speech recognition model runs 100% offline after the first download.

---

## 2. How It Works (Simple Overview)

```
Your Phone Browser
        │
        │  Wi-Fi (tap button or swipe)
        ▼
SlideCommander Server (running on your laptop)
        │
        ├── Sends arrow-key / Home / End keypresses to the active window
        │
        └── Voice thread (microphone) ──► same key presses
```

1. You run `python main.py` on the laptop.
2. A local web server starts on port 5000 (or any port you choose).
3. A QR code appears in the terminal. Scan it with your phone camera.
4. The phone opens the control UI in any browser. No app needed.
5. Every button tap on the phone sends a WebSocket message to the laptop.
6. The laptop simulates the matching keyboard shortcut, advancing or reversing the slide in whatever presentation app is open and focused.
7. At the same time, a background thread listens to the microphone and fires the same key presses when it hears a command word.

---

## 3. What You Need Before Starting

### Hardware
| Item | Requirement |
|---|---|
| Laptop / desktop | Windows 10+, macOS 12+, or Ubuntu 20.04+ |
| Smartphone | Any iPhone or Android with a browser (Safari, Chrome, Firefox) |
| Wi-Fi | Both devices on the **same** Wi-Fi network |
| Microphone | Built-in or external (for voice control) |

### Software
| Software | Version | Notes |
|---|---|---|
| Python | 3.9 or higher | Must be installed on the laptop |
| pip | Bundled with Python | Used to install dependencies |
| A presentation app | Any | PowerPoint, Keynote, LibreOffice Impress, Google Slides, PDF viewers |

### What you do NOT need
- A cloud account of any kind
- An app installed on your phone
- An internet connection after first setup
- A physical remote clicker

---

## 4. Installation

### Step 1 — Get Python

**Check if Python is already installed:**

```bash
python --version
```

If the output shows `Python 3.9` or higher, skip ahead to Step 2.

**If not installed:**
- **Windows:** Download from [python.org/downloads](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.
- **macOS:** Run `xcode-select --install` then install via [python.org](https://www.python.org/downloads/) or `brew install python`.
- **Ubuntu/Linux:** `sudo apt update && sudo apt install python3 python3-pip python3-venv`

---

### Step 2 — Download SlideCommander

**Option A — Git (recommended for developers):**

```bash
git clone https://github.com/your-username/slidecommander.git
cd slidecommander
```

**Option B — Download ZIP:**
Download the ZIP from the GitHub repository page, extract it, then open a terminal in the extracted folder.

---

### Step 3 — Install Dependencies

It is strongly recommended to use a **virtual environment** so SlideCommander's packages do not interfere with other Python projects on your machine.

**Create and activate a virtual environment:**

```bash
# Create the virtual environment (only needed once)
python -m venv .venv

# Activate it — Windows (Command Prompt / PowerShell):
.venv\Scripts\activate

# Activate it — macOS / Linux:
source .venv/bin/activate
```

You should see `(.venv)` appear at the start of your terminal prompt.

**Install all required packages:**

```bash
pip install -r requirements.txt
```

This installs:

| Package | Version | Purpose |
|---|---|---|
| flask | ≥ 3.0 | Local web server that serves the phone UI |
| flask-socketio | ≥ 5.0 | Real-time WebSocket communication |
| simple-websocket | ≥ 1.0 | WebSocket transport backend |
| pyautogui | ≥ 0.9.54 | Simulates keyboard key presses on the laptop |
| faster-whisper | ≥ 1.0 | Offline speech recognition (voice commands) |
| sounddevice | ≥ 0.4 | Cross-platform microphone audio capture |
| qrcode | ≥ 7.0 | Generates the terminal QR code |
| Pillow | ≥ 10.0 | Image processing for QR code rendering |
| psutil | ≥ 5.9 | System process utilities |

> **Note for non-IT users:** You only need to run `pip install -r requirements.txt` once. After that, just activate the virtual environment and run `python main.py` each time.

---

## 5. Quick Start (First Run)

**1. Open a terminal in the SlideCommander folder.**

**2. Activate the virtual environment** (if you created one):
```bash
# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate
```

**3. Start SlideCommander:**

```bash
python main.py
```

**4. What you will see in the terminal:**

```
╔══════════════════════════════════╗
║  ██░░██████░░████░░██████░░████  ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ║
║  ██░░███░░░░██░░░░██░░░░░░█░░██  ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ║
║  ██░░██████░░████░░██████░░████  ║
╚══════════════════════════════════╝

  Scan to connect: http://192.168.0.42:5000

  SlideCommander ready
  Voice: ON  |  Model: tiny  |  Mic: default input device
  Press Ctrl+C to stop.
```

**5. Connect your phone:**
- Open your phone camera and point it at the QR code.
- Tap the notification that appears to open the URL in your browser.
- Or manually type the URL shown below the QR code (e.g., `http://192.168.0.42:5000`) into any mobile browser.

**6. Open your presentation** on the laptop and click on it to make sure it has focus.

**7. Control slides** from your phone. That's it.

> **First-run voice model download:** The very first time you run SlideCommander with voice enabled, faster-whisper downloads the `tiny` English model (~39 MB) from Hugging Face. This takes 10–30 seconds depending on your connection. Every subsequent launch uses the cached model and starts instantly.

---

## 6. The Phone Remote UI

The phone browser shows a full-screen control interface. No installation required — it is a regular web page.

### Buttons

| Button | Label | Keyboard Action Sent | What It Does |
|---|---|---|---|
| ◀ BACK | BACK | LEFT arrow key | Go to previous slide |
| NEXT ▶ | NEXT | RIGHT arrow key | Go to next slide |
| ⏮ FIRST | FIRST | Home key | Jump to the very first slide |
| LAST ⏭ | LAST | End key | Jump to the very last slide |
| ▶ OPEN | (not shown by default) | F5 | Start / enter the presentation |
| ⏹ CLOSE | (not shown by default) | Escape | Exit the presentation |

> BACK and NEXT are the largest buttons, occupying the full bottom half of the screen for easy thumb-tapping.

---

### Timer

A built-in presentation timer is displayed on the phone UI.

| Control | What It Does |
|---|---|
| **START** | Begins counting up from 00:00 |
| **PAUSE** | Pauses the timer at its current time |
| **RESET** | Clears the timer back to 00:00 |

The timer runs entirely on the phone and does not affect the presentation software. It is purely to help you track how long you have been presenting.

---

### Slide Counter

Below the timer, a slide counter displays the current slide number. It updates automatically every time you tap NEXT, BACK, FIRST, or use a voice command. It shows "—" when not yet connected or when the total slide count is unknown.

---

### Voice Indicator

A strip at the top of the UI shows the current voice status:

| Indicator | Meaning |
|---|---|
| Green dot + **ON** | Microphone is active and listening |
| Red dot + **OFF** | Voice recognition is disabled (`--no-voice`) or sleeping (wake-word mode) |
| Animated waveform bars | Voice is actively listening |
| Blue label (e.g., **NEXT**) | The last command that voice recognition detected |

---

### Swipe Gestures

In addition to tapping buttons, you can swipe on the screen:

| Gesture | Action |
|---|---|
| Swipe left (→) | Next slide |
| Swipe right (←) | Previous slide |

Swipe must travel at least 60 pixels horizontally and be 1.5× more horizontal than vertical to be detected. Swipes on buttons are ignored.

---

### Visual Feedback

Every command (button, swipe, or voice) triggers visual feedback:

- **Central orb:** The large circle in the middle of the UI flashes and displays an icon + label for the command (e.g., "→ NEXT"). It pulses with an animated ring.
- **Ripple effect:** A water-ripple animation spreads from the point where you tap a button.
- **Command history ticker:** The last 4 commands are shown as a fading list (e.g., `NEXT › BACK › NEXT › FIRST`). The most recent command is brightest.
- **Haptic feedback:** On supported phones, a short vibration accompanies every voice-detected command.

---

## 7. Voice Control

SlideCommander listens to your laptop's microphone in a background thread. Audio is captured in 500 ms blocks, buffered into 2-second windows, and transcribed every ~1 second using the faster-whisper engine.

Speech recognition runs entirely offline — no audio is ever sent to the internet.

### Supported Voice Commands

Say any of these words or phrases naturally, at a normal speaking pace. You do not need to pause or speak slowly.

| Say This | Alternative Phrases | Action |
|---|---|---|
| `"next"` | `"forward"` | Go to next slide |
| `"back"` | `"previous"`, `"prev"` | Go to previous slide |
| `"start"` | `"first"`, `"beginning"` | Jump to first slide |
| `"end"` | `"last"`, `"final"` | Jump to last slide |
| `"pause"` | `"stop"`, `"resume"` | Toggle the presentation timer |
| `"open"` | `"present"` | Enter presentation mode (F5) |
| `"close"` | `"exit"`, `"quit"` | Exit presentation mode (Escape) |
| `"slide 5"` | `"go to slide 5"`, `"goto slide 5"` | Jump directly to slide 5 (any number) |

**Debounce:** Identical voice commands have a 1.5-second cooldown. Saying "next" twice within 1.5 seconds fires only once. Different commands each have their own independent cooldown, so saying "next" immediately followed by "back" works fine.

---

### Wake-Word Mode

Launch with `--wake-word` to require an activation phrase before SlideCommander responds to commands:

```bash
python main.py --wake-word
```

| Say This | Effect |
|---|---|
| `"on"` | Activates the listener (green indicator on phone) |
| `"off"` | Deactivates the listener (red indicator on phone) |

If the listener is active but no command is spoken for 30 seconds, it automatically goes back to sleep to save CPU.

This mode is useful when you are narrating something and do not want accidental voice triggers.

---

### Tips for Best Accuracy

- Speak clearly at a normal pace — no need to shout or slow down.
- The microphone used is your system default input device. Check which one is active with `python main.py --list-mics`.
- Use `--model base` for meaningfully better accuracy in noisy environments (the base model is ~74 MB, roughly twice the tiny model size).
- Use `--model small` for the best accuracy the offline engine can offer (~242 MB).
- In very noisy rooms or when you do not want voice at all, use `--no-voice` and rely entirely on phone buttons.
- Make sure your laptop microphone is not muted in system audio settings.

---

## 8. All Command-Line Options

Run `python main.py --help` at any time to see this summary:

```
usage: python main.py [options]

Options:
  --port PORT       Port for the local web server (default: 5000, range: 1024–65535)
  --model SIZE      Whisper model size: tiny | base | small (and .en variants; default: tiny)
  --no-voice        Disable microphone and voice recognition entirely
  --wake-word       Require "ON" spoken before commands are recognised
  --list-mics       Print available audio input devices and exit
  --help            Show this help message and exit
```

### Model Size Reference

| Model | Size | Accuracy | RAM Usage | Best For |
|---|---|---|---|---|
| `tiny` | ~39 MB | Good | ~200 MB | Default. Fast startup, works well in quiet rooms. |
| `tiny.en` | ~39 MB | Good (English only) | ~200 MB | Slightly faster if you only speak English. |
| `base` | ~74 MB | Better | ~400 MB | Recommended for slightly noisy environments. |
| `base.en` | ~74 MB | Better (English only) | ~400 MB | Same as base, English-only optimized. |
| `small` | ~242 MB | Best offline | ~1 GB | Noisy rooms or when accuracy is critical. |
| `small.en` | ~242 MB | Best (English only) | ~1 GB | Small, English only. |

---

## 9. Usage Examples

```bash
# Default run: port 5000, tiny model, voice ON
python main.py

# Run on a non-default port (useful if port 5000 is taken)
python main.py --port 8080

# Use a more accurate model in a noisier room
python main.py --model base

# Use the best accuracy model (slower to load)
python main.py --model small

# Button-only mode — no microphone used at all
python main.py --no-voice

# Require wake-word "ON" before responding to voice commands
python main.py --wake-word

# See what microphones are available before choosing one
python main.py --list-mics

# Combine options: port 8080, base model, wake-word mode
python main.py --port 8080 --model base --wake-word
```

---

## 10. Supported Presentation Software

SlideCommander works with any application that responds to keyboard shortcuts. It simply presses real keyboard keys via PyAutoGUI — the same as if you pressed them yourself.

| Application | Platform | Keys Used |
|---|---|---|
| Microsoft PowerPoint | Windows, macOS | Arrow keys, Home, End, F5, Escape |
| Apple Keynote | macOS | Arrow keys, Home, End |
| LibreOffice Impress | Windows, macOS, Linux | Arrow keys, Home, End, F5, Escape |
| Google Slides (in Chrome) | Any | Arrow keys, Home, End |
| PDF viewers (Adobe, Foxit, Okular) | Any | Arrow keys, Home, End |
| Any other app with arrow-key navigation | Any | Arrow keys |

> **Important:** The presentation window must be in focus (active/clicked) on your laptop. SlideCommander sends key presses to whichever window is currently active — just like pressing keys on the keyboard. If another window is active, the key presses go there instead.

---

## 11. Project Architecture (For Developers)

### File Structure

```
slidecommander/
├── main.py               # Entry point: CLI args, startup sequence, module wiring
├── server.py             # Flask + Flask-SocketIO HTTP and WebSocket server
├── keyboard.py           # PyAutoGUI command → key mapping and execution
├── voice.py              # faster-whisper audio capture and keyword spotting
├── qr_display.py         # Terminal Unicode QR code generation
├── config.py             # Central Config dataclass (all defaults + validation)
├── conftest.py           # pytest fixtures: stubs for pyautogui, qrcode, flask
├── requirements.txt      # Python dependency pinning
├── static/
│   └── index.html        # Mobile remote UI (HTML5 + Tailwind CSS + Socket.IO)
├── tests/
│   ├── test_config.py         # Unit tests: Config validation (30+ cases)
│   ├── test_keyboard.py       # Unit tests: key execution, goto slide, mode detection
│   ├── test_voice.py          # Unit tests: dispatch, debounce, keyword matching
│   ├── test_qr_display.py     # Unit tests: QR output, half-block rendering
│   ├── test_integration.py    # Integration tests IT-01 to IT-11 (end-to-end pipelines)
│   ├── run_latency_benchmark.py
│   └── run_voice_benchmark.py
├── docs/
│   ├── module_diagram.md  # Module dependency DAG
│   ├── ui_wireframe.md    # Mobile UI layout spec
│   ├── ws_protocol.md     # WebSocket message protocol reference
│   └── UAT_Protocol.md    # User Acceptance Test protocol
└── test_audio/            # Voice test WAV samples (back, end, final, last, next, pause, start)
```

---

### Module Roles

#### `config.py` — Configuration Foundation
Pure data layer. Defines the `Config` dataclass with all runtime settings and validates them at construction time. Has **zero imports** from the rest of the project — it is the foundation everything else builds on.

Fields:
- `port: int` — web server port (default: 5000, valid: 1024–65535)
- `model_path: str` — whisper model name (default: `"tiny"`)
- `no_voice: bool` — disable voice if True (default: False)
- `wake_word: bool` — require wake-word activation (default: False)

Property:
- `server_url` → returns `"http://0.0.0.0:{port}"`

Validation raises `ValueError` for:
- Ports outside 1024–65535
- Unrecognized model names

---

#### `keyboard.py` — Key Press Execution
Translates action name strings into actual OS-level key presses via PyAutoGUI. All commands — whether from button taps or voice — converge on the single `execute(action: str)` function here.

**Action → Key mapping:**

| Action | Key Sent | Notes |
|---|---|---|
| `next` | RIGHT arrow | — |
| `back` | LEFT arrow | — |
| `first` | HOME | — |
| `last` | END | — |
| `pause` | *(none)* | Timer-only event |
| `open` | F5 | Enter presentation mode |
| `close` | ESCAPE | Exit presentation mode |
| `goto:N` | Slide N | Mode-dependent (see below) |

**goto:N behaviour (two modes):**
- **Presentation mode** (fullscreen detected via Windows ctypes): types the number then presses Enter (native PowerPoint "go to slide" shortcut).
- **Edit mode** (not fullscreen): presses Home to go to slide 1, then presses Right arrow N−1 times. Capped at 500 slides for safety.

Thread safety: a module-level `_pyautogui_lock` prevents concurrent key presses when both the voice thread and the server thread receive commands simultaneously.

---

#### `voice.py` — Speech Recognition
Runs as a daemon thread started by `main.py`. Captures microphone audio via `sounddevice` at 16 kHz, accumulates 2-second windows with 1-second overlap, and transcribes each window using faster-whisper.

**Audio pipeline:**
```
Mic at 16 kHz
    → 500 ms blocks (8000 samples each)
    → Ring buffer of 4 blocks (2-second window)
    → faster-whisper transcribe (CPU, int8)
    → _dispatch(text) keyword matching
    → keyboard.execute(action) + on_command callback
```

**Debounce:** A per-command timestamp dictionary ensures at least 1.5 seconds between identical commands. Different commands have independent cooldown clocks.

**Wake-word logic:**
- `_WAKE_RE` regex: `\bon\b` — activates listening
- `_SLEEP_RE` regex: `\boff\b` — deactivates
- 30-second idle timeout auto-sleeps to conserve CPU

**Keyword → action map:**

| Keyword(s) | Action |
|---|---|
| `next`, `forward` | `next` |
| `back`, `previous`, `prev` | `back` |
| `start`, `first`, `beginning` | `first` |
| `end`, `last`, `final` | `last` |
| `pause`, `stop`, `resume` | `pause` |
| `open`, `present` | `open` |
| `close`, `exit`, `quit` | `close` |
| `slide N` regex match | `goto:N` |

---

#### `qr_display.py` — Terminal QR Code
Generates a Unicode block-character QR code and prints it to the terminal. Uses the `qrcode` library to build the boolean matrix, then renders it with Unicode half-block characters (▀ ▄ █ space) — two QR rows per terminal line — for compact display. Prints "Scan to connect: {url}" below the code. Degrades gracefully if the `qrcode` library is missing.

---

#### `server.py` — Flask + WebSocket Server
The network hub. Serves `static/index.html` over HTTP and handles real-time WebSocket events via Flask-SocketIO.

Tracks `_slide_counter` (module-level int) that increments on `next`, decrements on `back`, resets on `first`, and parses `goto:N` values. This counter is included in `ack` messages so the phone UI can display the current slide number.

`get_local_ip()` discovers the machine's LAN IP via a non-connecting UDP socket to 8.8.8.8, which causes the OS to select the correct outbound interface without actually transmitting data. Falls back to `127.0.0.1` if no network is available.

---

#### `main.py` — Orchestrator
The entry point. Parses CLI arguments with `argparse`, builds the `Config` object, prints the startup banner, calls `qr_display.generate_and_print()`, starts the voice thread (if not disabled), and then calls `server.start_server()` which blocks until Ctrl+C.

`main.py` is the **only** module that imports everything else. No other module imports `main.py`, keeping the dependency graph acyclic.

---

#### `static/index.html` — Mobile Remote UI
A single self-contained HTML file served by the Flask server. No build step, no framework beyond what is loaded from a CDN at runtime.

**Key front-end components:**

- **Particle canvas background:** 55 animated particles connected by distance-based lines (110 px threshold), rendered on a `<canvas>` element via `requestAnimationFrame`.
- **Waveform animation:** 14 bars with staggered heights and CSS keyframe delays. Paused when voice is inactive.
- **Central orb:** A layered set of `<div>` rings — a rotating conic-gradient scan ring (3.5 s), a breathing outer ring (3 s), and a core that shows the command icon and label for 1.8 s after each command.
- **Pulse rings:** Two rings that emit outward on every command.
- **Command history ticker:** Tracks the last 4 commands in a fading display (`NEXT › BACK › NEXT › FIRST`).
- **Ripple effect:** A `<span>` absolutely positioned at the touch point, scales from 0 to 1× over 550 ms.
- **Socket.IO client (v4.7.5):** Loaded from CDN. Handles connect/disconnect, emits `command` events, receives `ack` and `error` events.
- **Button debounce:** 350 ms cooldown on `_sendCmd` prevents double-firing from rapid taps.
- **Responsive layout:** CSS custom properties (`--orb`, `--nav-h`, etc.) adjust at four breakpoints: landscape phone (<500 px height), compact portrait (500–720 px), tablet (600 px+ width), and desktop (900 px+).

---

### Dependency Graph

The module dependency graph is a strict DAG — no circular imports:

```
config.py        (no project imports)
    ↑
keyboard.py      (imports config)
    ↑
qr_display.py    (imports config)
    ↑
voice.py         (imports config, keyboard)
    ↑
server.py        (imports config, keyboard)
    ↑
main.py          (imports all of the above)
```

This means you can import and test any lower layer without needing to load the layers above it.

---

### Thread Model

```
Process
├── Main thread
│   └── Flask-SocketIO server (blocking — runs until Ctrl+C)
│       └── Per-connection SocketIO handler threads (managed by Flask-SocketIO)
│           └── calls keyboard.execute() with _pyautogui_lock held
│
└── Daemon thread (started by main.py if voice is enabled)
    └── voice._worker()
        └── audio capture → transcription → keyword dispatch
            └── calls keyboard.execute() with _pyautogui_lock held
                └── calls on_command callback → server.broadcast_voice_event()
```

Both threads write to the laptop's keyboard through the same `_pyautogui_lock` in `keyboard.py`, preventing simultaneous key presses.

---

## 12. WebSocket Protocol

All communication between the phone browser and the laptop server uses Socket.IO v4 events over a WebSocket connection.

### Events: Client → Server

#### `command`
Sent when the user taps a button or swipes on the phone.

```json
{
  "action": "next",
  "source": "button",
  "ts": 1716900000000
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| `action` | string | `next`, `back`, `first`, `last`, `pause`, `open`, `close` | The command to execute |
| `source` | string | `"button"`, `"voice"` | Origin of the command |
| `ts` | integer | Unix milliseconds | Client-side timestamp for latency calculation |

#### `auth` *(PIN mode — reserved for future use)*
Used when a PIN is configured via `--pin` (not yet fully implemented in CLI).

```json
{
  "pin": "1234",
  "ts": 1716900000000
}
```

---

### Events: Server → Client

#### `ack`
Sent to the originating client (and broadcast to all clients for voice commands) after a command is successfully executed.

```json
{
  "action": "next",
  "source": "button",
  "ts": 1716900000123,
  "latency_ms": 12,
  "slide": 5
}
```

| Field | Type | Always Present | Description |
|---|---|---|---|
| `action` | string | Yes | The action that was executed |
| `source` | string | Yes | `"button"` or `"voice"` |
| `ts` | integer | Yes | Server timestamp in Unix ms |
| `latency_ms` | integer | No | Round-trip ms if client sent `ts` |
| `slide` | integer | No | Current slide number (omitted for `last` and `pause`) |

#### `error`
Sent when a command fails validation.

```json
{
  "code": "unknown_action",
  "message": "Action 'fly' is not recognised.",
  "ts": 1716900000999,
  "action": "fly"
}
```

---

### Error Codes

| Code | Meaning |
|---|---|
| `unknown_action` | The `action` field is not one of the seven allowed values |
| `not_authenticated` | PIN mode: command received before `auth` event |
| `wrong_pin` | PIN mode: the submitted PIN did not match |
| `pin_required` | PIN mode: no PIN was provided |
| `rate_limited` | Too many commands in a short window |
| `server_error` | Unexpected server-side exception |

---

## 13. Configuration Reference

All configuration is set at startup via CLI flags. There is no config file — everything is in `config.py` as a `Config` dataclass.

| Setting | CLI Flag | Default | Valid Range | Description |
|---|---|---|---|---|
| Port | `--port` | 5000 | 1024–65535 | Web server port |
| Model | `--model` | `tiny` | see table below | Whisper model for voice recognition |
| Voice | `--no-voice` | voice ON | — | Pass flag to disable voice |
| Wake-word | `--wake-word` | off | — | Pass flag to require "ON" before commands |

### Allowed Model Values

`tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large-v1`, `large-v2`, `large-v3`

Any other value causes a `ValueError` at startup with a clear message listing valid options.

---

## 14. Running the Test Suite

SlideCommander has a full pytest test suite. All tests run headlessly — no display, microphone, or physical keyboard required — because the test configuration in `conftest.py` stubs out PyAutoGUI, qrcode, and Flask.

```bash
# Install pytest (if not already installed)
pip install pytest

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only a specific test file
pytest tests/test_config.py -v

# Run only a specific test by name
pytest tests/test_voice.py::test_debounce_same_command -v
```

---

### Test Coverage Summary

| File | Tests | What Is Covered |
|---|---|---|
| `test_config.py` | 30+ | Default values, valid/invalid ports, all 11 model names, `server_url` property |
| `test_keyboard.py` | 15+ | All 8 action types, presentation vs. edit mode detection, goto slide (typewrite path & arrow path), out-of-range capping |
| `test_voice.py` | 20+ | Keyword→action dispatch, debounce timing (same command within 200 ms vs. after 1600 ms), independent cooldowns for different commands, wake-word regex, false-positive rejection |
| `test_qr_display.py` | 10+ | URL present in output, "Scan to connect" message, ≥5 non-empty lines, odd-row padding, graceful fallback without qrcode |
| `test_integration.py` | 11 | IT-01 to IT-11: full end-to-end pipeline from WebSocket `command` event through `keyboard.execute()` to PyAutoGUI; full voice→key pipeline |

**Integration test IDs:**

| ID | Pipeline | Description |
|---|---|---|
| IT-01 | WebSocket → keyboard | `command(next)` invokes the keyboard callback |
| IT-02 | WebSocket → ack | Valid command emits `ack` back to client |
| IT-03 | WebSocket → ack | `ack` echoes the original action |
| IT-04 | WebSocket → error | Unknown action emits `error` |
| IT-05 | WebSocket → keyboard | All 7 valid actions reach the keyboard callback |
| IT-06 | Voice → keyboard | `_dispatch("next", ...)` calls `keyboard.execute("next")` |
| IT-07 | Voice → keyboard | `_dispatch("back", ...)` calls `keyboard.execute("back")` |
| IT-08 | Voice → keyboard | `_dispatch("start", ...)` calls `keyboard.execute("first")` |
| IT-09 | Voice → keyboard | `_dispatch("end", ...)` calls `keyboard.execute("last")` |
| IT-10 | Voice → debounce | Same command within cooldown fires only once |
| IT-11 | Voice → goto | `_dispatch("slide 7", ...)` calls `keyboard.execute("goto:7")` |

---

## 15. Troubleshooting

### Phone cannot connect to the server

**Symptoms:** Phone browser says "site can't be reached" or the page never loads.

**Fixes:**
1. Confirm both devices are on the **same Wi-Fi network**. A phone on mobile data (4G/5G) cannot reach the laptop's local IP.
2. Check the IP address shown in the terminal. Sometimes laptops have multiple network interfaces and the displayed IP may be wrong. Try connecting to `http://127.0.0.1:5000` from the laptop browser first to confirm the server is running.
3. Check the laptop firewall. On Windows, allow inbound connections on the chosen port:
   - *Windows Defender Firewall → Advanced Settings → Inbound Rules → New Rule → Port → TCP → 5000*
4. Try a different port: `python main.py --port 8080`
5. Make sure no other application is using port 5000.

---

### Slides not advancing when tapping buttons

**Symptoms:** The phone UI shows "ONLINE" and the orb flashes, but slides do not move.

**Fixes:**
1. **Click on the presentation window** on the laptop to give it focus before using the remote. SlideCommander sends real keyboard events to the currently active window. If a different window is focused, that window receives the key presses.
2. On macOS, grant Accessibility permission to the Terminal or IDE you are running SlideCommander from: *System Settings → Privacy & Security → Accessibility → enable your terminal app*.
3. Confirm the presentation is open in a supported app (PowerPoint, Keynote, LibreOffice Impress, Google Slides in Chrome, or any PDF viewer).

---

### Voice commands not recognised

**Symptoms:** The voice indicator shows "ON" but spoken commands have no effect.

**Fixes:**
1. Check which microphone is selected: `python main.py --list-mics`. Look for the one that matches your preferred microphone.
2. Make sure your microphone is not muted in your system's audio settings (Windows Sound Settings, macOS Sound preferences).
3. Speak one of the supported command words clearly, in isolation. "Can you go to the next slide please" may not trigger — try just "next".
4. In noisy environments, use a larger model: `python main.py --model base`
5. If wake-word mode is enabled (`--wake-word`), say "on" first to activate the listener.
6. For complete silence, disable voice and use buttons only: `python main.py --no-voice`

---

### Port already in use

```
OSError: [Errno 98] Address already in use
```

Another application is using port 5000 (common on macOS — AirPlay Receiver uses port 5000 by default).

**Fix:**
```bash
python main.py --port 8080
```

Or on macOS, disable AirPlay Receiver: *System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off*

---

### Voice model download is slow or fails

The faster-whisper `tiny` model (~39 MB) is downloaded from Hugging Face on first run.

**Fixes:**
1. Ensure you have an internet connection for the first run.
2. If the download hangs, delete the partially downloaded cache (usually at `~/.cache/huggingface/hub/`) and retry.
3. After the first successful run, the model is cached locally and no internet is needed for future launches.

---

### QR code is garbled or missing in the terminal

Some terminal emulators do not support Unicode block characters well.

**Fixes:**
1. Try a different terminal: Windows Terminal, iTerm2 (macOS), or Gnome Terminal (Linux) render Unicode correctly.
2. If the QR code still looks wrong, type the URL printed below it manually into the phone browser.
3. The URL format is always `http://<laptop-IP>:<port>`.

---

### On Windows: `python` is not recognised

If `python` is not found, try `python3` or `py`:

```bash
py main.py
py -m venv .venv
```

Make sure Python was installed with "Add to PATH" checked.

---

## 16. Platform Notes

### Windows

- No special permissions required beyond standard firewall rules.
- The `goto:N` command in presentation mode uses ctypes to detect fullscreen state via the Windows API.
- If using PowerShell, the virtual environment activation command is `.venv\Scripts\Activate.ps1`. If you get an execution policy error:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### macOS

- **Accessibility permission is required** for PyAutoGUI to send key presses. Go to: *System Settings → Privacy & Security → Accessibility → enable your terminal or IDE*.
- Port 5000 is occupied by AirPlay Receiver by default in macOS 12+. Use `--port 8080` or disable AirPlay Receiver in settings.
- For Apple Silicon (M1/M2/M3) Macs, the `pip install` command installs native ARM builds of all packages automatically.

### Linux (Ubuntu / Debian)

- `sounddevice` requires PortAudio: `sudo apt install portaudio19-dev`
- `pyautogui` requires a display server. On headless servers (no GUI), SlideCommander cannot send key presses — it is designed for use on a presentation machine with a desktop environment.
- No special permissions required.

---

## 17. License

MIT License — free to use, modify, and distribute for personal or commercial purposes. See [LICENSE](LICENSE) for the full text.

---

*SlideCommander v1.0 — "No hardware. No cloud. No camera. Just Python, your voice, and your phone."*
