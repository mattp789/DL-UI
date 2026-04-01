# Deadlock Companion

A standalone Windows companion app for Valve's Deadlock that tracks objective respawn timers using screen capture and displays them on a minimap UI in your browser.

## Features

- Automatic detection of objective kills via minimap screen capture
- Respawn countdown timers for neutral camps, Sinner's Sacrifice, and bridge buffs
- Color-coded markers (green → red → yellow → orange → pulsing green)
- Manual override — right-click any marker to start/reset its timer
- Zero-dependency single exe — download and run
- Auto-detects match start/end

## Quick Start

1. Download `deadlock-companion.exe` from [Releases](../../releases)
2. Run it — your browser opens to `http://localhost:8080`
3. Click **Recalibrate** and drag a rectangle over your in-game minimap
4. Play Deadlock — timers appear automatically

## Tracked Objectives

| Objective | Respawn Timer |
|-----------|---------------|
| T1 Neutral Camps (1 arrow) | 1:25 |
| T2 Neutral Camps (2 arrows) | 7:00 |
| T3 Neutral Camps (3 arrows) | 10:00 |
| Sinner's Sacrifice | 5:00 |
| Bridge Buffs | 5:00 |

## Development

### Prerequisites

- Python 3.12+

### Setup

```bash
cd deadlock-companion
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

### Run

```bash
python -m src.main
```

### Test

```bash
python -m pytest tests/ -v
```

### Build exe

```bash
python build.py
```

Output: `dist/deadlock-companion.exe`

### Generate template images

You must provide template images before detection works. Use the extraction tool with a full-resolution in-game minimap screenshot:

```bash
python tools/extract_templates.py path/to/minimap-screenshot.png
```

See `templates/README.md` for details.

## How It Works

1. **Screen Capture** — captures a user-defined region of the screen at ~2 FPS using `mss`
2. **Detection** — uses OpenCV template matching to detect objective icon presence/absence
3. **Timers** — when an icon disappears, starts a countdown based on the objective type
4. **UI** — pushes state over WebSocket to a browser-based minimap display

## Match Lifecycle

- **Idle** → app waits, scanning at 0.5 FPS
- **Match detected** → minimap appears, all objectives go green, 2 FPS scanning begins
- **Objective killed** → icon disappears, countdown starts, marker turns red → yellow → orange → pulsing green
- **Match ends** → all timers clear, back to idle

## Notes

- Templates must be extracted at your native screen resolution for best detection accuracy
- If detection misses an event, right-click any marker to manually toggle its timer
- Tested on Windows 10/11
