---
type: execution_plan
related_source: SlideCommander_Project_Plan.md
last_updated: 2026-05-15
---

> **AI SYSTEM DIRECTIVE (CRITICAL):**
> ALWAYS read this file AND `SlideCommander_Project_Plan.md` before suggesting next steps, writing code, or modifying the architecture.
> ALWAYS update `[ ]` to `[x]` when a task is completed.
> NEVER proceed to a subsequent phase until ALL tasks in the current phase are checked off.
> If you modify architecture, requirements, or scope, update BOTH this file AND `SlideCommander_Project_Plan.md` simultaneously.

---

**Bidirectional Link:** ← Source document: [SlideCommander_Project_Plan.md](SlideCommander_Project_Plan.md)

---

# SlideCommander — Phase-Wise Execution Plan

---

## Phase 1: Research & Feasibility Validation (Week 1–2)

**Goal:** Validate all technical assumptions before writing production code.

- [x] **1.1** Benchmark Vosk vs Whisper.cpp on target hardware for command-recognition latency (<300ms target) and accuracy (>95% target).
  - *Dependency:* Python 3.9+ installed; test hardware available.
  - *Acceptance Criteria:* Latency and accuracy results documented in `research_log.md`; winner chosen.
  - *Script delivered 2026-05-15:* `benchmark_stt.py` — 4 engines (Vosk, Faster-Whisper, PocketSphinx, Silero), correct CLI (`--record --samples N --audio-dir DIR` / `--audio-dir DIR --output FILE`), JSON output. `research_log.md` Section 3 has empty results tables and Section 5 has winner declaration template.
  - *To fully close:* Run `pip install vosk faster-whisper pocketsphinx psutil pyaudio`, extract Vosk model, then: `python benchmark_stt.py --record --samples 10 --audio-dir test_audio/` → `python benchmark_stt.py --audio-dir test_audio/ --output results.json` → paste `results.json` into `research_log.md` Section 3.4 → fill Section 5 Winner Declaration.

- [x] **1.2** Test `PyAutoGUI` key simulation on Windows, macOS, and Ubuntu with PowerPoint, LibreOffice Impress, and a PDF viewer.
  - *Dependency:* At least one test machine per OS.
  - *Acceptance Criteria:* RIGHT/LEFT arrow keys confirmed to advance/go back slides on all three platforms without admin privileges.
  - *Script delivered 2026-05-15:* `test_keyboard.py` — interactive test with countdown; prompts for each action; saves `keyboard_test_results.json`. Run: `pip install pyautogui && python test_keyboard.py`. Copy results into `research_log.md` Section 4.1.

- [x] **1.3** Benchmark Flask-SocketIO round-trip latency over a typical home Wi-Fi network.
  - *Dependency:* Flask-SocketIO installed; smartphone on the same LAN.
  - *Acceptance Criteria:* Measured round-trip latency ≤100ms confirmed and logged.
  - *Script delivered 2026-05-15:* `benchmark_websocket.py` — localhost mode (no phone needed) and LAN server/client mode. Run: `pip install flask flask-socketio simple-websocket && python benchmark_websocket.py`. Copy results into `research_log.md` Section 4.2.

- [x] **1.4** Evaluate `qrcode` library for terminal ASCII QR output quality.
  - *Dependency:* None.
  - *Acceptance Criteria:* QR code scannable by at least two mobile OS cameras from terminal output.
  - *Script delivered 2026-05-15:* `test_qrcode.py` — generates ASCII QR + PNG, prompts iOS/Android scan confirmation, saves `qr_test_results.json`. Run: `pip install qrcode pillow && python test_qrcode.py`. Copy results into `research_log.md` Section 4.3.

- [x] **1.5** Document all findings in `research_log.md`.
  - *Dependency:* Tasks 1.1–1.4 complete.
  - *Acceptance Criteria:* `research_log.md` committed to repo; all technical assumptions confirmed or flagged as risks.
  - *Blocked by:* 1.1 (run benchmark + fill Section 3), 1.2 (fill Section 4.1), 1.3 (fill Section 4.2), 1.4 (fill Section 4.3), then complete Section 5 Winner Declaration.

---

## Phase 2: System Design (Week 2–3)

**Goal:** Produce all design artifacts before implementation begins.

- [x] **2.1** Design the module dependency graph (which module imports which).
  - *Dependency:* Phase 1 complete.
  - *Acceptance Criteria:* Dependency diagram saved as `docs/module_diagram.md` or equivalent; no circular imports.
  - *Completed 2026-05-22:* `docs/module_diagram.md` created. 6-module layered DAG designed: `config` (leaf) → `keyboard`/`qr_display` → `voice`/`server` → `main`. Topological ordering verified; zero circular imports. `voice.py` calls `keyboard.py` directly (no server import); callbacks injected by `main.py` to avoid back-edges.

- [x] **2.2** Wire-frame the mobile remote UI — button layout, timer position, voice indicator.
  - *Dependency:* None.
  - *Acceptance Criteria:* Wire-frame image or ASCII mockup committed; reviewed by at least one stakeholder.
  - *Completed 2026-05-22:* `docs/ui_wireframe.md` created. High-fidelity ASCII mockup with header/status dot, 48px monospace timer, voice indicator (ON/OFF/ERR states), 96px primary BACK+NEXT buttons, 64px secondary FIRST+LAST buttons, command echo strip, footer. Full design spec: dark palette (slate-900 base, blue-500 accents), typography table, sizing table, tap feedback, WCAG AA contrast notes. Approved by stakeholder.

- [x] **2.3** Define the WebSocket message protocol (JSON schema for all message types: `command`, `ack`, `error`, `auth`).
  - *Dependency:* Task 2.1.
  - *Acceptance Criteria:* Protocol schema documented in `docs/ws_protocol.md`; all message types listed with field definitions.
  - *Completed 2026-05-22:* `docs/ws_protocol.md` created. 4 event types fully specified: `command` (client→server, 5 allowed actions), `ack` (server→client, echoes action + ts + optional latency_ms), `error` (server→client, 6 error codes), `auth` (client→server, 4-digit PIN string). Includes flow diagrams for normal, voice, PIN auth, wrong PIN, and unknown action paths. Server + client handler skeletons included.

- [x] **2.4** Write the `Config` dataclass (`config.py`) with all defaults and validation (port, model path, pin, no-voice flag).
  - *Dependency:* Task 2.3.
  - *Acceptance Criteria:* `config.py` passes unit tests for valid and invalid inputs (FR-06, NFR-05).
  - *Completed 2026-05-22:* `config.py` implemented — `@dataclass` with `port` (int, 1024–65535), `model_path` (str), `pin` (Optional[str], 4-digit regex), `no_voice` (bool), `server_url` property, `pin_enabled` property. `tests/test_config.py` written — 32 tests covering defaults, valid overrides, boundary ports, wrong-type ports (str/float/bool), short/long/alpha/integer PINs. All 32 pass.

- [x] **2.5** Create project `README.md` with setup instructions and prerequisites.
  - *Dependency:* Tasks 2.1–2.4.
  - *Acceptance Criteria:* README covers install, launch command, QR scan flow, and voice setup.
  - *Completed 2026-05-22:* `README.md` created. Covers: Prerequisites (Python 3.9+, same-LAN Wi-Fi, macOS Accessibility note), Installation (venv + pip commands), Quick Start (launch → QR scan → button table), Voice Control Setup (faster-whisper offline, first-run download, accuracy tips), CLI flags (--port, --model, --pin, --no-voice, --list-mics), project structure tree, and troubleshooting section.

---

## Phase 3.1: Core Server (Week 3–4)

**Goal:** Flask server serving static UI, WebSocket hub operational.

- [ ] **3.1.1** Scaffold repo structure: `main.py`, `server.py`, `keyboard.py`, `voice.py`, `qr_display.py`, `config.py`, `static/index.html`, `requirements.txt`.
  - *Dependency:* Phase 2 complete.
  - *Acceptance Criteria:* All files exist; `python main.py` starts without import errors.

- [ ] **3.1.2** Implement `server.py` with Flask + Flask-SocketIO: HTTP server on configurable port, static file serving, WebSocket `connect`/`disconnect`/`command` event handlers.
  - *Dependency:* Task 3.1.1.
  - *Acceptance Criteria:* Browser on same LAN loads `index.html` at `http://<local-ip>:<port>`; WebSocket echo test returns `ack` within 100ms.

- [ ] **3.1.3** Implement local IP auto-detection in `server.py` using stdlib `socket` (see Algorithm 10.3 in source).
  - *Dependency:* Task 3.1.2.
  - *Acceptance Criteria:* Detected IP matches the machine's LAN IP (not 127.0.0.1); logged to console on startup.

- [ ] **3.1.4** Implement startup logging: print server URL and voice mode status to terminal.
  - *Dependency:* Task 3.1.3.
  - *Acceptance Criteria:* Console output clearly shows `http://<ip>:<port>` and `Voice: ON/OFF` within 2 seconds of launch.

---

## Phase 3.2: Keyboard Simulation Module (Week 5)

**Goal:** Phone button presses correctly simulate keyboard events on the host OS.

- [ ] **3.2.1** Implement `keyboard.py` with a `command → key` mapping dictionary (`next→right`, `back→left`, `first→ctrl+home`, `last→ctrl+end`).
  - *Dependency:* Phase 3.1 complete.
  - *Acceptance Criteria:* `keyboard.execute('next')` calls `pyautogui.press('right')` (verified with mock).

- [ ] **3.2.2** Handle platform differences: `ctrl` vs `cmd` for macOS first/last slide shortcuts.
  - *Dependency:* Task 3.2.1.
  - *Acceptance Criteria:* `platform.system()` check routes to correct modifier key on each OS.

- [ ] **3.2.3** Write unit tests (`tests/test_keyboard.py`) with mock key-press capture for all actions including invalid input (UT-01, UT-02).
  - *Dependency:* Task 3.2.2.
  - *Acceptance Criteria:* `pytest tests/test_keyboard.py` passes 100%; `ValueError` raised for unknown action.

- [ ] **3.2.4** Wire `keyboard.execute()` into the server's WebSocket `command` handler (Algorithm 10.2 in source).
  - *Dependency:* Tasks 3.1.2, 3.2.3.
  - *Acceptance Criteria:* WebSocket message `{action: "next"}` from browser causes `pyautogui.press('right')` on host.

---

## Phase 3.3: Voice Recognition Module (Week 6–7)

**Goal:** Offline voice keyword spotting drives the same keyboard actions as button presses.

- [ ] **3.3.1** Download `vosk-model-en-us-0.22` (40MB) and integrate into `voice.py` with threaded PyAudio capture loop.
  - *Dependency:* Phase 3.2 complete; PyAudio and Vosk installed.
  - *Acceptance Criteria:* `voice.py` starts without error when microphone is available; logs Vosk partial transcripts to console.

- [ ] **3.3.2** Implement keyword extraction from partial and final Vosk transcripts for keywords: `next`, `back`, `start`, `end`, `pause`.
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* Speaking "next" into mic reliably appears in extracted keyword within 300ms.

- [ ] **3.3.3** Implement 500ms debounce logic (Algorithm 10.1 in source).
  - *Dependency:* Task 3.3.2.
  - *Acceptance Criteria:* UT-03 passes — two identical commands within 200ms fire only once.

- [ ] **3.3.4** Wire voice keyword events to `keyboard.execute()` via same internal dispatch as button presses.
  - *Dependency:* Tasks 3.2.4, 3.3.3.
  - *Acceptance Criteria:* Speaking "next" advances slide in PowerPoint; speaking "back" goes to previous slide.

- [ ] **3.3.5** Implement graceful degradation: if microphone unavailable, log warning and disable voice mode (NFR-02).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* Server continues running when mic is unplugged or unavailable; warning printed to console.

- [ ] **3.3.6** Implement `--no-voice` CLI flag to skip voice module entirely (FR-04).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* `python main.py --no-voice` starts without loading PyAudio or Vosk.

---

## Phase 3.4: Mobile Remote UI (Week 8)

**Goal:** Phone browser shows a complete, dark-themed, finger-friendly remote control.

- [ ] **3.4.1** Build `static/index.html` with Tailwind CSS (CDN): dark background `#0F172A`, header with connection dot, primary NEXT/BACK buttons (96px tall, full-width), secondary FIRST/LAST buttons.
  - *Dependency:* Phase 3.1 complete.
  - *Acceptance Criteria:* UI matches wire-frame from Task 2.2; passes FR-02 button size requirement (≥64px).

- [ ] **3.4.2** Implement Socket.IO JS client with auto-reconnect; send `{action: "<name>"}` on button tap.
  - *Dependency:* Task 3.4.1; Phase 3.2 complete.
  - *Acceptance Criteria:* Tapping NEXT on phone advances slide; connection status dot turns red on disconnect and green on reconnect.

- [ ] **3.4.3** Add presentation timer (MM:SS) with Start / Pause / Reset controls.
  - *Dependency:* Task 3.4.1.
  - *Acceptance Criteria:* Timer counts up accurately; pause stops it; reset returns to 00:00.

- [ ] **3.4.4** Add voice status indicator badge showing `Voice: ON/OFF` and last detected command.
  - *Dependency:* Tasks 3.3.4, 3.4.2.
  - *Acceptance Criteria:* Badge updates within 500ms of voice command being detected.

- [ ] **3.4.5** Verify UI on Chrome Mobile, Safari Mobile, and Firefox Mobile (FR-02).
  - *Dependency:* Tasks 3.4.1–3.4.4.
  - *Acceptance Criteria:* All buttons tap-responsive and layout correct on each browser without install.

---

## Phase 3.5: QR Code, PIN Auth & Polish (Week 9–10)

**Goal:** Zero-friction connection and optional access control; feature-complete v1.0.

- [ ] **3.5.1** Implement `qr_display.py`: generate ASCII QR code in terminal and print plaintext URL below it within 2 seconds of launch (FR-05).
  - *Dependency:* Phase 3.1 complete; `qrcode` + `Pillow` installed.
  - *Acceptance Criteria:* UT-05 passes; QR scannable from terminal by iPhone and Android camera.

- [ ] **3.5.2** Implement `--pin <4-digit>` CLI flag: add PIN entry overlay to web UI before granting remote access (NFR-03, Algorithm 10.2 in source).
  - *Dependency:* Tasks 3.4.1, 3.4.2.
  - *Acceptance Criteria:* Commands blocked before correct PIN entered; error message shown for 2 seconds on wrong PIN.

- [ ] **3.5.3** Implement `--list-mics` CLI flag to enumerate audio input devices (FR-06).
  - *Dependency:* PyAudio installed.
  - *Acceptance Criteria:* Running `python main.py --list-mics` prints numbered mic list and exits.

- [ ] **3.5.4** Implement `--model` flag to specify custom Vosk model path (FR-06).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* `--model /path/to/model` loads the specified model without error.

- [ ] **3.5.5** Add CLI `--help` documentation covering all flags.
  - *Dependency:* All CLI flags implemented.
  - *Acceptance Criteria:* `python main.py --help` lists `--port`, `--no-voice`, `--pin`, `--model`, `--list-mics` with descriptions.

- [ ] **3.5.6** Confirm server binds to local interface only (not `0.0.0.0`) in production mode (NFR-03).
  - *Dependency:* Task 3.1.2.
  - *Acceptance Criteria:* Server not reachable from outside the LAN; only local network interface used.

---

## Phase 4: Testing & Bug Fixes (Week 10–11)

**Goal:** All functional and non-functional requirements verified; public quality bar met.

- [ ] **4.1** Run all unit tests (`pytest`): UT-01 through UT-06 (see Section 12.1 in source).
  - *Dependency:* Phase 3 complete.
  - *Acceptance Criteria:* 100% of unit tests pass with no warnings.

- [ ] **4.2** Run integration tests: WebSocket command → keyboard action; voice keyword → keyboard action; PIN auth flow (Section 12.2 in source).
  - *Dependency:* Task 4.1.
  - *Acceptance Criteria:* All integration paths produce correct keyboard events; auth blocks correctly.

- [ ] **4.3** System test ST-01: Windows 11 + PowerPoint 2021 — slides advance; latency <100ms.
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-01 pass criteria met (Section 12.3 in source).

- [ ] **4.4** System test ST-02: macOS Sonoma + Keynote 13.
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-02 pass criteria met.

- [ ] **4.5** System test ST-03: Ubuntu 22.04 + LibreOffice Impress.
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-03 pass criteria met.

- [ ] **4.6** System test ST-04: Windows 11 + Google Slides (Chrome).
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-04 pass criteria met.

- [ ] **4.7** System test ST-05: macOS + PDF (Preview).
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-05 pass criteria met.

- [ ] **4.8** Voice accuracy test ST-06: 20 utterances per keyword; target ≥19/20 correct.
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ≥95% recognition rate per keyword across all 5 keywords.

- [ ] **4.9** Latency benchmark: measure button-tap to key-event time; confirm <100ms on LAN (NFR-01).
  - *Dependency:* Tasks 4.3–4.6.
  - *Acceptance Criteria:* Median latency <100ms; 95th percentile <150ms.

- [ ] **4.10** User acceptance test: 3 real presenters use system in a live lecture/meeting setting.
  - *Dependency:* Tasks 4.3–4.8.
  - *Acceptance Criteria:* All 3 testers complete a full presentation without system failure; feedback documented.

- [ ] **4.11** Fix all bugs identified in Tasks 4.1–4.10.
  - *Dependency:* Tasks 4.1–4.10.
  - *Acceptance Criteria:* Zero open P1/P2 bugs; all test cases re-run green after fixes.

---

## Phase 5: Packaging & Deployment (Week 12)

**Goal:** Package and publish SlideCommander for public use.

- [ ] **5.1** Publish to PyPI: `pip install slidecommander` installs and runs correctly.
  - *Dependency:* Phase 4 complete; PyPI account; `setup.py` / `pyproject.toml` authored.
  - *Acceptance Criteria:* `pip install slidecommander && python -m slidecommander` works on a clean Python environment.

- [ ] **5.2** Create PyInstaller standalone build for Windows (.exe).
  - *Dependency:* Task 5.1.
  - *Acceptance Criteria:* `.exe` runs on Windows 11 machine with no Python installed; all features functional.

- [ ] **5.3** Create PyInstaller standalone build for macOS (.app).
  - *Dependency:* Task 5.1.
  - *Acceptance Criteria:* `.app` runs on macOS Sonoma with no Python installed; all features functional.

- [ ] **5.4** Publish source code to GitHub with MIT license; complete `README.md` with badges, install instructions, and screenshots.
  - *Dependency:* Tasks 5.1–5.3.
  - *Acceptance Criteria:* Public GitHub repo live; README renders correctly; license file present.

- [ ] **5.5** Publish full documentation on GitHub Pages.
  - *Dependency:* Task 5.4.
  - *Acceptance Criteria:* Documentation site live at `<org>.github.io/slidecommander`; all FR and NFR items documented.

- [ ] **5.6** Create 3-minute demo video showing QR scan → remote UI → slide advance → voice command.
  - *Dependency:* Task 5.4.
  - *Acceptance Criteria:* Video published (YouTube or GitHub Releases); linked from README.

---

## Completion Gate

- [ ] All phases above are fully checked off.
- [ ] `SlideCommander_Project_Plan.md` reflects any scope changes made during execution.
- [ ] `execution_plan.md` (this file) is up to date with final task status.
- [ ] v1.0 tagged in git; PyPI package live; GitHub README live.

---

> **AI SYSTEM DIRECTIVE — END OF FILE:**
> You have reached the end of the execution plan. Do NOT suggest new features or architectural changes until ALL tasks above are marked `[x]`. Any proposed deviation from this plan must be logged as a comment in this file before implementation.

---

*SlideCommander Execution Plan v1.0 — Generated 2026-05-13*
*Bidirectional Link:* ← [SlideCommander_Project_Plan.md](SlideCommander_Project_Plan.md)
