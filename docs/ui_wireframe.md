# SlideCommander — Mobile Remote UI Wire-frame

**Task ref:** 2.2 · **Phase:** Design · **Created:** 2026-05-22

---

## Wire-frame Mockup

> Represents a 390×844px viewport (iPhone 14 / mid-range Android reference).
> Each character cell ≈ 8px. Dark background rendered as `░` fill.

```
╔═══════════════════════════════════════╗
║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║  ← Status bar (OS)
╠═══════════════════════════════════════╣
║░░  SlideCommander            ●  LIVE ░║  ← Header
║░░  v1.0                               ║    ● green = connected
╠═══════════════════════════════════════╣    ● red   = disconnected
║░░                                   ░░║
║░░        ┌─────────────────────┐    ░░║
║░░        │                     │    ░░║  ← Timer block
║░░        │     ⏱  00:00        │    ░░║
║░░        │                     │    ░░║
║░░        └─────────────────────┘    ░░║
║░░                                   ░░║
║░░   [ ▶ START ]  [ ‖ PAUSE ]        ░░║  ← Timer controls
║░░                                   ░░║
╠═══════════════════════════════════════╣
║░░                                   ░░║
║░░   🎤  Voice: ON  │  Listening...  ░░║  ← Voice indicator
║░░                                   ░░║
╠═══════════════════════════════════════╣
║░░                                   ░░║
║░░  ┌─────────────┐ ┌─────────────┐  ░░║
║░░  │             │ │             │  ░░║
║░░  │             │ │             │  ░░║
║░░  │  ◀  BACK   │ │   NEXT  ▶  │  ░░║  ← PRIMARY buttons
║░░  │             │ │             │  ░░║  (96px tall, full-half width)
║░░  │             │ │             │  ░░║
║░░  └─────────────┘ └─────────────┘  ░░║
║░░                                   ░░║
╠═══════════════════════════════════════╣
║░░                                   ░░║
║░░  ┌─────────────┐ ┌─────────────┐  ░░║
║░░  │  ⏮  FIRST  │ │  LAST  ⏭  │  ░░║  ← SECONDARY buttons
║░░  └─────────────┘ └─────────────┘  ░░║  (64px tall)
║░░                                   ░░║
╠═══════════════════════════════════════╣
║░░                                   ░░║
║░░   Last command:  [ NEXT  ▶ ]      ░░║  ← Command echo badge
║░░                                   ░░║
╠═══════════════════════════════════════╣
║░░                                   ░░║
║░░  http://192.168.0.170:5000  v1.0  ░░║  ← Footer (server URL)
║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
╚═══════════════════════════════════════╝
```

---

## State Variants

### Voice indicator states

```
  🎤  Voice: ON  │  Listening...       ← idle, waiting for command
  🎤  Voice: ON  │  ✔ NEXT detected    ← command just fired (1.5s flash)
  🎤  Voice: OFF │  (disabled)         ← launched with --no-voice
  🎤  Voice: ERR │  No microphone      ← mic unavailable at startup
```

### Connection status dot

```
  ●  LIVE      ← green  (#22C55E)  — WebSocket connected
  ●  OFFLINE   ← red    (#EF4444)  — connection lost (auto-retry shown)
  ●  RETRY…    ← amber  (#F59E0B)  — Socket.IO reconnecting
```

### Command echo badge (bottom strip)

```
  Last command:  [ ◀ BACK  ]    ← blue pill, fades after 2 s
  Last command:  [ NEXT ▶  ]
  Last command:  [ ⏮ FIRST ]
  Last command:  [ LAST ⏭  ]
  Last command:  [ ‖ PAUSE  ]
```

---

## Design Specifications

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--bg-base` | `#0F172A` | Page background (Tailwind `slate-900`) |
| `--bg-surface` | `#1E293B` | Card / button-face background (`slate-800`) |
| `--bg-elevated` | `#334155` | Hovered / active button (`slate-700`) |
| `--accent-primary` | `#3B82F6` | BACK + NEXT button face (`blue-500`) |
| `--accent-primary-hover` | `#2563EB` | Button hover state (`blue-600`) |
| `--accent-primary-active` | `#1D4ED8` | Button pressed state (`blue-700`) |
| `--accent-secondary` | `#1E40AF` | FIRST + LAST button face (`blue-800`) |
| `--text-primary` | `#F8FAFC` | All main labels (`slate-50`) |
| `--text-muted` | `#94A3B8` | Footer URL, muted labels (`slate-400`) |
| `--status-live` | `#22C55E` | Connected dot (`green-500`) |
| `--status-offline` | `#EF4444` | Disconnected dot (`red-500`) |
| `--status-retry` | `#F59E0B` | Reconnecting dot (`amber-500`) |
| `--voice-active` | `#A78BFA` | Voice indicator glow (`violet-400`) |

### Typography

| Element | Size | Weight | Font |
|---|---|---|---|
| App title | `18px` | 700 | System UI / Inter |
| Timer display | `48px` | 800 | Monospace (tabular nums) |
| Primary button label | `22px` | 700 | System UI |
| Secondary button label | `16px` | 600 | System UI |
| Voice indicator | `14px` | 500 | System UI |
| Footer | `11px` | 400 | Monospace |

### Layout & Sizing

| Element | Height | Width | Notes |
|---|---|---|---|
| Header bar | `56px` | 100% | Fixed top |
| Timer block | `120px` | 80% | Centered, rounded-xl border |
| Timer controls row | `44px` | 80% | START + PAUSE inline |
| Voice indicator row | `40px` | 100% | Full-width, border-top/bottom |
| Primary buttons | `96px` | `calc(50% - 12px)` | 8px gap between; 8px margin each side |
| Secondary buttons | `64px` | `calc(50% - 12px)` | Same horizontal rhythm as primary |
| Command echo strip | `44px` | 100% | Full-width |
| Footer | `36px` | 100% | Fixed bottom |

### Interaction Design

- **Tap feedback:** Primary buttons scale to `0.96` on `touchstart`, restore on `touchend` (CSS `transform: scale()`). No 300ms click delay — `touch-action: manipulation` set on `<body>`.
- **Voice flash:** When a voice command fires, the matching button briefly highlights (`--accent-primary-active`) for 400ms to confirm detection visually.
- **Auto-reconnect indicator:** If WebSocket drops, a slim amber banner slides in below the header: `"Reconnecting… (attempt 2)"`. Disappears on reconnect.
- **Dark room safe:** No white backgrounds anywhere. Timer digits use `--text-primary` on `--bg-surface` — sufficient contrast (WCAG AA, ratio ≥ 4.5:1) without being harsh in a dark room.

### Accessibility

- All buttons carry `aria-label` attributes (`"Go to previous slide"`, `"Go to next slide"`, etc.).
- Minimum tap target: 64×64px (secondary) / 96×96px (primary) — exceeds WCAG 2.5.5 `44×44px` minimum.
- Color is never the sole indicator — button labels are always present alongside status dots.

---

*SlideCommander docs — ui_wireframe.md · Phase 2.2*
