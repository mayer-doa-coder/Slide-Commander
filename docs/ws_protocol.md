# SlideCommander — WebSocket Message Protocol

**Task ref:** 2.3 · **Phase:** Design · **Created:** 2026-05-22

---

## Overview

SlideCommander uses **Flask-SocketIO** (Socket.IO protocol v4) for all bidirectional
communication between the phone browser and the Python server. Every message is a
Socket.IO *named event* carrying a single JSON object as its payload.

The protocol is intentionally minimal — four event types cover the entire surface area
of the application:

| # | Event | Direction | Purpose |
|---|---|---|---|
| 1 | `command` | Client → Server | Send a slide navigation or pause action |
| 2 | `ack` | Server → Client | Confirm a command was received and executed |
| 3 | `error` | Server → Client | Report a failure (unknown command, bad PIN, etc.) |
| 4 | `auth` | Client → Server | Submit a PIN when the server runs in `--pin` mode |

All timestamps are **Unix epoch milliseconds** (integer). All string fields are
lowercase unless noted otherwise. Unknown fields in any payload MUST be silently
ignored by both sides to allow forward compatibility.

---

## 1. `command` — Client → Server

Sent by the phone browser each time the user taps a button or a voice command fires
on the host machine and needs to be echoed to connected clients.

### Field Definitions

| Field | Type | Required | Allowed Values | Description |
|---|---|---|---|---|
| `action` | string | **Required** | `"next"` `"back"` `"first"` `"last"` `"pause"` | The slide navigation or timer action to perform. Any other value MUST be rejected with an `error` response. |
| `source` | string | Optional | `"button"` `"voice"` | Origin of the command. Used by the server to annotate the `ack` and update the voice indicator on other connected clients. Defaults to `"button"` if omitted. |
| `ts` | integer | Optional | Unix ms | Client-side timestamp at the moment of the tap/detection. Used for latency logging only; not acted upon by the server. |

### Allowed `action` Values

| Value | Key sent to OS | FR ref |
|---|---|---|
| `"next"` | `RIGHT` arrow | FR-03 |
| `"back"` | `LEFT` arrow | FR-03 |
| `"first"` | `CTRL+HOME` / `CMD+HOME` | FR-03 |
| `"last"` | `CTRL+END` / `CMD+END` | FR-03 |
| `"pause"` | *(timer toggle — no key sent)* | FR-02 |

### Example Payloads

```json
{
  "action": "next",
  "source": "button",
  "ts": 1716336000123
}
```

```json
{
  "action": "back",
  "source": "voice"
}
```

```json
{
  "action": "first"
}
```

---

## 2. `ack` — Server → Client

Emitted by the server to the sending client immediately after a `command` is
successfully validated and the key-press dispatched. If `--pin` mode is active,
`ack` is only emitted to authenticated sessions.

### Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | **Required** | Echoes the `action` field from the triggering `command`. |
| `source` | string | **Required** | Echoes `source` from the command, or `"button"` if the original command omitted it. |
| `ts` | integer | **Required** | Server-side Unix ms timestamp at the moment of key dispatch. |
| `latency_ms` | integer | Optional | Round-trip latency in ms, computed as `server_ts − client_ts`. Only present when the `command` included a client `ts`. |

### Example Payloads

```json
{
  "action": "next",
  "source": "button",
  "ts": 1716336000125,
  "latency_ms": 2
}
```

```json
{
  "action": "back",
  "source": "voice",
  "ts": 1716336000300
}
```

---

## 3. `error` — Server → Client

Emitted to the sending client when a request cannot be fulfilled. The client SHOULD
display the `message` string to the user (e.g., as a toast notification) and take no
further action unless `code` indicates a recoverable condition.

### Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `code` | string | **Required** | Machine-readable error identifier (see Error Code Table below). |
| `message` | string | **Required** | Human-readable description safe to display in the UI. |
| `ts` | integer | **Required** | Server-side Unix ms timestamp. |
| `action` | string | Optional | The `action` value from the rejected `command`, if applicable. |

### Error Code Table

| `code` | Meaning | Typical trigger |
|---|---|---|
| `"unknown_action"` | `action` value not in the allowed set | Client sent `"swipe"` or a typo |
| `"not_authenticated"` | Session has not passed PIN auth | `command` received before `auth` in `--pin` mode |
| `"wrong_pin"` | PIN in `auth` payload did not match | User entered incorrect PIN |
| `"pin_required"` | Server is in `--pin` mode but no `auth` sent yet | First message was `command`, not `auth` |
| `"rate_limited"` | Commands arriving faster than debounce window | Client sending spam taps |
| `"server_error"` | Unhandled exception in key dispatch | PyAutoGUI failure, OS denial |

### Example Payloads

```json
{
  "code": "unknown_action",
  "message": "Unknown action 'swipe'. Allowed: next, back, first, last, pause.",
  "ts": 1716336000200,
  "action": "swipe"
}
```

```json
{
  "code": "not_authenticated",
  "message": "PIN required. Please authenticate before sending commands.",
  "ts": 1716336000050
}
```

```json
{
  "code": "wrong_pin",
  "message": "Incorrect PIN. Please try again.",
  "ts": 1716336000999
}
```

---

## 4. `auth` — Client → Server

Sent once by the phone browser when the server is launched with `--pin <digits>`.
The PIN entry screen is shown before the remote UI; on successful auth the server
responds with an `ack` (action `"auth_ok"`) and the full remote UI is revealed.
On failure the server responds with an `error` (`code: "wrong_pin"`).

### Field Definitions

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `pin` | string | **Required** | Exactly 4 ASCII digit characters (`[0-9]{4}`) | The PIN entered by the user. Transmitted as a string to preserve leading zeros (e.g., `"0042"`). |
| `ts` | integer | Optional | Unix ms | Client-side timestamp. Used for latency logging only. |

> **Security note:** The PIN is transmitted in plaintext over the local WebSocket
> connection. This is intentional — the threat model is LAN-local unauthorized access,
> not a network attacker. The PIN is a convenience lock, not a cryptographic secret.
> For high-security environments, bind the server to `127.0.0.1` only (`--localhost` flag).

### Example Payloads

```json
{
  "pin": "1234",
  "ts": 1716336000010
}
```

```json
{
  "pin": "0042"
}
```

### Auth Success Response (`ack`)

When the PIN matches, the server emits a standard `ack` with a special action value:

```json
{
  "action": "auth_ok",
  "source": "server",
  "ts": 1716336000015
}
```

---

## Full Message Flow Diagrams

### Flow A: Normal button press (no PIN)

```
Phone Browser                         Python Server
      │                                     │
      │──── command {"action":"next"} ─────►│
      │                                     │  keyboard.execute("next")
      │◄─── ack {"action":"next", ...} ─────│
      │                                     │
```

### Flow B: Voice command (server-side origin)

```
Microphone → voice.py → keyboard.py
                  │
                  └──► server.py broadcasts to all clients:
                            ack {"action":"next", "source":"voice", ...}
```

### Flow C: PIN authentication flow

```
Phone Browser                         Python Server
      │                                     │
      │  (PIN screen shown)                 │
      │──── auth {"pin":"1234"} ───────────►│
      │                                     │  PIN matches
      │◄─── ack {"action":"auth_ok"} ───────│
      │                                     │
      │  (Remote UI revealed)               │
      │──── command {"action":"next"} ─────►│
      │◄─── ack {"action":"next", ...} ─────│
```

### Flow D: Wrong PIN

```
Phone Browser                         Python Server
      │                                     │
      │──── auth {"pin":"9999"} ───────────►│
      │                                     │  PIN mismatch
      │◄─── error {"code":"wrong_pin"} ─────│
      │                                     │
      │  (PIN screen remains; error toast)  │
```

### Flow E: Unknown action rejected

```
Phone Browser                         Python Server
      │                                     │
      │──── command {"action":"zoom"} ─────►│
      │                                     │  "zoom" ∉ allowed set
      │◄─── error {"code":"unknown_action"} │
```

---

## Implementation Notes

- **Server handler skeleton** (`server.py`):

```python
ALLOWED_ACTIONS = {"next", "back", "first", "last", "pause"}

@socketio.on("command")
def handle_command(data):
    if pin_enabled and not session.get("authenticated"):
        emit("error", {"code": "not_authenticated", ...})
        return
    action = data.get("action")
    if action not in ALLOWED_ACTIONS:
        emit("error", {"code": "unknown_action", ...})
        return
    keyboard.execute(action)
    emit("ack", {"action": action, "source": data.get("source", "button"), "ts": now_ms()})

@socketio.on("auth")
def handle_auth(data):
    if data.get("pin") == config.pin:
        session["authenticated"] = True
        emit("ack", {"action": "auth_ok", "source": "server", "ts": now_ms()})
    else:
        emit("error", {"code": "wrong_pin", ...})
```

- **Client handler skeleton** (`static/index.html`):

```javascript
socket.on("ack",   (data) => highlightButton(data.action));
socket.on("error", (data) => showToast(data.message));

function sendCommand(action) {
  socket.emit("command", { action, source: "button", ts: Date.now() });
}
```

---

*SlideCommander docs — ws_protocol.md · Phase 2.3*
