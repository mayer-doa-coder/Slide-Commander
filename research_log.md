# SlideCommander — Research Log

**Task refs:** 1.1 (STT benchmark) · 1.2 (keyboard sim) · 1.3 (WebSocket latency) · 1.4 (QR code)
**Status:** Scripts delivered — awaiting results from local hardware runs.
**Phase gate:** All sections below must be filled in before Phase 2 begins.

---

## 1. Research Methodology

### 1.1 Objective

Select the optimal offline speech-to-text engine for SlideCommander's voice command layer
and validate all other technical assumptions required by the project plan.

### 1.2 Acceptance Targets

| Requirement | Target | Source |
|---|---|---|
| Voice recognition latency | < 300 ms | NFR-01 |
| Voice recognition accuracy | ≥ 95 % | FR-04 |
| WebSocket round-trip latency | ≤ 100 ms | NFR-01 |
| Key simulation: no admin privileges required | Confirmed | FR-03 |
| QR code: scannable from terminal by 2 mobile OSes | Confirmed | FR-05 |

### 1.3 Tooling

| Task | Script | How to run |
|---|---|---|
| 1.1 STT benchmark | `benchmark_stt.py` | See §2 |
| 1.2 Keyboard simulation | `test_keyboard.py` | See §3.2 |
| 1.3 WebSocket latency | `benchmark_websocket.py` | See §3.3 |
| 1.4 QR code evaluation | `test_qrcode.py` | See §3.4 |

---

## 2. STT Engine Benchmark (Task 1.1)

### 2.1 Engines Evaluated

| # | Engine | Package | Approach | Model size |
|---|---|---|---|---|
| 1 | **Vosk** | `vosk` | Streaming Kaldi ASR | 40 MB (manual download) |
| 2 | **Faster-Whisper** | `faster-whisper` | CTranslate2 Whisper int8 | 39 MB tiny / 74 MB base (auto) |
| 3 | **PocketSphinx** | `pocketsphinx` | Keyword-spotting mode | Bundled (no download) |
| 4 | Silero STT *(optional)* | `torch` + `torchaudio` | Neural CTC via PyTorch Hub | ~25 MB (auto) |

### 2.2 Setup

```bash
# 1 — Install packages
pip install vosk faster-whisper pocketsphinx psutil pyaudio
# Optional: pip install torch torchaudio   ← adds Silero engine

# 2 — Download Vosk model
# Windows (PowerShell):
Invoke-WebRequest https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip -OutFile model.zip
Expand-Archive model.zip .
# Linux / macOS:
# wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip && unzip vosk-model-en-us-0.22.zip

# 3 — Record 10 test samples per command (50 total)
python benchmark_stt.py --record --samples 10 --audio-dir test_audio/

# 4 — Run benchmark and save JSON
python benchmark_stt.py --audio-dir test_audio/ --output results.json
```

**Test audio format:** 16 kHz · 16-bit PCM · mono WAV · 1–3 s per clip.
Use ffmpeg to convert existing recordings:
```
ffmpeg -i input.wav -ac 1 -ar 16000 -sample_fmt s16 output.wav
```

### 2.3 Hardware Profile

| Field | Value |
|---|---|
| Date | 2026-05-21 |
| OS / Version | Windows 11 |
| CPU | Intel64 Family 6 Model 191 (13th Gen Intel Core, GenuineIntel) |
| Machine | AMD64 |
| Python | 3.14.2 |
| Engines tested | vosk (vosk-model-en-us-0.22), faster-whisper (tiny), pocketsphinx (failed — not installed) |

---

## 3. Results

### 3.1 Load Time & Memory Footprint

> Copy values from `results.json → results[n].load_time_ms` and `.memory_delta_mb`.

| Engine | Load Time (ms) | Memory Δ (MB) | Notes |
|---|---|---|---|
| vosk | 24,553.7 | +2,140.7 | vosk-model-en-us-0.22 (large model); extremely high RAM usage |
| faster-whisper (tiny) | 65,719.4 | +148.4 | Auto-downloaded tiny model; high load time, low memory after load |
| pocketsphinx | — | — | Not installed (Python 3.14 incompatible) |
| silero | — | — | Not tested |

### 3.2 Latency

> Copy values from `results.json → results[n].median_latency_ms`, `.p95_latency_ms`, `.mean_rtf`.

| Engine | Median (ms) | P95 (ms) | Mean RTF | < 300 ms? |
|---|---|---|---|---|
| vosk | 526.7 | 895.7 | 0.229 | **NO** |
| faster-whisper (tiny) | 269.4 | 303.3 | 0.112 | **YES** (median passes; P95 barely over) |
| pocketsphinx | — | — | — | — |
| silero | — | — | — | — |

### 3.3 Accuracy

> Copy values from `results.json → results[n].accuracy_pct` and `.per_keyword_accuracy`.

| Engine | next | back | start | end | pause | **Overall %** | ≥ 95 %? |
|---|---|---|---|---|---|---|---|
| vosk | 100.0 % | 10.0 % | 0.0 % | 0.0 % | 50.0 % | **32.0 %** | **NO** |
| faster-whisper (tiny) | 100.0 % | 100.0 % | 80.0 % | 30.0 % | 100.0 % | **82.0 %** | **NO** |
| pocketsphinx | — | — | — | — | — | — | — |
| silero | — | — | — | — | — | — | — |

### 3.4 Benchmarking Results

> Paste the full contents of `results.json` into the code block below after running the benchmark.

```json
{
  "benchmark_version": "1.1",
  "timestamp": "2026-05-21T23:52:24",
  "hardware": {
    "os": "Windows 11",
    "machine": "AMD64",
    "python": "3.14.2",
    "cpu": "Intel64 Family 6 Model 191 Stepping 2, GenuineIntel"
  },
  "targets": {
    "latency_budget_ms": 300.0,
    "accuracy_target_pct": 95.0
  },
  "results": [
    {
      "engine": "vosk",
      "load_time_ms": 24553.7,
      "memory_delta_mb": 2140.7,
      "accuracy_pct": 32.0,
      "median_latency_ms": 526.7,
      "p95_latency_ms": 895.7,
      "mean_rtf": 0.229,
      "per_keyword_accuracy": {
        "next": 100.0,
        "back": 10.0,
        "start": 0.0,
        "end": 0.0,
        "pause": 50.0
      },
      "sample_count": 50,
      "meets_latency": false,
      "meets_accuracy": false,
      "error": null
    },
    {
      "engine": "faster-whisper",
      "load_time_ms": 65719.4,
      "memory_delta_mb": 148.4,
      "accuracy_pct": 82.0,
      "median_latency_ms": 269.4,
      "p95_latency_ms": 303.3,
      "mean_rtf": 0.112,
      "per_keyword_accuracy": {
        "next": 100.0,
        "back": 100.0,
        "start": 80.0,
        "end": 30.0,
        "pause": 100.0
      },
      "sample_count": 50,
      "meets_latency": true,
      "meets_accuracy": false,
      "error": null
    },
    {
      "engine": "pocketsphinx",
      "load_time_ms": 0.2,
      "memory_delta_mb": 0.0,
      "accuracy_pct": 0.0,
      "median_latency_ms": 0.0,
      "p95_latency_ms": 0.0,
      "mean_rtf": 0.0,
      "per_keyword_accuracy": {
        "next": 0.0,
        "back": 0.0,
        "start": 0.0,
        "end": 0.0,
        "pause": 0.0
      },
      "sample_count": 0,
      "meets_latency": true,
      "meets_accuracy": false,
      "error": "pip install pocketsphinx"
    }
  ],
  "recommended_engine": null
}
```

---

## 4. Other Feasibility Results

### 4.1 PyAutoGUI Key Simulation (Task 1.2)

**Script:** `test_keyboard.py`
**How to run:**
```bash
pip install pyautogui
python test_keyboard.py
# Follow on-screen prompts. Switch to a presentation app when the countdown starts.
```

| Platform | App tested | RIGHT key (next) | LEFT key (back) | CTRL+HOME (first) | CTRL+END (last) | Admin needed? |
|---|---|---|---|---|---|---|
| Windows 11 | PowerPoint | YES ✓ | YES ✓ | YES ✓ | YES ✓ | **NO** ✓ |
| macOS | Not tested — no macOS machine available | — | — | — | — | — |
| Ubuntu | Not tested — no Ubuntu machine available | — | — | — | — | — |

**Test run details:**
- Timestamp: 2026-05-22T00:06:51
- Python: 3.14.2
- Modifier key used: `ctrl`
- All 4 actions passed: **YES**

**Raw results (`keyboard_test_results.json`):**
```json
{
  "timestamp": "2026-05-22T00:06:51",
  "platform": "Windows 11",
  "python": "3.14.2",
  "modifier": "ctrl",
  "results": [
    { "action": "next",  "description": "NEXT slide (RIGHT arrow)",       "passed": true, "note": "" },
    { "action": "back",  "description": "PREVIOUS slide (LEFT arrow)",    "passed": true, "note": "" },
    { "action": "first", "description": "FIRST slide (CTRL/CMD + HOME)",  "passed": true, "note": "" },
    { "action": "last",  "description": "LAST slide  (CTRL/CMD + END)",   "passed": true, "note": "" }
  ],
  "all_passed": true
}
```

**Viability summary:** PyAutoGUI key simulation is fully confirmed on Windows 11 — all four slide navigation actions (next, back, first, last) work correctly without administrator privileges. macOS and Ubuntu remain untested due to hardware unavailability; this is an accepted risk logged below. Windows is the primary target platform for SlideCommander v1.0.

**Notes / issues found:**
- No issues on Windows 11. macOS will require Accessibility permission (System Settings → Privacy & Security → Accessibility) when tested — document this in README.

---

### 4.2 Flask-SocketIO Latency (Task 1.3)

**Script:** `benchmark_websocket.py`
**How to run:**
```bash
pip install flask flask-socketio simple-websocket
# Localhost benchmark (no phone needed):
python benchmark_websocket.py

# LAN test — run on presenter's machine:
python benchmark_websocket.py --server --port 5001
# Then on a second device (same Wi-Fi), open browser → http://<host-ip>:5001
# OR run: python benchmark_websocket.py --client --host <host-ip> --port 5001
```

| Mode | Pings | Min (ms) | Median (ms) | Mean (ms) | P95 (ms) | P99 (ms) | Max (ms) | ≤ 100 ms? |
|---|---|---|---|---|---|---|---|---|
| Localhost (127.0.0.1) | 100 | 0.7 | **0.9** | 1.0 | 1.5 | 2.8 | 2.8 | **YES ✓** |
| LAN (192.168.0.170:5001) | 100 | 0.7 | **1.0** | 1.1 | 2.1 | 7.6 | 7.6 | **YES ✓** |

**Test details:**
- Timestamp: 2026-05-22T00:16:06
- Platform: Windows 11
- Transport: WebSocket (websocket-client + simple-websocket)
- Warm-up pings: 5 (discarded) | Benchmark pings: 100

**Raw results (`websocket_results.json`):**
```json
{
  "timestamp": "2026-05-22T00:16:06",
  "platform": "Windows 11",
  "results": [
    {
      "mode": "localhost",
      "ping_count": 100,
      "min_ms": 0.7, "median_ms": 0.9, "mean_ms": 1.0,
      "p95_ms": 1.5, "p99_ms": 2.8, "max_ms": 2.8,
      "meets_target": true
    },
    {
      "mode": "LAN → 192.168.0.170:5001",
      "ping_count": 100,
      "min_ms": 0.7, "median_ms": 1.0, "mean_ms": 1.1,
      "p95_ms": 2.1, "p99_ms": 7.6, "max_ms": 7.6,
      "meets_target": true
    }
  ]
}
```

**Viability summary:** Flask-SocketIO WebSocket round-trip latency is **confirmed well within target** on this hardware. Localhost median is 0.9 ms and LAN median is 1.0 ms — both are 100× faster than the ≤100 ms requirement. Even the worst single ping (7.6 ms) is 13× under the budget. The WebSocket stack is not a bottleneck for SlideCommander.

**Notes:**
- LAN test was run client→server on the same machine (192.168.0.170 is the local LAN IP). A real phone-over-Wi-Fi test would add ~5–30 ms depending on router and distance, but would still comfortably pass the 100 ms target.
- First run used HTTP polling (websocket-client not found); second run used true WebSocket after installing websocket-client — results reflect true WebSocket transport.

---

### 4.3 QR Code Library (Task 1.4)

**Script:** `test_qrcode.py`
**How to run:**
```bash
pip install qrcode pillow
python test_qrcode.py
# Scan the QR code printed in the terminal with your phone camera.
```

| Item | Result |
|---|---|
| QR generated in terminal | YES / NO |
| QR scannable — iOS camera | YES / NO |
| QR scannable — Android camera | YES / NO |
| PNG also saved | YES / NO |
| Generation time (ms) | *(fill in)* |

**Notes:**
> *(fill in — e.g. terminal font size needed, colour contrast issues)*

---

## 5. Winner Declaration

> **Complete this section after filling in all results above.**
> This section constitutes the acceptance evidence for Task 1.1.

### 5.1 Ranking

> No engine passed BOTH targets on this hardware in this run. faster-whisper (tiny) is the conditional winner — it meets latency and is closest to the accuracy target. Root cause of accuracy failure is the keyword "end" (30 % recognition rate), which is phonetically ambiguous and easily transcribed as "and", "in", or similar words.

| Rank | Engine | Median latency | Accuracy | Status |
|---|---|---|---|---|
| 1 (conditional) | faster-whisper (tiny) | 269.4 ms | 82.0 % | Latency ✓ — Accuracy ✗ (fix: swap "end" → "last") |
| 2 | vosk | 526.7 ms | 32.0 % | Latency ✗ — Accuracy ✗ — RAM +2.1 GB |
| — | pocketsphinx | — | — | Not installed (Python 3.14 incompatible) |

### 5.2 Selected Engine

| Field | Value |
|---|---|
| **Engine name** | faster-whisper |
| **Model size** | tiny (~39 MB, auto-downloaded) |
| **Median latency** | 269.4 ms |
| **P95 latency** | 303.3 ms |
| **Overall accuracy (current)** | 82.0 % |
| **Accuracy blocker** | "end" keyword — 30 % recognition; phonetically ambiguous |
| **Projected accuracy after fix** | ~95 % (replace "end" with "last" in COMMANDS list) |
| **Reason for selection** | Only engine that met the latency target; lowest memory footprint; accuracy failure is isolated to one keyword with a clear fix |

### 5.3 Rejected Engines

| Engine | Reason for rejection |
|---|---|
| vosk (vosk-model-en-us-0.22) | Median latency 526.7 ms (exceeds 300 ms budget); accuracy only 32 %; RAM usage +2.1 GB is impractical for a background service. Consider re-testing with vosk-model-small-en-us-0.15 if faster-whisper is ruled out. |
| pocketsphinx | Could not be installed on Python 3.14. No data collected. |
| silero | Not tested (requires torch/torchaudio, not installed). |

### 5.4 Integration Notes

- Engine to wire into `voice.py`: **faster-whisper (tiny model)**
- CLI flag for model path: `--model <path>` (maps to `config.py` → `model_path`)
- Debounce setting confirmed: **500 ms** (per Algorithm 10.1, project plan Section 10.1)
- **Required fix before Phase 3.3:** Replace keyword `"end"` with `"last"` in `COMMANDS` list in `benchmark_stt.py` and `voice.py` to resolve the 30 % recognition rate on that keyword.
- **Optional follow-up:** Re-run benchmark with `--whisper-model base` to verify accuracy improvement before committing to tiny model.

---

## 6. Risk Register

| Risk | Observed? | Mitigation Applied |
|---|---|---|
| Vosk latency > 300 ms on this CPU | **YES** — 526.7 ms median | Switch to `vosk-model-small-en-us-0.15`; or use faster-whisper instead (selected) |
| "end" confused with "and" in transcript | **YES** — 30 % accuracy on "end" | Replace keyword `"end"` with `"last"` in COMMANDS list |
| "start" not in Vosk vocabulary | **YES** — 0 % accuracy on "start" for Vosk | Vosk large model failed on "start"; faster-whisper got 80 % |
| High false-positive rate in noisy room | Not tested | Re-test in noisy environment before Phase 3.3 |
| PyAudio install failed on Windows | **YES** — Python 3.14 incompatible | Replaced with `sounddevice` backend in `benchmark_stt.py` |
| macOS Accessibility permission required | Not tested (Windows only machine) | Document in README when macOS testing is done (Task 1.2) |

---

*SlideCommander Research Log v1.1 — Created 2026-05-15*
*Covers Tasks: 1.1 · 1.2 · 1.3 · 1.4 · 1.5*
