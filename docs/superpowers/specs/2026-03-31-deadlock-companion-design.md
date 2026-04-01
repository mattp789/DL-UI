# Deadlock Companion — Objective Timer App

## Overview

A standalone Windows companion app for Valve's Deadlock that monitors the in-game minimap via screen capture, detects when objectives are killed, and displays respawn countdown timers on a large minimap UI in the browser — designed for a second monitor.

Distributed as a single `.exe` with zero dependencies. Users download, run, calibrate once, and it works automatically every match.

## Architecture

Single Python process with three components:

```
Screen Capture (mss, ~2 FPS) → OpenCV Detection → WebSocket → Browser UI (localhost:8080)
```

1. **Screen Capture Engine** — `mss` library grabs a user-defined rectangular region of the screen at ~2 FPS during active matches, 0.5 FPS during idle.
2. **Detection Engine** — OpenCV `matchTemplate` compares captured frames against bundled reference images of each objective icon. A match score drop below threshold = objective killed. Score returning above threshold = objective respawned.
3. **Web UI Server** — FastAPI serves a static HTML/JS/CSS page and pushes real-time timer updates over WebSocket.

## Tracked Objectives

| Objective | Icon Type | Respawn Timer | Timer Type |
|-----------|-----------|---------------|------------|
| T1 Neutral Camps (1 arrow) | Small camp marker | 1:25 | Relative to clear |
| T2 Neutral Camps (2 arrows) | Medium camp marker | 7:00 | Relative to clear |
| T3 Neutral Camps (3 arrows) | Large camp marker | 10:00 | Relative to clear |
| Sinner's Sacrifice | Sacrifice icon | 5:00 | Relative to destruction |
| Bridge Buffs | Buff icon on bridge | 5:00 | Relative to pickup |

All timers are relative — they start counting down when the objective is detected as cleared/destroyed.

## Screen Capture & Detection

### Region Selection (Calibration)

- On first launch or when user clicks "Recalibrate", a semi-transparent fullscreen overlay appears.
- User drags a rectangle over their in-game minimap.
- Coordinates saved to `~/.deadlock-companion/config.json`.
- Persists across sessions — subsequent launches skip calibration.

### Detection Strategy

- Bundled **reference template images** for each objective icon in its "alive" state (extracted from provided minimap screenshots).
- Each captured frame is compared against templates using `cv2.matchTemplate`.
- Each objective has a known relative position within the minimap region.
- **Icon disappears** (match score drops below threshold) → objective killed → start respawn countdown.
- **Icon reappears** (match score returns above threshold) → objective respawned → clear timer.

### Performance

- `mss` screen capture: ~5ms for a small region.
- Template matching for ~15 objectives: negligible.
- Total CPU overhead: under 2%.

## Match Lifecycle

### States

1. **Idle** — No minimap detected. UI shows "Waiting for match..." overlay. Capture runs at 0.5 FPS.
2. **Active** — Minimap detected. All objectives tracked. Capture runs at 2 FPS.

### Transitions

- **Idle → Active**: Minimap appears in capture region (template matches return above threshold). All objectives initialize as alive (green).
- **Active → Idle**: All template matches drop below threshold simultaneously (minimap disappears — match ended, menu screen, etc.). All timers cleared.
- Fully automatic — no user interaction needed between matches.

## Web UI

### Layout

- Large circular minimap rendering filling most of the browser window.
- Dark background matching game aesthetic.
- Objective markers placed at correct relative positions mirroring the in-game minimap.
- Top bar: connection status indicator, "Recalibrate" button.

### Marker Color Coding

| State | Color |
|-------|-------|
| Alive / available | Green |
| Just killed (full timer remaining) | Red |
| Respawning, > 50% timer remaining | Yellow |
| Respawning, < 50% timer remaining | Orange |
| About to respawn (< 15 seconds) | Pulsing green |

### Marker Behavior

- Each marker displays its remaining countdown time as a small label.
- Hover shows objective name and type.
- Optional audio chime when an objective is about to respawn (< 15 seconds).

### Manual Override

- Right-click a marker to manually toggle its state (start/reset timer).
- Allows correction if detection misses an event.
- Makes the tool functional even with imperfect detection.

## Configuration

Stored in `~/.deadlock-companion/config.json`:

- `capture_region`: `{x, y, width, height}` — minimap screen region
- `audio_alerts`: `boolean` — enable/disable respawn chimes
- `marker_adjustments`: optional manual position tweaks

## Distribution

- **Bundled with PyInstaller** into a single `deadlock-companion.exe`.
- Reference template images embedded in the bundle.
- No Python, Docker, or other dependencies required.
- Hosted on GitHub Releases.

### First-Run Experience

1. User downloads and double-clicks `deadlock-companion.exe`.
2. App starts, browser opens to `localhost:8080`.
3. "Welcome" screen with "Calibrate Minimap" button.
4. User clicks → transparent overlay appears → user drags rectangle over minimap.
5. Calibration saved, detection begins, UI goes live.

### Subsequent Runs

1. Double-click exe.
2. Browser opens, capture starts immediately with saved region.
3. Fully automatic — no interaction needed.

## Tech Stack

- **Python 3.12**
- **mss** — screen capture
- **OpenCV (cv2)** — template matching / image detection
- **FastAPI** — web server
- **uvicorn** — ASGI server
- **WebSocket** — real-time UI updates
- **tkinter** — region selector overlay (bundled with Python)
- **PyInstaller** — exe bundling
