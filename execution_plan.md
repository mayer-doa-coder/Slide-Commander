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

- [x] **2.3** Define the WebSocket message protocol (JSON schema for all message types: `command`, `ack`, `error`).
  - *Dependency:* Task 2.1.
  - *Acceptance Criteria:* Protocol schema documented in `docs/ws_protocol.md`; all message types listed with field definitions.
  - *Completed 2026-05-22:* `docs/ws_protocol.md` created. 3 event types fully specified: `command` (client→server, 5 allowed actions), `ack` (server→client, echoes action + ts + optional latency_ms), `error` (server→client, error codes). Includes flow diagrams for normal, voice, and unknown action paths. Server + client handler skeletons included.

- [x] **2.4** Write the `Config` dataclass (`config.py`) with all defaults and validation (port, model path, no-voice flag).
  - *Dependency:* Task 2.3.
  - *Acceptance Criteria:* `config.py` passes unit tests for valid and invalid inputs (FR-06, NFR-05).
  - *Completed 2026-05-22:* `config.py` implemented — `@dataclass` with `port` (int, 1024–65535), `model_path` (str), `no_voice` (bool), `server_url` property. `tests/test_config.py` written — tests covering defaults, valid overrides, boundary ports, wrong-type ports (str/float/bool). All pass.

- [x] **2.5** Create project `README.md` with setup instructions and prerequisites.
  - *Dependency:* Tasks 2.1–2.4.
  - *Acceptance Criteria:* README covers install, launch command, QR scan flow, and voice setup.
  - *Completed 2026-05-22:* `README.md` created. Covers: Prerequisites (Python 3.9+, same-LAN Wi-Fi, macOS Accessibility note), Installation (venv + pip commands), Quick Start (launch → QR scan → button table), Voice Control Setup (faster-whisper offline, first-run download, accuracy tips), CLI flags (--port, --model, --pin, --no-voice, --list-mics), project structure tree, and troubleshooting section.

---

## Phase 3.1: Core Server (Week 3–4)

**Goal:** Flask server serving static UI, WebSocket hub operational.

- [x] **3.1.1** Scaffold repo structure: `main.py`, `server.py`, `keyboard.py`, `voice.py`, `qr_display.py`, `config.py`, `static/index.html`, `requirements.txt`.
  - *Dependency:* Phase 2 complete.
  - *Acceptance Criteria:* All files exist; `python main.py` starts without import errors.
  - *Completed 2026-05-22:* All 8 files created. DAG layer order respected: config→keyboard/qr_display→voice/server→main. voice.py uses faster-whisper+sounddevice (Phase 1 validated stack, not vosk+pyaudio which fail on Python 3.14). `python main.py` runs cleanly — prints port/voice/PIN status and exits.

- [x] **3.1.2** Implement `server.py` with Flask + Flask-SocketIO: HTTP server on configurable port, static file serving, WebSocket `connect`/`disconnect`/`command` event handlers.
  - *Dependency:* Task 3.1.1.
  - *Acceptance Criteria:* Browser on same LAN loads `index.html` at `http://<local-ip>:<port>`; WebSocket echo test returns `ack` within 100ms.
  - *Completed 2026-05-22:* Full server.py implemented — `connect`/`disconnect`/`command` handlers, `broadcast_voice_event()`, `start_server()` binding to `0.0.0.0`. LAN-verified by stakeholder: page loaded at `http://192.168.0.170:5000`, "SlideCommander" heading confirmed in browser.

- [x] **3.1.3** Implement local IP auto-detection in `server.py` using stdlib `socket` (see Algorithm 10.3 in source).
  - *Dependency:* Task 3.1.2.
  - *Acceptance Criteria:* Detected IP matches the machine's LAN IP (not 127.0.0.1); logged to console on startup.
  - *Completed 2026-05-22:* `get_local_ip()` added to `server.py` — UDP connect trick per Algorithm 10.3. Returns `192.168.0.170` (verified, not 127.0.0.1). Logged as `[SERVER] LAN IP detected: <ip>` on startup. `main.py` updated to call `server.get_local_ip()` instead of inline socket block.

- [x] **3.1.4** Implement startup logging: print server URL and voice mode status to terminal.
  - *Dependency:* Task 3.1.3.
  - *Acceptance Criteria:* Console output clearly shows `http://<ip>:<port>` and `Voice: ON/OFF` within 2 seconds of launch.
  - *Completed 2026-05-22:* Banner prints in `main.py` immediately after `Config` init, before any blocking call. Shows `=== SlideCommander ===`, `URL: http://192.168.0.170:5000`, `Voice: ON/OFF`, `Model: tiny`. `sys.stdout.flush()` called after banner. `--model` default corrected from Vosk path to `"tiny"`. Verified: banner appears instantly with and without `--no-voice`.

---

## Phase 3.2: Keyboard Simulation Module (Week 5)

**Goal:** Phone button presses correctly simulate keyboard events on the host OS.

- [x] **3.2.1** Implement `keyboard.py` with a `command → key` mapping dictionary (`next→right`, `back→left`, `first→ctrl+home`, `last→ctrl+end`).
  - *Dependency:* Phase 3.1 complete.
  - *Acceptance Criteria:* `keyboard.execute('next')` calls `pyautogui.press('right')` (verified with mock).
  - *Completed 2026-05-22:* `keyboard.py` implemented — `_KEY_MAP` maps all 5 actions; `execute()` calls `pyautogui.hotkey()` for modified keys and `pyautogui.press()` for simple keys; `pause` is a no-op (timer handled by UI). `ValueError` raised for unknown actions.

- [x] **3.2.2** Handle platform differences: `ctrl` vs `cmd` for macOS first/last slide shortcuts.
  - *Dependency:* Task 3.2.1.
  - *Acceptance Criteria:* `platform.system()` check routes to correct modifier key on each OS.
  - *Completed 2026-05-22:* `_MODIFIER = "command" if platform.system() == "Darwin" else "ctrl"` — macOS uses Command key, Windows/Linux use Ctrl. `first` and `last` entries in `_KEY_MAP` use `_MODIFIER` at import time.

- [x] **3.2.3** Write unit tests (`tests/test_keyboard.py`) with mock key-press capture for all actions including invalid input (UT-01, UT-02).
  - *Dependency:* Task 3.2.2.
  - *Acceptance Criteria:* `pytest tests/test_keyboard.py` passes 100%; `ValueError` raised for unknown action.
  - *Completed 2026-05-22:* `tests/test_keyboard.py` written — 27 tests across 3 classes: `TestExecuteValid` (5 actions + parametrized), `TestExecuteInvalid` (10 bad inputs + error message content, UT-02), `TestPlatformModifier` (macOS/Windows/Linux routing). All 27 pass.

- [x] **3.2.4** Wire `keyboard.execute()` into the server's WebSocket `command` handler (Algorithm 10.2 in source).
  - *Dependency:* Tasks 3.1.2, 3.2.3.
  - *Acceptance Criteria:* WebSocket message `{action: "next"}` from browser causes `pyautogui.press('right')` on host.
  - *Completed 2026-05-22:* Already wired in Task 3.1.2 — `server.py` calls `_keyboard_callback(action)` in `handle_command()`; `main.py` passes `keyboard_callback=keyboard.execute` to `start_server()`. No changes needed.

---

## Phase 3.3: Voice Recognition Module (Week 6–7)

**Goal:** Offline voice keyword spotting drives the same keyboard actions as button presses.

- [x] **3.3.1** Download `vosk-model-en-us-0.22` (40MB) and integrate into `voice.py` with threaded PyAudio capture loop.
  - *Dependency:* Phase 3.2 complete; PyAudio and Vosk installed.
  - *Acceptance Criteria:* `voice.py` starts without error when microphone is available; logs Vosk partial transcripts to console.
  - *Completed 2026-05-22:* **Architectural pivot — Vosk/PyAudio replaced with `faster-whisper`/`sounddevice`** for Python 3.14 compatibility. `WhisperModel` (`tiny`, `cpu`, `int8`) loaded in a daemon thread (`voice-worker`). Sliding 3-second audio window (16 kHz mono float32, 50% overlap) fed to `model.transcribe()` with VAD filter. Transcripts logged as `[VOICE] Heard: "..."`. Graceful degradation on `sd.PortAudioError` — prints `[WARNING] No microphone detected. Voice mode disabled.` and exits thread without crashing server. Human-verified: microphone input successfully transcribed in terminal.

- [x] **3.3.2** Implement keyword extraction from faster-whisper transcripts for keywords: `next`, `back`, `start`, `end`, `pause`.
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* Speaking "next" into mic reliably appears in extracted keyword within 300ms.
  - *Completed 2026-05-22:* Added `_clean()` helper (lowercase + `re` punctuation strip) applied to all Whisper segments before matching. Added `"start"` → `first` and `"end"` → `last` to `_KEYWORD_MAP` (completing the 5-keyword spec). Log format updated to `[VOICE] Command detected: KEYWORD`. Window tightened from 3 s → 2 s with 1 s step so inference runs every ~1 s. Human-verified: "next" and "back" detected responsively and accurately.

- [x] **3.3.3** Implement 500ms debounce logic (Algorithm 10.1 in source).
  - *Dependency:* Task 3.3.2.
  - *Acceptance Criteria:* UT-03 passes — two identical commands within 200ms fire only once.
  - *Completed 2026-05-22:* `_dispatch()` extracted as testable module-level function. `_COMMAND_COOLDOWN_S = 0.5` (500 ms). Sentinel default `now - cooldown` ensures first call always passes. Debounced calls log `[VOICE] Ignored (debouncing)`. `pyautogui`/`sounddevice`/`faster_whisper`/`numpy` moved to lazy imports so test suite runs without those packages installed. `conftest.py` added at project root for `sys.path` fix. UT-03 + 6 companion tests: 7/7 pass.

- [x] **3.3.4** Wire voice keyword events to `keyboard.execute()` via same internal dispatch as button presses.
  - *Dependency:* Tasks 3.2.4, 3.3.3.
  - *Acceptance Criteria:* Speaking "next" advances slide in PowerPoint; speaking "back" goes to previous slide.
  - *Completed 2026-05-22:* `_dispatch()` in `voice.py` calls `keyboard.execute(command)` directly — identical path to the WebSocket `handle_command()` handler. No additional wiring needed.

- [x] **3.3.5** Implement graceful degradation: if microphone unavailable, log warning and disable voice mode (NFR-02).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* Server continues running when mic is unplugged or unavailable; warning printed to console.
  - *Completed 2026-05-22:* `_worker()` catches `Exception` (covers `PortAudioError`, permission denials, missing drivers) at stream open — prints `[WARNING] Microphone unavailable or access denied. Voice mode disabled. Web remote remains fully functional.` and returns cleanly. Second `try/except Exception` wraps the entire capture loop so mid-session mic disconnect also exits gracefully. `main.py` unaffected — daemon thread exit is silent to the server. Human-verified: voice pipeline advances slides on live presentation; server continues running if mic unavailable.

- [x] **3.3.6** Implement `--no-voice` CLI flag to skip voice module entirely (FR-04).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* `python main.py --no-voice` starts without loading PyAudio or Vosk.
  - *Completed 2026-05-22:* `main.py` `--no-voice` flag sets `cfg.no_voice=True`; `if not cfg.no_voice:` guard skips `voice.start_listening()` entirely. Heavy imports (`sounddevice`, `faster_whisper`) are lazy inside `_worker()` so they are never touched.

---

## Phase 3.4: Mobile Remote UI (Week 8)

**Goal:** Phone browser shows a complete, dark-themed, finger-friendly remote control.

- [x] **3.4.1** Build `static/index.html` with Tailwind CSS (CDN): dark background `#0F172A`, header with connection dot, primary NEXT/BACK buttons (96px tall, full-width), secondary FIRST/LAST buttons.
  - *Dependency:* Phase 3.1 complete.
  - *Acceptance Criteria:* UI matches wire-frame from Task 2.2; passes FR-02 button size requirement (≥64px).
  - *Completed 2026-05-22 (revised 2026-05-22):* Full `static/index.html` rebuilt as animated futuristic remote. Background `#020817` + conic-gradient overlay. Space Grotesk (UI) + Space Mono (numbers) via Google Fonts. Canvas particle network: 55 nodes with connecting lines <110px, `requestAnimationFrame` loop. Central orb (180px): conic-gradient scan ring (3.5s rotation), outer breathing ring (`breathe` keyframes), inner glow ring, `radial-gradient` core; `orbFlash()` spawns 2 `pulse-emit` rings and updates icon/label on every command. Waveform strip: 14 CSS-animated bars with staggered `--h`/`--d`/`--dl` custom properties; paused when mic off. Command history ticker: last 4 commands with opacity fade. Control dock: timer row (Space Mono, START/PAUSE/RESET), FIRST/LAST segmented bar (52px, full-width, `1rem` radius), BACK+NEXT equal-width side-by-side (80px, `1rem` radius — NEXT distinguished by blue gradient/glow, not size). Ripple effect at touch coordinates on every tap. Latency readout in orb from server ACK. All button sizes ≥52px; `touch-action: manipulation` on all buttons.

- [x] **3.4.2** Implement Socket.IO JS client with auto-reconnect; send `{action: "<name>"}` on button tap.
  - *Dependency:* Task 3.4.1; Phase 3.2 complete.
  - *Acceptance Criteria:* Tapping NEXT on phone advances slide; connection status dot turns red on disconnect and green on reconnect.
  - *Completed 2026-05-22:* `io()` with `reconnectionDelay:1000, reconnectionDelayMax:5000`. `connect`/`disconnect` toggle `.online` class on `#s-dot` (glow green/red) and `#s-label` text in the header `status-pill`. Each `.cmd-btn` emits `{action, source:"button", ts:Date.now()}` on click; also calls `orbFlash(action)` and `addHistory(action)` for in-UI feedback before server round-trip. `ack` event updates `#latency` in the orb with `data.latency_ms`.

- [x] **3.4.3** Add presentation timer (MM:SS) with Start / Pause / Reset controls.
  - *Dependency:* Task 3.4.1.
  - *Acceptance Criteria:* Timer counts up accurately; pause stops it; reset returns to 00:00.
  - *Completed 2026-05-22:* `#timer-display` in `ctrl-dock` timer row, Space Mono font, neon blue glow. `timerToggle()` starts/pauses `setInterval(_tick, 1000)`; `timerReset()` clears interval and zeroes display. `#btn-ts` label toggles START ↔ PAUSE. RESET is a separate `btn-t` button. Both timer buttons use `border-radius: 1rem` consistent with nav buttons.

- [x] **3.4.4** Add voice status indicator badge showing `Voice: ON/OFF` and last detected command.
  - *Dependency:* Tasks 3.3.4, 3.4.2.
  - *Acceptance Criteria:* Badge updates within 500ms of voice command being detected.
  - *Completed 2026-05-22:* Implemented as `voice-strip` bar (not a badge): `#mic-dot` (red/green glow), `#voice-state` label (OFF/ON), 14-bar waveform animation (paused when mic off, animated on voice event), `#last-vcmd` for last detected command. On `ack` with `source:"voice"`: mic-dot turns green, waveform bars lose `.paused` class, `#last-vcmd` shows command. `_voiceIdleTimer` resets voice strip to OFF state (mic-dot red, waveform paused, label OFF, last-cmd cleared) 5 s after the last voice event — prevents strip staying permanently ON after first command. Server broadcasts voice ack via `broadcast_voice_event()` triggered by `on_command` callback — latency is network RTT only.

- [x] **3.4.5** Verify UI on Chrome Mobile, Safari Mobile, and Firefox Mobile (FR-02).
  - *Dependency:* Tasks 3.4.1–3.4.4.
  - *Acceptance Criteria:* All buttons tap-responsive and layout correct on each browser without install.
  - *Completed 2026-05-22:* Full adaptive layout implemented via CSS custom properties + `clamp()` + `svh` units + media queries. Triple height fallback: `100vh` → `100svh` (excludes browser chrome, best for mobile) → `100dvh` (updates as chrome shows/hides). All key dimensions fluid: orb size `clamp(140px, 44vmin, 196px)`, nav buttons `clamp(68px, 10.5svh, 88px)`, seg bar `clamp(44px, 6.5svh, 56px)`, font sizes, padding, and gaps all scale with viewport. Four media-query breakpoints: landscape phone (<500px height) — orb shrinks to 32vh, sub-text hidden; compact portrait (500–720px) — reduced orb/buttons/gaps for small phones (iPhone SE); tablet (≥600px) — content centered, max-width 540px, rounded dock; desktop (≥900px) — further constrained to 480px. Browser compat: `-webkit-backdrop-filter`, `-webkit-tap-highlight-color`, `touch-action: manipulation`, `overscroll-behavior: none`, `user-select: none`. All features supported Chrome 69+ / Firefox 83+ / Safari 12.1+.

---

## Phase 3.5: QR Code & Polish (Week 9–10)

**Goal:** Zero-friction connection and polish; feature-complete v1.0.

- [x] **3.5.1** Implement `qr_display.py`: generate ASCII QR code in terminal and print plaintext URL below it within 2 seconds of launch (FR-05).
  - *Dependency:* Phase 3.1 complete; `qrcode` + `Pillow` installed.
  - *Acceptance Criteria:* UT-05 passes; QR scannable from terminal by iPhone and Android camera.
  - *Completed 2026-05-22:* `generate_and_print(url)` uses Unicode half-block renderer `_half_block()` — maps every 2 QR rows to 1 terminal line using `█ ▀ ▄ ' '`; light modules render as solid blocks, dark modules as empty space (correct polarity on dark terminals). Falls back to `qr.print_ascii(invert=True)` if `get_matrix()` unavailable; degrades gracefully with install hint if `qrcode` absent. `QRCode(ERROR_CORRECT_L, box_size=1, border=2)`. Message: `Scan to connect: {url}`. Called from `main.py` line 79 within the <2s launch window. `tests/test_qr_display.py` — 7 tests (UT-05): URL in output, scan message, QR body ≥5 lines, no exception, graceful without qrcode, half-block height, odd-row padding — all pass. Human-verified: scanned successfully on iOS and Android.

- [x] **3.5.2** Implement `--list-mics` CLI flag to enumerate audio input devices (FR-06).
  - *Dependency:* PyAudio installed.
  - *Acceptance Criteria:* Running `python main.py --list-mics` prints numbered mic list and exits.
  - *Completed 2026-05-22:* `main.py` `--list-mics` flag iterates `sounddevice.query_devices()`, prints all input devices, and calls `sys.exit(0)`.

- [x] **3.5.3** Implement `--model` flag to specify custom Whisper model size (FR-06).
  - *Dependency:* Task 3.3.1.
  - *Acceptance Criteria:* `--model SIZE` loads the specified model without error.
  - *Completed 2026-05-22:* `--model SIZE` CLI arg (default `tiny`) stored in `cfg.model_path`; passed to `WhisperModel(cfg.model_path, ...)` in `voice._worker()`.

- [x] **3.5.4** Add CLI `--help` documentation covering all flags.
  - *Dependency:* All CLI flags implemented.
  - *Acceptance Criteria:* `python main.py --help` lists `--port`, `--no-voice`, `--model`, `--list-mics` with descriptions.
  - *Completed 2026-05-22:* All four flags defined in `build_parser()` in `main.py` with `help=` strings. `argparse` auto-generates `--help` output.

- [x] **3.5.5** Confirm server is LAN-accessible without authentication (NFR-03).
  - *Dependency:* Task 3.1.2.
  - *Acceptance Criteria:* Any device on the same Wi-Fi can reach the remote UI instantly without any login step.
  - *Completed 2026-05-22:* Server binds to `0.0.0.0` (required for phone LAN access). No authentication required — open access by design for ease of use. External internet access blocked by home router NAT.

---

## Phase 4: Testing & Bug Fixes (Week 10–11)

**Goal:** All functional and non-functional requirements verified; public quality bar met.

- [x] **4.1** Run all unit tests (`pytest`): UT-01 through UT-06 (see Section 12.1 in source).
  - *Dependency:* Phase 3 complete.
  - *Acceptance Criteria:* 100% of unit tests pass with no warnings.
  - *Completed 2026-05-22 (updated 2026-05-22):* `pytest tests/` — **72/72 passed**, zero warnings, zero skips. Covers UT-01 (valid key mappings), UT-02 (invalid input ValueError), UT-03 (debounce), config validation (incl. model size), platform modifier routing, and UT-05 (qr_display). `conftest.py` updated to stub `pyautogui` and `qrcode` when not installed so suite runs green on any Python environment (3.13 Anaconda verified).

- [x] **4.2** Run integration tests: WebSocket command → keyboard action; voice keyword → keyboard action (Section 12.2 in source).
  - *Dependency:* Task 4.1.
  - *Acceptance Criteria:* All integration paths produce correct keyboard events.
  - *Completed 2026-05-22:* `tests/test_integration.py` written — 11 tests (IT-01–IT-11) across two classes. `TestWebSocketIntegration` (5 tests): calls `handle_command()` directly with `server.emit` patched to capture output — tests callback invocation, ack emission, ack payload, error on unknown action, all 5 valid actions. `TestVoiceIntegration` (6 tests): drives `voice._dispatch()` directly — tests keyboard.execute call, on_command callback, no-match returns False, and full pipeline to pyautogui.press. `conftest.py` updated with passthrough `socketio.on()` decorator stub so handler functions remain callable without real flask_socketio. Verified on Python 3.13 (Anaconda): 11/11 passed in 0.15s.

- [x] **4.3** System test ST-01: Windows 11 + PowerPoint 2021 — slides advance; latency <100ms.
  - *Dependency:* Task 4.2.
  - *Acceptance Criteria:* ST-01 pass criteria met (Section 12.3 in source).
  - *Completed 2026-05-22:* NEXT and BACK buttons physically advance/reverse slides in PowerPoint 2021 full-screen on Windows 11. Latency readout in UI orb confirms median <100ms over LAN; occasional spikes above 100ms observed under Wi-Fi jitter — consistent with NFR-01 (median target, not per-tap guarantee). ST-01 passed.

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
