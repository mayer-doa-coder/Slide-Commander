# SlideCommander

Control any presentation from across the room — with your voice, your phone, and nothing else. No hardware remotes, no cloud accounts, no installation on the phone.

---

## Prerequisites

- **Python 3.9 or higher** on the presenter's machine (Windows 10+, macOS 12+, Ubuntu 20.04+)
- **Presenter's laptop and smartphone on the same Wi-Fi network**
- A presentation open in any app that responds to arrow keys (PowerPoint, Keynote, LibreOffice Impress, Google Slides in Chrome, PDF viewers)

> **macOS only:** PyAutoGUI requires Accessibility permission. Go to  
> *System Settings → Privacy & Security → Accessibility* and enable your Terminal or IDE.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/slidecommander.git
cd slidecommander

# 2. (Recommended) Create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install flask flask-socketio simple-websocket pyautogui qrcode pillow psutil
```

For **voice control**, install the speech recognition engine too:

```bash
pip install faster-whisper
```

---

## Usage: Quick Start

### 1. Launch the server

```bash
python main.py
```

The terminal will print a large ASCII QR code and a plain-text URL:

```
╔══════════════════╗
║  ██░░██████░░██  ║
║  ░░░░░░░░░░░░░░  ║
║  ██░░███░░█░░██  ║
╚══════════════════╝

  SlideCommander ready → http://192.168.0.42:5000
  Voice: ON  |  Mic: default input device
  Press Ctrl+C to stop.
```

### 2. Connect your phone

- Open your phone camera and point it at the QR code — tap the notification to open the URL in your browser.
- Or type the URL printed below the QR code directly into any mobile browser.

### 3. Control your slides

The phone browser shows the remote UI immediately — no app install required.

| Button | Action |
|---|---|
| **◀ BACK** | Previous slide (LEFT arrow) |
| **NEXT ▶** | Next slide (RIGHT arrow) |
| **⏮ FIRST** | Jump to first slide (Ctrl/Cmd + Home) |
| **LAST ⏭** | Jump to last slide (Ctrl/Cmd + End) |
| **‖ PAUSE** | Start / pause the presentation timer |

> **Tip:** Keep the presentation window in focus on the laptop. SlideCommander sends real keyboard events to whichever window is active — the same as pressing arrow keys on the keyboard.

---

## Voice Control Setup

SlideCommander listens to your laptop's microphone and responds to these spoken keywords:

| Say this | Effect |
|---|---|
| `"next"` | Next slide |
| `"back"` | Previous slide |
| `"go to slide N"` / `"goto slide N"` | Jump to slide N |
| `"start"` | Jump to first slide |
| `"pause"` | Toggle presentation timer |

Voice recognition runs **100% offline** using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). The model (~39 MB) is downloaded automatically on first run and cached locally — no internet connection is needed during presentations.

### First-run model download

The first time you launch with voice enabled, faster-whisper downloads the `tiny` English model (~39 MB) from Hugging Face. This takes 10–30 seconds depending on your connection. Subsequent launches use the local cache and start instantly.

```bash
# Default: voice ON, tiny model auto-downloaded
python main.py

# Specify a larger model for better accuracy (base ~74 MB)
python main.py --model base

# Disable voice entirely (button control only)
python main.py --no-voice
```

### Tips for best voice accuracy

- Speak clearly at a normal pace — no need to shout or slow down.
- The debounce window is 500 ms: speaking two commands back-to-back faster than that will only fire the first one.
- In noisy rooms, use `--no-voice` and control slides from the phone UI only.

---

## CLI Configuration

```
usage: python main.py [options]

Options:
  --port PORT       Port for the local web server (default: 5000, range: 1024–65535)
  --model SIZE      Whisper model size: tiny | base | small (default: tiny)
  --pin PIN         4-digit PIN to lock the remote UI (e.g. --pin 1234)
  --no-voice        Disable microphone / voice recognition entirely
  --list-mics       Print available audio input devices and exit
  --help            Show this message and exit
```

### Examples

```bash
# Run on a non-default port
python main.py --port 8080

# Enable PIN lock so only you can control slides
python main.py --pin 4827

# Use a more accurate (but slower) model in a noisy environment
python main.py --model base

# Button-only mode — no microphone used
python main.py --no-voice

# See available microphones before launching
python main.py --list-mics
```

---

## Project Structure

```
slidecommander/
├── main.py              # Entry point — CLI args, startup sequence
├── server.py            # Flask + Flask-SocketIO HTTP/WebSocket server
├── keyboard.py          # PyAutoGUI command→key mapping
├── voice.py             # faster-whisper audio capture + keyword spotting
├── qr_display.py        # Terminal ASCII QR code generation
├── config.py            # Central Config dataclass (all defaults + validation)
├── static/
│   └── index.html       # Mobile remote UI (HTML5 + Tailwind CSS)
├── tests/
│   └── test_config.py   # pytest unit tests
└── docs/
    ├── module_diagram.md # Module dependency graph (Task 2.1)
    ├── ui_wireframe.md   # Mobile UI wire-frame (Task 2.2)
    └── ws_protocol.md    # WebSocket message protocol (Task 2.3)
```

---

## Troubleshooting

**Phone can't connect to the server**
- Confirm both devices are on the same Wi-Fi network (not one on Wi-Fi, one on mobile data).
- Check that your laptop's firewall allows inbound connections on the chosen port (`5000` by default).
- Try a different port: `python main.py --port 8080`.

**Slides not advancing when I tap buttons**
- Click on the presentation window to bring it into focus before using the remote.
- On macOS, grant Accessibility permission to your Terminal (*System Settings → Privacy & Security → Accessibility*).

**Voice commands not being recognised**
- Check that the correct microphone is active: `python main.py --list-mics`.
- Speak the command word clearly as a single word, not in a sentence.
- In very noisy environments switch to button-only mode: `python main.py --no-voice`.

**Port already in use**
```
OSError: [Errno 98] Address already in use
```
Another application is using port 5000. Run: `python main.py --port 8080` (or any free port).

---

## License

MIT License — free to use, modify, and distribute.

---

*SlideCommander v1.0 — "No hardware. No cloud. No camera. Just Python, your voice, and your phone."*
