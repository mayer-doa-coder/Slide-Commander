# SlideCommander — Project Plan | *Confidential Draft*

---

> **AI SYSTEM DIRECTIVE (CRITICAL):**
> This is the canonical requirements and design source for SlideCommander.
> ALWAYS read this file AND [`execution_plan.md`](execution_plan.md) together before suggesting next steps, writing code, or modifying the architecture.
> ANY change to scope, requirements, or design in this file MUST be reflected in [`execution_plan.md`](execution_plan.md) immediately.
> NEVER implement a feature that is not traceable to a Functional Requirement (FR-XX) in Section 5.

**Bidirectional Link:** → Execution tracker: [`execution_plan.md`](execution_plan.md)

---

# PROJECT PLAN

# SlideCommander

### *A Lightweight Local Presentation Remote*

Control any presentation from across the room —
with your voice, your phone, and nothing else.

**Prepared by:** [Your Name / Team Name]

**Institution:** [University / Organization]

**Date:** May 2026

**Version:** 1.0

---

# 1. Project Overview

## 1.1 Simple Explanation

SlideCommander is a lightweight Python application that turns any laptop or desktop into a universal presentation remote control system. Once launched, it runs a local web server on the presenter's machine. The presenter can then open a webpage on their smartphone (connected to the same Wi-Fi network) and tap large, finger-friendly buttons to advance or go back through slides. Alternatively, the presenter can simply say the words "next" or "back" out loud, and the software will detect those voice commands and perform the corresponding action — all without any internet connection, external hardware, or cloud services.

The core insight is simple: almost every computer can simulate keyboard key-presses, and almost every presentation tool (PowerPoint, Google Slides, PDF viewers, Keynote) responds to the arrow keys. SlideCommander wraps this universal behavior inside a modern, zero-install, Wi-Fi-based remote control.

## 1.2 Objectives & Goals

- **Provide a free, open-source alternative to proprietary hardware presentation remotes.**
- **Support all major presentation formats without requiring special plugins or integrations.**
- **Enable voice-driven control using an offline, lightweight speech recognition engine.**
- **Deliver a phone-optimized web UI reachable via any mobile browser over Wi-Fi.**
- **Ensure the entire system runs with a single terminal command and zero configuration.**
- **Keep the tool privacy-first: no data leaves the user's local network.**

## 1.3 Problem Being Solved

Presenters today face a frustrating set of trade-offs when delivering presentations away from their desk:

- Bluetooth hardware remotes (Logitech Spotlight, Kensington) cost $30–$150 and require USB dongles or pairing rituals.
- Commercial apps like Keynote Remote only work within Apple's ecosystem.
- Cloud-based solutions (Google Slides mobile remote) require internet and a Google account.
- Built-in screen-share or pointer tools do not advance slides on all platforms.
- Classroom or boardroom environments often have inconsistent Bluetooth coverage.

SlideCommander solves all these problems at once with a single Python script and a local Wi-Fi network — both of which are already present in virtually every presentation environment.

## 1.4 Real-World Applications

- Academic lectures and classroom teaching sessions.
- Corporate boardroom and investor presentations.
- Conference talks, seminars, and panel discussions.
- Remote team meetings where the presenter shares their screen.
- Online teaching platforms where the instructor controls local slides.
- Accessibility tool for users with limited mobility who prefer voice control.
- Museum kiosk presentations and digital signage rotation.

---

# 2. Background & Motivation

## 2.1 Why This Project Matters

Presentations remain the dominant medium for knowledge transfer in academic, professional, and public settings. According to industry reports, over 30 million PowerPoint presentations are delivered globally every single day. The experience of delivering a presentation, however, has barely evolved — the presenter is still tethered to their machine or dependent on expensive proprietary hardware.

The proliferation of smartphones (ownership exceeding 6.8 billion globally as of 2024) and ubiquitous Wi-Fi in public and institutional spaces creates a ready infrastructure for a software-only remote solution. SlideCommander capitalizes on this infrastructure with zero additional cost to the user.

## 2.2 Current Challenges in Presentation Control

**Hardware Dependency**

- Most professional remotes require USB Bluetooth receivers or manual pairing — a friction point in shared presentation environments.
- Hardware devices are an additional expense and can be forgotten, lost, or run out of battery.

**Platform Lock-in**

- Apple's Keynote Remote works only with Apple devices. Google Slides' companion app requires a Google account and internet.
- Windows and Linux users are essentially underserved by app-based remote solutions.

**Privacy and Connectivity Concerns**

- Cloud-connected remotes transmit control signals through external servers, creating both privacy risks and latency.
- Conference venues frequently block outbound traffic on firewalled Wi-Fi networks, making cloud tools unreliable.

**Voice Control Gaps**

- No mainstream free tool offers offline, lightweight voice control for slide advancement.
- Tools that do offer voice control (Dragon NaturallySpeaking) are expensive and complex to set up.

## 2.3 Existing Solutions & Limitations

| **Solution** | **Type** | **Key Limitation** | **Cost** |
|---|---|---|---|
| **Logitech Spotlight** | Hardware Remote | Requires USB dongle; $130 cost | $130 |
| **Apple Keynote Remote** | Mobile App | Apple-only ecosystem | Free (Apple-only) |
| **Google Slides Remote** | Web App | Requires internet & Google account | Free |
| **Unified Remote** | Mobile App | Requires install on phone; some features paid | Freemium |
| **SlideCommander** | Local Python Server | Requires Python on host machine | Free & Open Source |

---

# 3. Scope of the Project

## 3.1 What Is Included

- **A Python-based local HTTP/WebSocket server (Flask or FastAPI).**
- **A mobile-optimized browser UI with large Next / Back / Start / End buttons.**
- **Offline voice recognition module using Vosk or Whisper.cpp (keyword spotting for 'next', 'back', 'start', 'end', 'pause').**
- **Keyboard simulation layer (PyAutoGUI / pynput) to send arrow key events to the active window.**
- **QR code auto-display on launch for instant phone connection.**
- **Cross-platform support: Windows 10+, macOS 12+, Ubuntu 20.04+.**
- **A single-file launcher script: `python slidecommander.py`.**
- **Basic presenter timer display on the phone UI.**
- **Slide number / progress indicator (where the host app exposes it via OS accessibility APIs).**

## 3.2 What Is Excluded

- Cloud sync, remote internet control, or any data transmission beyond local Wi-Fi.
- Screen mirroring or video streaming of the presenter's display.
- Deep integration with presentation software APIs (e.g., COM automation of PowerPoint).
- Mobile app packaging (Android APK / iOS .ipa) — browser only.
- Multi-presenter or audience interaction features (Q&A, polls).
- Annotation or laser-pointer functionality (planned as future enhancement).
- NLP understanding beyond fixed command keywords in voice mode.

## 3.3 Assumptions

> ℹ  All assumptions listed below are required for the system to function correctly.

- The presenter's computer and smartphone are connected to the same Wi-Fi network.
- Python 3.9 or higher is installed on the presenter's computer.
- The active presentation window on the host machine responds to keyboard arrow keys.
- The host machine's firewall allows inbound TCP connections on the selected port (default: 5000).
- The smartphone microphone is accessible by the mobile browser (for future on-device voice expansion).
- The presentation environment has a standard Wi-Fi network; enterprise 802.1X client isolation is NOT assumed.

---

# 4. Feasibility Analysis

## 4.1 Technical Feasibility

**✔  HIGH — All required technologies are mature and freely available.**

Every component of SlideCommander relies on well-established, stable Python libraries. Flask/FastAPI have been in production use for over a decade. PyAutoGUI/pynput provide cross-platform keyboard simulation without OS-level drivers. Vosk offers 100% offline speech recognition with a 40 MB English model that runs on commodity hardware in real time. WebSocket support (via Flask-SocketIO or FastAPI WebSockets) is native in all modern browsers, including mobile Safari and Chrome.

- No proprietary SDKs, paid APIs, or hardware dependencies are required.
- The keyboard-simulation approach works with any application that responds to keyboard input, making it universally compatible.
- All chosen libraries have active maintenance and large community support bases.

## 4.2 Economic Feasibility

**✔  HIGH — Zero licensing cost; development cost is primarily developer time.**

| **Cost Item** | **Estimated Cost** | **Notes** |
|---|---|---|
| Python & all libraries | $0 | All open-source |
| Vosk English Model | $0 | Apache 2.0 license |
| Development hardware | $0 | Uses existing laptop |
| Testing devices | $0 | Personal smartphones |
| Hosting / deployment | $0 | Runs locally |
| **TOTAL** | **$0** | Pure open-source |

## 4.3 Operational Feasibility

**✔  HIGH — Single command to start; no training required for end users.**

- The presenter runs one command: `python slidecommander.py`. A QR code appears immediately.
- The audience member or operator scans the QR code on their phone and sees the remote UI instantly.
- No account creation, no app store download, no pairing ritual.
- The system is self-documenting: the UI labels all buttons clearly and voice commands are listed on screen.

## 4.4 Time Feasibility

**✔  ACHIEVABLE — Estimated 8–10 weeks for a solo developer; 4–5 weeks for a small team.**

- Core server + phone UI: 2 weeks.
- Keyboard simulation layer: 3–5 days.
- Voice recognition integration: 1 week.
- QR code generation + polish: 2–3 days.
- Cross-platform testing: 1 week.
- Documentation and packaging: 3 days.

---

# 5. Requirements

## 5A. Functional Requirements

### FR-01: Server Initialization

- On launch, the system SHALL start a local HTTP server on a user-configurable port (default: 5000).
- The system SHALL detect the host machine's local IP address automatically.
- The system SHALL generate and display a QR code in the terminal encoding the server URL.

### FR-02: Mobile Web Remote Interface

- The server SHALL serve a mobile-optimized HTML page at the root URL.
- The page SHALL display at minimum: NEXT, BACK, FIRST SLIDE, LAST SLIDE, and PAUSE TIMER buttons.
- Buttons SHALL be at least 64×64px for finger-tap accessibility.
- The page SHALL display a running presentation timer.
- The interface SHALL work on Chrome Mobile, Safari Mobile, and Firefox Mobile without any installation.

### FR-03: Keyboard Simulation

- On NEXT command, the system SHALL send the RIGHT ARROW key to the active foreground window.
- On BACK command, the system SHALL send the LEFT ARROW key.
- On FIRST SLIDE, the system SHALL send CTRL+HOME (or CMD+HOME on macOS).
- On LAST SLIDE, the system SHALL send CTRL+END.
- Key simulation SHALL work on Windows, macOS, and Linux without administrator privileges.

### FR-04: Voice Command Recognition

- The system SHALL continuously listen to the host machine's microphone.
- The system SHALL recognize the keywords: 'next', 'back', 'start', 'end', 'pause'.
- Voice recognition SHALL function entirely offline — no internet call is made.
- The system SHALL debounce voice commands (500ms minimum gap) to prevent accidental double-advance.
- Voice recognition mode SHALL be togglable via a command-line flag: `--no-voice`.

### FR-05: QR Code & Discovery

- The terminal output SHALL display a scannable QR code within 2 seconds of launch.
- The URL encoded in the QR code SHALL be the full local network address (e.g., http://192.168.1.10:5000).

### FR-06: Configuration

- Port number SHALL be configurable via `--port` flag.
- Voice recognition language model path SHALL be configurable via `--model` flag.
- A `--list-mics` flag SHALL enumerate available audio input devices.

## 5B. Non-Functional Requirements

### NFR-01: Performance

- Button press to keyboard event latency SHALL not exceed 100ms on a local Wi-Fi network.
- Voice recognition SHALL produce a result within 300ms of the command being spoken.
- The server SHALL handle up to 5 simultaneous WebSocket connections without degradation.

### NFR-02: Reliability

- The server SHALL reconnect automatically if a WebSocket client disconnects and reconnects.
- The system SHALL not crash if the microphone is unavailable; it SHALL log a warning and disable voice mode.

### NFR-03: Security

- The server SHALL bind only to the local network interface (not 0.0.0.0 on production mode).
- An optional `--pin` flag SHALL add a 4-digit PIN prompt on the remote UI to prevent unauthorized access.
- No sensitive data, keystrokes typed by the user, or screen content SHALL ever be transmitted.

### NFR-04: Usability

- Total setup time from terminal open to remote ready SHALL not exceed 60 seconds.
- The mobile UI SHALL be usable in a dark room without bright glare (dark theme default).

### NFR-05: Portability

- The codebase SHALL run on Python 3.9+ with dependencies installable via `pip install -r requirements.txt`.
- No OS-specific binaries SHALL be required beyond what pip provides.

---

# 6. System Design

## 6.1 High-Level Architecture

SlideCommander follows a three-tier local architecture: an input layer (phone browser & microphone), a server/logic layer (Python), and an output layer (keyboard simulation to the OS).

```
[ Phone Browser ] ──HTTP/WebSocket──► [ Python Server ] ──PyAutoGUI──► [ OS / App ]
                                              ↑
                                    [ Microphone → Vosk ]
```

## 6.2 Component / Module Breakdown

| **Module** | **Technology** | **Responsibility** |
|---|---|---|
| **main.py** | Python argparse | Entry point; CLI argument parsing; startup sequence |
| **server.py** | Flask + Flask-SocketIO | HTTP server; static file serving; WebSocket hub |
| **keyboard.py** | PyAutoGUI / pynput | Translate command names to OS key-press events |
| **voice.py** | Vosk + PyAudio | Mic capture; keyword spotting; emit events |
| **qr_display.py** | qrcode + Pillow | Generate & print QR code in terminal |
| **static/index.html** | HTML5 + Tailwind CSS | Mobile remote UI; WebSocket client JS |
| **config.py** | Python dataclass | Central config object passed to all modules |

## 6.3 Data Flow Explanation

### Path A: Button Press (Phone → Slide)

- User taps 'NEXT' on phone browser.
- Browser JS sends WebSocket message: `{action: 'next'}`.
- Flask-SocketIO receives message; routes to `keyboard.py`.
- `keyboard.py` calls `pyautogui.press('right')`.
- OS delivers key event to the active foreground window (PowerPoint, etc.).
- Slide advances. Total round-trip: < 100ms on LAN.

### Path B: Voice Command (Microphone → Slide)

- PyAudio streams 16kHz audio from the default microphone.
- Vosk processes each audio chunk; emits a partial/final JSON transcript.
- `voice.py` scans transcript text for keywords ('next', 'back', etc.).
- On keyword match (with 500ms debounce), emit same internal event as a button press.
- `keyboard.py` fires the corresponding key-press.
- Optionally, a WebSocket broadcast updates the phone UI to show 'Voice: NEXT detected'.

## 6.4 Database Design

> ℹ  SlideCommander is stateless by design — no database is required. Session state (timer value, current slide estimate) is held in Python memory variables and broadcast to connected WebSocket clients. No data is persisted to disk during a presentation session.

---

# 7. Technology Stack

| **Layer** | **Technology** | **Version** | **Justification** |
|---|---|---|---|
| **Language** | Python | 3.9+ | Cross-platform; rich ecosystem; standard in academia |
| **Web Server** | Flask + Flask-SocketIO | 3.x / 5.x | Minimal boilerplate; mature WebSocket support |
| **Frontend** | HTML5 + Tailwind CDN | Latest | Zero build step; single file; mobile-first utility CSS |
| **WebSocket Client** | Socket.IO JS (CDN) | 4.x | Automatic reconnection; matches server library |
| **Keyboard Sim** | PyAutoGUI | 0.9+ | Single API for Win/Mac/Linux key simulation |
| **Voice Engine** | Vosk | 0.3+ | Fully offline; 40MB model; Apache 2.0 license |
| **Audio Capture** | PyAudio | 0.2+ | Low-latency mic access across all platforms |
| **QR Generation** | qrcode + Pillow | 7.x / 10.x | Pure Python; terminal ASCII QR output |
| **Network Discovery** | socket (stdlib) | stdlib | No extra dependency needed for IP detection |
| **Packaging** | PyInstaller (optional) | 6.x | Creates standalone .exe/.app for non-Python users |

---

# 8. Workflow / Methodology

## 8.1 Development Methodology: Agile (Scrum-lite)

Agile is chosen over Waterfall because:

- Requirements for a novel UX tool like SlideCommander benefit from rapid prototyping and real-world testing feedback.
- Voice recognition accuracy and UI ergonomics can only be validated through iterative user testing.
- The team is small (1–3 developers), making ceremony-heavy Waterfall unnecessary.
- Agile allows reprioritization if cross-platform keyboard simulation proves harder than expected on a specific OS.

## 8.2 Sprint Plan (2-Week Sprints)

| **Sprint** | **Dates** | **Goals** | **Deliverable** |
|---|---|---|---|
| **Sprint 0** | Week 1–2 | Environment setup; dependency validation; repo scaffolding | Working skeleton |
| **Sprint 1** | Week 3–4 | Flask server; static HTML served; WebSocket echo test | Server + browser connected |
| **Sprint 2** | Week 5–6 | Keyboard simulation module; button-to-keypress pipeline | Phone controls PowerPoint |
| **Sprint 3** | Week 7–8 | Voice recognition; debounce; voice+button coexistence | Voice commands working |
| **Sprint 4** | Week 9–10 | QR code; timer; dark theme UI polish; PIN auth option | Feature-complete v1.0 |
| **Sprint 5** | Week 11–12 | Cross-platform testing; bug fixes; packaging; documentation | Releasable v1.0 |

---

# 9. Implementation Plan

## Phase 1: Research (Week 1–2)

> *Execution tracker:* See [Phase 1 tasks in execution_plan.md](execution_plan.md#phase-1-research--feasibility-validation-week-12)

**Goal: Validate all technical assumptions before writing production code.**

- Benchmark Vosk vs Whisper.cpp on target hardware for latency and accuracy.
- Test PyAutoGUI key simulation on Windows, macOS, and Ubuntu with PowerPoint, LibreOffice Impress, and a PDF viewer.
- Confirm Flask-SocketIO latency meets the 100ms requirement over a typical home Wi-Fi network.
- Evaluate qrcode library for terminal ASCII output quality.
- Document all findings in a Research Log markdown file.

## Phase 2: Design (Week 2–3)

> *Execution tracker:* See [Phase 2 tasks in execution_plan.md](execution_plan.md#phase-2-system-design-week-23)

**Goal: Produce all design artifacts before implementation begins.**

- Design the module dependency graph (which module imports which).
- Wire-frame the mobile remote UI — button layout, timer position, voice indicator.
- Define the WebSocket message protocol (JSON schema for all message types).
- Write the Configuration dataclass with all defaults and validation.
- Create the project README with setup instructions.

## Phase 3: Development (Week 3–10)

> *Execution tracker:* See [Phase 3.1–3.5 tasks in execution_plan.md](execution_plan.md#phase-31-core-server-week-34)

**Goal: Build all modules iteratively, integrating each before starting the next.**

### 3.1 – Core Server (Week 3–4)

- Implement `server.py` with Flask + Flask-SocketIO.
- Serve static `index.html` from a `/static` directory.
- Implement WebSocket event handlers: `connect`, `disconnect`, `command`.
- Implement IP auto-detection and startup logging.

### 3.2 – Keyboard Module (Week 5)

- Implement `keyboard.py` with a command→key mapping dictionary.
- Handle macOS vs Windows vs Linux platform differences (e.g., `super` vs `ctrl`).
- Write unit tests with mock key-press capture.

### 3.3 – Voice Module (Week 6–7)

- Implement `voice.py` with threaded PyAudio capture loop.
- Integrate Vosk recognizer with the 40 MB `vosk-model-en-us-0.22` model.
- Implement keyword extraction from partial transcripts.
- Add 500ms debounce logic.

### 3.4 – Mobile UI (Week 8)

- Build `index.html` with Tailwind CSS utility classes.
- Implement Socket.IO JS client with auto-reconnect.
- Add presentation timer (start/stop/reset).
- Add voice status indicator (listening / command detected).

### 3.5 – QR & Polish (Week 9–10)

- Implement `qr_display.py` using the qrcode library.
- Add `--pin` mode with a simple PIN entry form on the web UI.
- Add CLI `--help` documentation.

## Phase 4: Testing (Week 10–11)

> *Execution tracker:* See [Phase 4 tasks in execution_plan.md](execution_plan.md#phase-4-testing--bug-fixes-week-1011)

**Goal: Validate all functional and non-functional requirements.**

- Unit tests for keyboard.py and voice.py (pytest).
- Integration tests: simulate WebSocket commands; verify key presses.
- Cross-platform system tests on Windows 11, macOS Sonoma, Ubuntu 22.04.
- Latency benchmark: measure time from button tap to key event (target: <100ms).
- Voice accuracy test: 20 utterances per keyword; target >95% recognition rate.
- User acceptance test: 3 presenters use system in a real lecture setting.

## Phase 5: Deployment (Week 12)

> *Execution tracker:* See [Phase 5 tasks in execution_plan.md](execution_plan.md#phase-5-packaging--deployment-week-12)

**Goal: Package and publish the project for public use.**

- Publish to PyPI: `pip install slidecommander`.
- Create PyInstaller standalone builds for Windows (.exe) and macOS (.app).
- Publish source code to GitHub with MIT license.
- Write full documentation on GitHub Pages.
- Create a 3-minute demo video.

---

# 10. Algorithms / Logic

## 10.1 Voice Keyword Spotting with Debounce

The voice pipeline uses a sliding-window approach over Vosk partial transcripts to detect command keywords as soon as they are spoken, without waiting for the end of a sentence.

**Pseudocode: Voice Recognition Loop**

```
last_command_time = 0
DEBOUNCE_MS = 500
KEYWORDS = {'next': 'right', 'back': 'left', 'start': 'home', 'end': 'end', 'pause': 'pause'}

LOOP (while server running):

    audio_chunk = microphone.read(4000 samples)

    IF vosk_recognizer.AcceptWaveform(audio_chunk):
        result = json.loads(vosk_recognizer.Result())
        text = result['text'].lower()
    ELSE:
        partial = json.loads(vosk_recognizer.PartialResult())
        text = partial['partial'].lower()

    FOR keyword IN KEYWORDS:
        IF keyword IN text:
            now = current_time_ms()
            IF (now - last_command_time) > DEBOUNCE_MS:
                key = KEYWORDS[keyword]
                keyboard.press(key)
                last_command_time = now
                BREAK  ← only one command per chunk
```

## 10.2 WebSocket Command Routing

**Pseudocode: Server-Side Event Handler**

```
@socketio.on('command')
def handle_command(data):
    action = data.get('action')       # e.g., 'next', 'back', 'first', 'last'

    IF action NOT IN ALLOWED_ACTIONS:
        emit('error', {'msg': 'unknown action'})
        RETURN

    IF pin_enabled AND NOT session.get('authenticated'):
        emit('error', {'msg': 'not authenticated'})
        RETURN

    keyboard.execute(action)
    emit('ack', {'action': action, 'ts': timestamp()})
```

## 10.3 Local IP Auto-Detection

**Pseudocode: IP Discovery**

```
def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TRY:
        sock.connect(('8.8.8.8', 80))   ← does NOT send any packet
        ip = sock.getsockname()[0]       ← reads the source IP chosen by OS
    FINALLY:
        sock.close()
    RETURN ip
```

---

# 11. UI/UX Design

## 11.1 Screen Descriptions

### Screen 1: QR Code Launch Screen (Terminal)

When the Python server starts, the terminal displays a large ASCII QR code (approximately 30×30 characters) centered in the terminal window. Below the QR code, the URL is printed in plaintext (e.g., http://192.168.1.42:5000) for users who prefer to type the address. A status line confirms the server is running and voice mode status.

### Screen 2: Mobile Remote UI (Phone Browser)

The mobile UI is a single, scrollable page with a dark background (#0F172A) optimized for use in dark presentation rooms. Layout from top to bottom:

- Header bar: 'SlideCommander' title + connection status dot (green=connected, red=disconnected).
- Timer row: Large digital clock display (MM:SS) with Start / Pause / Reset buttons.
- Voice indicator row: A small badge showing 'Voice: ON' or 'Voice: OFF' and last detected command.
- Primary action buttons: Two large full-width buttons — '◀ BACK' (left, blue) and 'NEXT ▶' (right, blue). Each button is 96px tall.
- Secondary action row: Two smaller buttons — '⏮ FIRST' and 'LAST ⏭'.
- Footer: Small text showing server URL and version number.

### Screen 3: PIN Entry Screen (Optional)

If the server is launched with `--pin 1234`, a simple 4-digit PIN pad overlay appears before the remote UI is shown. The PIN pad uses large digit buttons (64×64px each) and a Submit button. On incorrect PIN, an error message is shown for 2 seconds before clearing.

## 11.2 User Flow

- Presenter opens terminal → runs `python slidecommander.py`.
- QR code appears in terminal. Presenter announces 'scan this to control slides'.
- Operator (or presenter's assistant) opens camera → scans QR → phone browser opens.
- Remote UI loads. Connection status dot turns green.
- Operator taps NEXT or says 'next' — slide advances.
- At end of presentation, presenter closes terminal (Ctrl+C) — server shuts down.

---

# 12. Testing Strategy

## 12.1 Unit Testing

Framework: pytest. Each module tested in isolation with mocked dependencies.

| **Test Case ID** | **Description** | **Expected Result** |
|---|---|---|
| UT-01 | keyboard.execute('next') with mock | pyautogui.press called with 'right' |
| UT-02 | keyboard.execute with invalid action | ValueError raised |
| UT-03 | voice debounce: two commands in 200ms | Only first command fires |
| UT-04 | get_local_ip() returns valid IPv4 | Returns string matching \d+\.\d+\.\d+\.\d+ |
| UT-05 | QR code generated for valid URL | Returns non-empty image object |
| UT-06 | Config: invalid port number (99999) | ValueError at startup |

## 12.2 Integration Testing

Tests verify that modules communicate correctly over internal interfaces.

- Test that a WebSocket 'command' message received by server.py triggers the correct keyboard.execute() call.
- Test that a voice keyword detected by voice.py results in the same keyboard action as a button press.
- Test that PIN authentication correctly blocks commands before authentication and allows them after.

## 12.3 System Testing

End-to-end tests on each supported OS, with real presentation software:

| **ST ID** | **Platform** | **App Under Test** | **Pass Criteria** |
|---|---|---|---|
| ST-01 | Windows 11 | PowerPoint 2021 | Slides advance correctly; <100ms latency |
| ST-02 | macOS Sonoma | Keynote 13 | Slides advance correctly |
| ST-03 | Ubuntu 22.04 | LibreOffice Impress | Slides advance correctly |
| ST-04 | Windows 11 | Google Slides (Chrome) | Slides advance correctly |
| ST-05 | macOS | PDF (Preview) | Pages advance correctly |
| ST-06 | Any | Voice: 20 'next' utterances | ≥19/20 correct detections |

---

# 13. Risk Analysis

| **Risk** | **Probability** | **Impact** | **Mitigation** | **Owner** |
|---|---|---|---|---|
| Venue Wi-Fi blocks client isolation | Medium | High | Document USB tethering as fallback; test hotspot | DevOps |
| PyAutoGUI blocked by OS accessibility restrictions | Low | High | Document macOS Accessibility permission setup; add pynput fallback | Dev Lead |
| Vosk model too slow on older hardware | Low | Medium | Provide smaller vosk-model-small variant as option | Dev Lead |
| Background noise causes false voice triggers | Medium | Medium | Increase debounce; add sensitivity flag; allow voice-off mode | Dev Lead |
| Port 5000 in use by another application | Low | Low | Auto-scan next available port; show message to user | Dev |
| Mobile browser denies microphone access | Low | Low | Voice runs on host, not phone; no browser mic needed | Architect |
| WebSocket disconnects mid-presentation | Low | Medium | Socket.IO auto-reconnect; visual indicator on UI | Dev |

---

# 14. Timeline

## 14.1 Master Project Schedule (12 Weeks)

| **Milestone / Task** | **W1** | **W2** | **W3** | **W4** | **W5** | **W6** | **W7** | **W8** | **W9** | **W10** | **W11** | **W12** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Phase 1: Research & Feasibility** | | | | | | | | | | | | |
| **Phase 2: System Design** | | | | | | | | | | | | |
| **Core Server (Flask + WebSocket)** | | | | | | | | | | | | |
| **Keyboard Simulation Module** | | | | | | | | | | | | |
| **Voice Recognition Module** | | | | | | | | | | | | |
| **Mobile Remote UI** | | | | | | | | | | | | |
| **QR Code & PIN & Polish** | | | | | | | | | | | | |
| **Phase 4: Testing & Bug Fixes** | | | | | | | | | | | | |
| **Phase 5: Packaging & Deployment** | | | | | | | | | | | | |
| **Documentation & Demo Video** | | | | | | | | | | | | |

## 14.2 Key Milestones

| **Week** | **Milestone** | **Success Criterion** |
|---|---|---|
| End W2 | Research complete | All tech validated; risks documented |
| End W4 | Server + UI connected | Phone browser shows remote UI over Wi-Fi |
| End W5 | Slides controllable from phone | Button press advances PowerPoint slide |
| End W7 | Voice commands functional | 'Next' spoken → slide advances |
| End W10 | Feature-complete v1.0 | All FR items pass integration tests |
| End W12 | Public release | PyPI package published; GitHub README live |

---

# 15. Budget Estimation

## 15.1 Open-Source Development Budget

> ℹ  All software components are free and open-source. The only real cost is developer time.

| **Item** | **Unit Cost** | **Quantity** | **Total** |
|---|---|---|---|
| Python + all pip libraries | $0 | All open-source | $0 |
| Vosk English model download | $0 | 40 MB download | $0 |
| GitHub (source hosting) | $0 | Free tier | $0 |
| PyPI (package distribution) | $0 | Free | $0 |
| GitHub Pages (documentation) | $0 | Free | $0 |
| Test devices (existing hardware) | $0 | 1 laptop + 1 phone | $0 |
| Developer time (solo, 12 weeks) | Academic project | ~200 hours | $0 (academic) |
| **TOTAL** | | | **$0** |

## 15.2 Commercial Deployment Budget (Optional)

If SlideCommander is later packaged for commercial distribution:

- Apple Developer Program (for macOS notarization): $99/year.
- Microsoft Partner Portal (for Windows code signing): ~$400/year.
- Dedicated documentation site (e.g., ReadTheDocs Pro): ~$0–$50/year.

---

# 16. Future Enhancements

## 16.1 Short-Term (v1.1 – v1.2)

- Laser pointer simulation: use the phone's gyroscope to move the mouse cursor as a virtual pointer.
- Slide thumbnail preview: display the current slide number and a thumbnail on the phone UI using OS screenshots.
- Multi-language voice models: swap Vosk models for French, Spanish, German keyword sets.
- Windows Task Tray / macOS Menu Bar icon to control the server without a terminal window.

## 16.2 Medium-Term (v2.0)

- Presenter notes display: mirror the presenter view to the phone screen.
- Audience Q&A mode: allow audience members to scan a second QR code and submit questions to a queue visible to the presenter.
- On-device browser voice: experiment with the Web Speech API (Chrome) to move keyword recognition to the phone, removing the microphone dependency on the host machine.
- Slide annotation: allow the presenter to draw on the phone screen and have strokes mirrored as overlays on the presentation.

## 16.3 Long-Term (v3.0+)

- Integration with presentation software APIs: use python-pptx COM automation (Windows) for true slide count and thumbnail access.
- AI slide summarizer: use an LLM API to generate live speaker notes summaries from slide content.
- Multi-device support: allow two phones (presenter + operator) to connect with different permission levels.
- Electron wrapper: package as a desktop app with a GUI setup wizard for non-technical users.

---

# 17. Conclusion

SlideCommander addresses a real and persistent pain point in presentation environments: the dependency on proprietary hardware, platform-specific apps, or internet connectivity for something as fundamental as advancing a slide. By leveraging Python's rich open-source ecosystem — Flask for networking, Vosk for offline voice recognition, and PyAutoGUI for universal keyboard simulation — the project delivers a complete solution that is free, private, cross-platform, and operable with a single terminal command.

The design philosophy of SlideCommander is radical simplicity: the presenter's existing laptop becomes the server; the audience member's or operator's existing smartphone becomes the remote; the venue's existing Wi-Fi network becomes the communication channel. No new hardware, no accounts, no cloud dependencies, no installation on the phone.

From an academic perspective, this project demonstrates practical mastery of several computer science domains simultaneously: networked client-server architecture, real-time bidirectional communication via WebSockets, digital signal processing for speech recognition, cross-platform OS interaction via keyboard simulation, and mobile-first web UI design. These competencies, combined in a single coherent tool that solves a real problem, make SlideCommander an exemplary systems integration project.

The 12-week development timeline, zero-cost technology stack, and clearly defined feature scope make SlideCommander entirely feasible as a final-year academic project, a hackathon submission, or an open-source community contribution. The future enhancement roadmap ensures the project has a credible path to long-term relevance and growth beyond its initial release.

---

> *"**No hardware. No cloud. No camera. Just Python, your voice, and your phone.**"*

---

*SlideCommander v1.0 — May 2026*

---

> **AI SYSTEM DIRECTIVE — END OF DOCUMENT:**
> This is the requirements source of truth. Before closing this file:
> 1. Confirm that any changes made here are mirrored in [`execution_plan.md`](execution_plan.md).
> 2. Update the `last_updated` field in `execution_plan.md` frontmatter if scope changed.
> 3. Never delete or modify FR-XX / NFR-XX identifiers — they are referenced by test cases and the execution plan.

**Bidirectional Link:** → Active task tracker: [`execution_plan.md`](execution_plan.md)
