# Deadlock Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Windows companion app that monitors the Deadlock minimap via screen capture, detects objective state changes, and displays respawn countdown timers in a browser UI.

**Architecture:** Single Python process with three components — screen capture engine (mss), detection engine (OpenCV template matching), and web UI server (FastAPI + WebSocket). Bundled as a single .exe via PyInstaller.

**Tech Stack:** Python 3.12, mss, OpenCV, FastAPI, uvicorn, websockets, tkinter, PyInstaller

**Spec:** `docs/superpowers/specs/2026-03-31-deadlock-companion-design.md`

---

## File Structure

```
deadlock-companion/
├── src/
│   ├── main.py                  # Entry point — starts all components
│   ├── capture.py               # Screen capture engine (mss)
│   ├── detector.py              # OpenCV template matching detection
│   ├── timers.py                # Timer state management for objectives
│   ├── server.py                # FastAPI + WebSocket server
│   ├── calibration.py           # Tkinter region selector overlay
│   ├── config.py                # Config load/save (~/.deadlock-companion/)
│   └── models.py                # Shared data models (ObjectiveState, etc.)
├── static/
│   ├── index.html               # Main UI page
│   ├── style.css                # Dark theme styles
│   ├── app.js                   # WebSocket client + minimap rendering
│   └── minimap.svg              # Base minimap background image
├── templates/
│   ├── t1_camp.png              # Reference icon — T1 neutral camp
│   ├── t2_camp.png              # Reference icon — T2 neutral camp
│   ├── t3_camp.png              # Reference icon — T3 neutral camp
│   ├── sinner.png               # Reference icon — Sinner's Sacrifice
│   └── bridge_buff.png          # Reference icon — Bridge Buff
├── tests/
│   ├── test_timers.py           # Timer logic tests
│   ├── test_detector.py         # Detection logic tests
│   ├── test_config.py           # Config tests
│   ├── test_models.py           # Model tests
│   └── test_server.py           # Server/WebSocket tests
├── requirements.txt             # Python dependencies
├── build.spec                   # PyInstaller spec file
└── README.md                    # User-facing docs
```

---

## Task 1: Project Scaffolding & Dependencies

**Files:**
- Create: `deadlock-companion/requirements.txt`
- Create: `deadlock-companion/src/main.py` (stub)
- Create: `deadlock-companion/src/models.py`
- Create: `deadlock-companion/tests/test_models.py`

- [ ] **Step 1: Create project directory and requirements.txt**

```bash
mkdir -p deadlock-companion/src deadlock-companion/static deadlock-companion/templates deadlock-companion/tests
```

Create `deadlock-companion/requirements.txt`:
```
mss==9.0.2
opencv-python-headless==4.10.0.84
fastapi==0.115.6
uvicorn[standard]==0.34.0
websockets==13.1
Pillow==11.1.0
numpy==2.2.1
pytest==8.3.4
```

- [ ] **Step 2: Create virtual environment and install dependencies**

```bash
cd deadlock-companion
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

Expected: All packages install successfully.

- [ ] **Step 3: Write failing test for data models**

Create `deadlock-companion/tests/test_models.py`:
```python
from src.models import ObjectiveType, ObjectiveState, Objective, MatchState


def test_objective_type_has_respawn_durations():
    assert ObjectiveType.T1_CAMP.respawn_seconds == 85  # 1:25
    assert ObjectiveType.T2_CAMP.respawn_seconds == 420  # 7:00
    assert ObjectiveType.T3_CAMP.respawn_seconds == 600  # 10:00
    assert ObjectiveType.SINNER.respawn_seconds == 300  # 5:00
    assert ObjectiveType.BRIDGE_BUFF.respawn_seconds == 300  # 5:00


def test_objective_state_values():
    assert ObjectiveState.ALIVE.value == "alive"
    assert ObjectiveState.DEAD.value == "dead"


def test_objective_creation():
    obj = Objective(
        id="t1_camp_1",
        name="T1 Camp Alpha",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.25, 0.40),
        template_name="t1_camp.png",
    )
    assert obj.state == ObjectiveState.ALIVE
    assert obj.remaining_seconds is None
    assert obj.objective_type.respawn_seconds == 85


def test_match_state_values():
    assert MatchState.IDLE.value == "idle"
    assert MatchState.ACTIVE.value == "active"
```

- [ ] **Step 4: Run test to verify it fails**

```bash
cd deadlock-companion
python -m pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 5: Implement data models**

Create `deadlock-companion/src/__init__.py` (empty file).

Create `deadlock-companion/tests/__init__.py` (empty file).

Create `deadlock-companion/src/models.py`:
```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ObjectiveType(Enum):
    T1_CAMP = ("t1_camp", 85)       # 1:25
    T2_CAMP = ("t2_camp", 420)      # 7:00
    T3_CAMP = ("t3_camp", 600)      # 10:00
    SINNER = ("sinner", 300)        # 5:00
    BRIDGE_BUFF = ("bridge_buff", 300)  # 5:00

    def __init__(self, key: str, respawn_seconds: int):
        self.key = key
        self.respawn_seconds = respawn_seconds


class ObjectiveState(Enum):
    ALIVE = "alive"
    DEAD = "dead"


class MatchState(Enum):
    IDLE = "idle"
    ACTIVE = "active"


@dataclass
class Objective:
    id: str
    name: str
    objective_type: ObjectiveType
    position: tuple[float, float]  # (x%, y%) relative to minimap region
    template_name: str
    state: ObjectiveState = ObjectiveState.ALIVE
    remaining_seconds: Optional[float] = None
    killed_at: Optional[float] = None  # time.monotonic() when killed
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python -m pytest tests/test_models.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 7: Create main.py stub**

Create `deadlock-companion/src/main.py`:
```python
"""Deadlock Companion — Objective Timer App entry point."""

import sys


def main():
    print("Deadlock Companion starting...")
    print("Components will be initialized here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 8: Commit**

```bash
git add deadlock-companion/
git commit -m "feat: scaffold project with data models and dependencies"
```

---

## Task 2: Configuration Management

**Files:**
- Create: `deadlock-companion/src/config.py`
- Create: `deadlock-companion/tests/test_config.py`

- [ ] **Step 1: Write failing tests for config**

Create `deadlock-companion/tests/test_config.py`:
```python
import json
import os
from pathlib import Path
from src.config import Config


def test_default_config(tmp_path):
    config = Config(config_dir=tmp_path)
    assert config.capture_region is None
    assert config.audio_alerts is True


def test_save_and_load_config(tmp_path):
    config = Config(config_dir=tmp_path)
    config.capture_region = {"x": 100, "y": 200, "width": 300, "height": 300}
    config.audio_alerts = False
    config.save()

    loaded = Config(config_dir=tmp_path)
    loaded.load()
    assert loaded.capture_region == {"x": 100, "y": 200, "width": 300, "height": 300}
    assert loaded.audio_alerts is False


def test_config_creates_directory(tmp_path):
    config_dir = tmp_path / "subdir" / "deadlock-companion"
    config = Config(config_dir=config_dir)
    config.save()
    assert config_dir.exists()
    assert (config_dir / "config.json").exists()


def test_load_missing_file_uses_defaults(tmp_path):
    config = Config(config_dir=tmp_path)
    config.load()  # Should not raise
    assert config.capture_region is None
    assert config.audio_alerts is True


def test_needs_calibration(tmp_path):
    config = Config(config_dir=tmp_path)
    assert config.needs_calibration is True
    config.capture_region = {"x": 0, "y": 0, "width": 100, "height": 100}
    assert config.needs_calibration is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.config'`

- [ ] **Step 3: Implement config module**

Create `deadlock-companion/src/config.py`:
```python
import json
from pathlib import Path
from typing import Optional


class Config:
    DEFAULT_DIR = Path.home() / ".deadlock-companion"

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self.DEFAULT_DIR
        self.config_file = self.config_dir / "config.json"
        self.capture_region: Optional[dict] = None
        self.audio_alerts: bool = True
        self.load()

    def load(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                data = json.load(f)
            self.capture_region = data.get("capture_region")
            self.audio_alerts = data.get("audio_alerts", True)

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "capture_region": self.capture_region,
            "audio_alerts": self.audio_alerts,
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def needs_calibration(self) -> bool:
        return self.capture_region is None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_config.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add deadlock-companion/src/config.py deadlock-companion/tests/test_config.py
git commit -m "feat: add configuration management with persistence"
```

---

## Task 3: Timer State Management

**Files:**
- Create: `deadlock-companion/src/timers.py`
- Create: `deadlock-companion/tests/test_timers.py`

- [ ] **Step 1: Write failing tests for timer manager**

Create `deadlock-companion/tests/test_timers.py`:
```python
import time
from unittest.mock import patch
from src.models import Objective, ObjectiveType, ObjectiveState, MatchState
from src.timers import TimerManager


def _make_objectives():
    return [
        Objective(
            id="t1_camp_1",
            name="T1 Camp 1",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.25, 0.40),
            template_name="t1_camp.png",
        ),
        Objective(
            id="sinner_1",
            name="Sinner 1",
            objective_type=ObjectiveType.SINNER,
            position=(0.50, 0.50),
            template_name="sinner.png",
        ),
    ]


def test_initial_state():
    mgr = TimerManager(_make_objectives())
    assert mgr.match_state == MatchState.IDLE
    for obj in mgr.objectives:
        assert obj.state == ObjectiveState.ALIVE
        assert obj.remaining_seconds is None


def test_start_match():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    assert mgr.match_state == MatchState.ACTIVE


def test_mark_killed_starts_timer():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("t1_camp_1")
    obj = mgr.get_objective("t1_camp_1")
    assert obj.state == ObjectiveState.DEAD
    assert obj.killed_at is not None


def test_update_decrements_remaining():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("t1_camp_1")
    obj = mgr.get_objective("t1_camp_1")
    killed_time = obj.killed_at

    with patch("time.monotonic", return_value=killed_time + 10.0):
        mgr.update()
    assert obj.remaining_seconds == 75.0  # 85 - 10


def test_timer_expires_resets_to_alive():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("t1_camp_1")
    obj = mgr.get_objective("t1_camp_1")
    killed_time = obj.killed_at

    with patch("time.monotonic", return_value=killed_time + 86.0):
        mgr.update()
    assert obj.state == ObjectiveState.ALIVE
    assert obj.remaining_seconds is None
    assert obj.killed_at is None


def test_mark_respawned():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("sinner_1")
    mgr.mark_respawned("sinner_1")
    obj = mgr.get_objective("sinner_1")
    assert obj.state == ObjectiveState.ALIVE
    assert obj.remaining_seconds is None


def test_end_match_clears_all():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("t1_camp_1")
    mgr.end_match()
    assert mgr.match_state == MatchState.IDLE
    for obj in mgr.objectives:
        assert obj.state == ObjectiveState.ALIVE
        assert obj.remaining_seconds is None


def test_get_all_states():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.mark_killed("t1_camp_1")
    states = mgr.get_all_states()
    assert len(states) == 2
    assert states[0]["id"] == "t1_camp_1"
    assert states[0]["state"] == "dead"
    assert states[1]["id"] == "sinner_1"
    assert states[1]["state"] == "alive"


def test_toggle_manual():
    mgr = TimerManager(_make_objectives())
    mgr.start_match()
    mgr.toggle_manual("t1_camp_1")
    obj = mgr.get_objective("t1_camp_1")
    assert obj.state == ObjectiveState.DEAD
    mgr.toggle_manual("t1_camp_1")
    assert obj.state == ObjectiveState.ALIVE
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_timers.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.timers'`

- [ ] **Step 3: Implement timer manager**

Create `deadlock-companion/src/timers.py`:
```python
import time
from typing import Optional
from src.models import Objective, ObjectiveState, MatchState


class TimerManager:
    def __init__(self, objectives: list[Objective]):
        self.objectives = objectives
        self.match_state = MatchState.IDLE
        self._objectives_by_id = {obj.id: obj for obj in objectives}

    def get_objective(self, objective_id: str) -> Optional[Objective]:
        return self._objectives_by_id.get(objective_id)

    def start_match(self):
        self.match_state = MatchState.ACTIVE
        for obj in self.objectives:
            obj.state = ObjectiveState.ALIVE
            obj.remaining_seconds = None
            obj.killed_at = None

    def end_match(self):
        self.match_state = MatchState.IDLE
        for obj in self.objectives:
            obj.state = ObjectiveState.ALIVE
            obj.remaining_seconds = None
            obj.killed_at = None

    def mark_killed(self, objective_id: str):
        obj = self._objectives_by_id.get(objective_id)
        if obj and self.match_state == MatchState.ACTIVE:
            obj.state = ObjectiveState.DEAD
            obj.killed_at = time.monotonic()
            obj.remaining_seconds = float(obj.objective_type.respawn_seconds)

    def mark_respawned(self, objective_id: str):
        obj = self._objectives_by_id.get(objective_id)
        if obj:
            obj.state = ObjectiveState.ALIVE
            obj.remaining_seconds = None
            obj.killed_at = None

    def toggle_manual(self, objective_id: str):
        obj = self._objectives_by_id.get(objective_id)
        if not obj:
            return
        if obj.state == ObjectiveState.ALIVE:
            self.mark_killed(objective_id)
        else:
            self.mark_respawned(objective_id)

    def update(self):
        now = time.monotonic()
        for obj in self.objectives:
            if obj.state == ObjectiveState.DEAD and obj.killed_at is not None:
                elapsed = now - obj.killed_at
                remaining = obj.objective_type.respawn_seconds - elapsed
                if remaining <= 0:
                    obj.state = ObjectiveState.ALIVE
                    obj.remaining_seconds = None
                    obj.killed_at = None
                else:
                    obj.remaining_seconds = remaining

    def get_all_states(self) -> list[dict]:
        return [
            {
                "id": obj.id,
                "name": obj.name,
                "type": obj.objective_type.key,
                "state": obj.state.value,
                "remaining_seconds": obj.remaining_seconds,
                "respawn_total": obj.objective_type.respawn_seconds,
                "position": obj.position,
            }
            for obj in self.objectives
        ]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_timers.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add deadlock-companion/src/timers.py deadlock-companion/tests/test_timers.py
git commit -m "feat: add timer state management with kill/respawn tracking"
```

---

## Task 4: Screen Capture Engine

**Files:**
- Create: `deadlock-companion/src/capture.py`
- Create: `deadlock-companion/tests/test_capture.py`

- [ ] **Step 1: Write failing tests for capture engine**

Create `deadlock-companion/tests/test_capture.py`:
```python
import numpy as np
from unittest.mock import patch, MagicMock
from src.capture import CaptureEngine


def test_capture_returns_numpy_array():
    region = {"x": 0, "y": 0, "width": 100, "height": 100}
    engine = CaptureEngine(region)

    # Mock mss to return a fake screenshot
    fake_pixels = np.zeros((100, 100, 4), dtype=np.uint8)
    mock_sct = MagicMock()
    mock_monitor = {"left": 0, "top": 0, "width": 100, "height": 100}
    mock_grab = MagicMock()
    mock_grab.__array__ = lambda self: fake_pixels
    mock_sct.grab.return_value = mock_grab

    with patch("mss.mss", return_value=mock_sct):
        frame = engine.capture_frame()

    assert isinstance(frame, np.ndarray)
    assert frame.shape[0] == 100
    assert frame.shape[1] == 100


def test_capture_region_to_monitor():
    region = {"x": 150, "y": 250, "width": 300, "height": 300}
    engine = CaptureEngine(region)
    monitor = engine._region_to_monitor()
    assert monitor == {"left": 150, "top": 250, "width": 300, "height": 300}


def test_update_region():
    region = {"x": 0, "y": 0, "width": 100, "height": 100}
    engine = CaptureEngine(region)
    new_region = {"x": 50, "y": 50, "width": 200, "height": 200}
    engine.update_region(new_region)
    assert engine.region == new_region
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_capture.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.capture'`

- [ ] **Step 3: Implement capture engine**

Create `deadlock-companion/src/capture.py`:
```python
import numpy as np
import mss


class CaptureEngine:
    def __init__(self, region: dict):
        self.region = region

    def _region_to_monitor(self) -> dict:
        return {
            "left": self.region["x"],
            "top": self.region["y"],
            "width": self.region["width"],
            "height": self.region["height"],
        }

    def capture_frame(self) -> np.ndarray:
        monitor = self._region_to_monitor()
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
        # Convert BGRA to BGR (drop alpha channel)
        return frame[:, :, :3]

    def update_region(self, region: dict):
        self.region = region
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_capture.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add deadlock-companion/src/capture.py deadlock-companion/tests/test_capture.py
git commit -m "feat: add screen capture engine using mss"
```

---

## Task 5: Detection Engine

**Files:**
- Create: `deadlock-companion/src/detector.py`
- Create: `deadlock-companion/tests/test_detector.py`

- [ ] **Step 1: Write failing tests for detector**

Create `deadlock-companion/tests/test_detector.py`:
```python
import numpy as np
import cv2
from src.detector import Detector, DetectionResult
from src.models import Objective, ObjectiveType


def _make_test_template(size=30, color=200):
    """Create a small solid-color square as a test template."""
    img = np.full((size, size, 3), color, dtype=np.uint8)
    return img


def _make_test_frame(width=300, height=300, bg_color=50):
    """Create a dark background frame."""
    return np.full((height, width, 3), bg_color, dtype=np.uint8)


def _place_template_in_frame(frame, template, x, y):
    """Place a template at a specific position in the frame."""
    h, w = template.shape[:2]
    result = frame.copy()
    result[y : y + h, x : x + w] = template
    return result


def test_detect_present_icon():
    template = _make_test_template(size=30, color=200)
    frame = _make_test_frame(300, 300, bg_color=50)
    # Place template at position (100, 100)
    frame = _place_template_in_frame(frame, template, 100, 100)

    objective = Objective(
        id="t1_camp_1",
        name="T1 Camp 1",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.33, 0.33),  # roughly where we placed it
        template_name="t1_camp.png",
    )

    detector = Detector(templates={"t1_camp.png": template}, threshold=0.8)
    results = detector.detect(frame, [objective])
    assert len(results) == 1
    assert results[0].objective_id == "t1_camp_1"
    assert results[0].is_present is True
    assert results[0].confidence > 0.8


def test_detect_absent_icon():
    template = _make_test_template(size=30, color=200)
    frame = _make_test_frame(300, 300, bg_color=50)
    # Do NOT place the template in the frame

    objective = Objective(
        id="t1_camp_1",
        name="T1 Camp 1",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.33, 0.33),
        template_name="t1_camp.png",
    )

    detector = Detector(templates={"t1_camp.png": template}, threshold=0.8)
    results = detector.detect(frame, [objective])
    assert len(results) == 1
    assert results[0].is_present is False
    assert results[0].confidence < 0.8


def test_detect_multiple_objectives():
    t1_template = _make_test_template(size=30, color=200)
    sinner_template = _make_test_template(size=30, color=150)
    frame = _make_test_frame(300, 300, bg_color=50)
    frame = _place_template_in_frame(frame, t1_template, 50, 50)
    # sinner NOT placed

    objectives = [
        Objective(
            id="t1_camp_1", name="T1 Camp 1",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.17, 0.17), template_name="t1_camp.png",
        ),
        Objective(
            id="sinner_1", name="Sinner 1",
            objective_type=ObjectiveType.SINNER,
            position=(0.50, 0.50), template_name="sinner.png",
        ),
    ]

    detector = Detector(
        templates={"t1_camp.png": t1_template, "sinner.png": sinner_template},
        threshold=0.8,
    )
    results = detector.detect(frame, objectives)
    results_by_id = {r.objective_id: r for r in results}
    assert results_by_id["t1_camp_1"].is_present is True
    assert results_by_id["sinner_1"].is_present is False


def test_is_minimap_visible_all_gone():
    template = _make_test_template(size=30, color=200)
    frame = _make_test_frame(300, 300, bg_color=50)

    objectives = [
        Objective(
            id="t1_camp_1", name="T1 Camp 1",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.17, 0.17), template_name="t1_camp.png",
        ),
        Objective(
            id="t1_camp_2", name="T1 Camp 2",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.50, 0.50), template_name="t1_camp.png",
        ),
    ]

    detector = Detector(templates={"t1_camp.png": template}, threshold=0.8)
    results = detector.detect(frame, objectives)
    assert detector.is_minimap_visible(results) is False


def test_is_minimap_visible_some_present():
    template = _make_test_template(size=30, color=200)
    frame = _make_test_frame(300, 300, bg_color=50)
    frame = _place_template_in_frame(frame, template, 50, 50)

    objectives = [
        Objective(
            id="t1_camp_1", name="T1 Camp 1",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.17, 0.17), template_name="t1_camp.png",
        ),
        Objective(
            id="t1_camp_2", name="T1 Camp 2",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.50, 0.50), template_name="t1_camp.png",
        ),
    ]

    detector = Detector(templates={"t1_camp.png": template}, threshold=0.8)
    results = detector.detect(frame, objectives)
    assert detector.is_minimap_visible(results) is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.detector'`

- [ ] **Step 3: Implement detector**

Create `deadlock-companion/src/detector.py`:
```python
import cv2
import numpy as np
from dataclasses import dataclass
from src.models import Objective


@dataclass
class DetectionResult:
    objective_id: str
    is_present: bool
    confidence: float


class Detector:
    def __init__(self, templates: dict[str, np.ndarray], threshold: float = 0.8):
        self.templates = templates
        self.threshold = threshold

    def detect(self, frame: np.ndarray, objectives: list[Objective]) -> list[DetectionResult]:
        results = []
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for obj in objectives:
            template = self.templates.get(obj.template_name)
            if template is None:
                results.append(DetectionResult(obj.id, False, 0.0))
                continue

            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # Search in a sub-region around the expected position to improve
            # speed and reduce false positives
            search_region, offset = self._get_search_region(
                gray_frame, obj.position, template.shape
            )

            match = cv2.matchTemplate(search_region, gray_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(match)

            results.append(DetectionResult(
                objective_id=obj.id,
                is_present=max_val >= self.threshold,
                confidence=float(max_val),
            ))

        return results

    def _get_search_region(
        self, frame: np.ndarray, position: tuple[float, float], template_shape: tuple
    ) -> tuple[np.ndarray, tuple[int, int]]:
        h, w = frame.shape[:2]
        th, tw = template_shape[:2]

        # Center of expected position
        cx = int(position[0] * w)
        cy = int(position[1] * h)

        # Search area: 3x template size around expected position
        margin = max(tw, th) * 2
        x1 = max(0, cx - margin)
        y1 = max(0, cy - margin)
        x2 = min(w, cx + margin)
        y2 = min(h, cy + margin)

        # Ensure search region is at least as large as template
        if (x2 - x1) < tw or (y2 - y1) < th:
            return frame, (0, 0)

        return frame[y1:y2, x1:x2], (x1, y1)

    def is_minimap_visible(self, results: list[DetectionResult]) -> bool:
        if not results:
            return False
        return any(r.is_present for r in results)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add deadlock-companion/src/detector.py deadlock-companion/tests/test_detector.py
git commit -m "feat: add OpenCV template matching detection engine"
```

---

## Task 6: Calibration Overlay

**Files:**
- Create: `deadlock-companion/src/calibration.py`

Note: This uses tkinter for a GUI overlay — not unit-testable in headless CI. We'll test it manually.

- [ ] **Step 1: Implement calibration overlay**

Create `deadlock-companion/src/calibration.py`:
```python
import tkinter as tk
from typing import Optional


def select_region() -> Optional[dict]:
    """Show a fullscreen transparent overlay and let user drag a rectangle.
    Returns {"x": int, "y": int, "width": int, "height": int} or None if cancelled.
    """
    result = {"region": None}

    root = tk.Tk()
    root.title("Deadlock Companion — Select Minimap Region")
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    canvas = tk.Canvas(root, cursor="crosshair", bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = 0
    start_y = 0
    rect_id = None

    instruction = canvas.create_text(
        root.winfo_screenwidth() // 2,
        50,
        text="Drag a rectangle over your minimap. Press Escape to cancel.",
        fill="white",
        font=("Arial", 24),
    )

    def on_press(event):
        nonlocal start_x, start_y, rect_id
        start_x = event.x
        start_y = event.y
        if rect_id:
            canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(
            start_x, start_y, start_x, start_y,
            outline="lime", width=3,
        )

    def on_drag(event):
        nonlocal rect_id
        if rect_id:
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_release(event):
        x1 = min(start_x, event.x)
        y1 = min(start_y, event.y)
        x2 = max(start_x, event.x)
        y2 = max(start_y, event.y)
        width = x2 - x1
        height = y2 - y1
        if width > 10 and height > 10:
            result["region"] = {
                "x": x1,
                "y": y1,
                "width": width,
                "height": height,
            }
        root.destroy()

    def on_escape(event):
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)

    root.mainloop()
    return result["region"]
```

- [ ] **Step 2: Smoke-test manually**

```bash
python -c "from src.calibration import select_region; print(select_region())"
```

Expected: A fullscreen dark overlay appears. Drag a rectangle and release — coordinates print to console. Press Escape to cancel.

- [ ] **Step 3: Commit**

```bash
git add deadlock-companion/src/calibration.py
git commit -m "feat: add tkinter calibration overlay for minimap region selection"
```

---

## Task 7: WebSocket Server & API

**Files:**
- Create: `deadlock-companion/src/server.py`
- Create: `deadlock-companion/tests/test_server.py`

- [ ] **Step 1: Write failing tests for server**

Create `deadlock-companion/tests/test_server.py`:
```python
import pytest
from fastapi.testclient import TestClient
from src.server import create_app
from src.models import Objective, ObjectiveType
from src.timers import TimerManager


def _make_timer_manager():
    objectives = [
        Objective(
            id="t1_camp_1", name="T1 Camp 1",
            objective_type=ObjectiveType.T1_CAMP,
            position=(0.25, 0.40), template_name="t1_camp.png",
        ),
    ]
    return TimerManager(objectives)


def test_health_endpoint():
    mgr = _make_timer_manager()
    app = create_app(mgr)
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_state_endpoint():
    mgr = _make_timer_manager()
    mgr.start_match()
    app = create_app(mgr)
    client = TestClient(app)
    resp = client.get("/api/state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_state"] == "active"
    assert len(data["objectives"]) == 1
    assert data["objectives"][0]["id"] == "t1_camp_1"


def test_toggle_endpoint():
    mgr = _make_timer_manager()
    mgr.start_match()
    app = create_app(mgr)
    client = TestClient(app)
    resp = client.post("/api/toggle/t1_camp_1")
    assert resp.status_code == 200
    obj = mgr.get_objective("t1_camp_1")
    assert obj.state.value == "dead"


def test_calibrate_endpoint():
    mgr = _make_timer_manager()
    app = create_app(mgr)
    client = TestClient(app)
    resp = client.get("/api/needs-calibration")
    assert resp.status_code == 200


def test_static_index(tmp_path):
    # Create a minimal index.html for testing
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html>test</html>")

    mgr = _make_timer_manager()
    app = create_app(mgr, static_dir=str(static_dir))
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_server.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.server'`

- [ ] **Step 3: Implement server**

Create `deadlock-companion/src/server.py`:
```python
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.timers import TimerManager


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                pass


def create_app(
    timer_manager: TimerManager,
    static_dir: str | None = None,
) -> FastAPI:
    app = FastAPI(title="Deadlock Companion")
    ws_manager = ConnectionManager()
    app.state.ws_manager = ws_manager
    app.state.timer_manager = timer_manager

    if static_dir is None:
        static_dir = str(Path(__file__).parent.parent / "static")

    @app.get("/api/health")
    def health():
        return {"status": "healthy"}

    @app.get("/api/state")
    def get_state():
        return {
            "match_state": timer_manager.match_state.value,
            "objectives": timer_manager.get_all_states(),
        }

    @app.post("/api/toggle/{objective_id}")
    def toggle_objective(objective_id: str):
        timer_manager.toggle_manual(objective_id)
        return {"ok": True}

    @app.get("/api/needs-calibration")
    def needs_calibration():
        return {"needs_calibration": True}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "toggle":
                    timer_manager.toggle_manual(msg["id"])
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    static_path = Path(static_dir)
    if static_path.exists():
        @app.get("/")
        def index():
            return FileResponse(static_path / "index.html")

        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_server.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add deadlock-companion/src/server.py deadlock-companion/tests/test_server.py
git commit -m "feat: add FastAPI server with WebSocket and REST endpoints"
```

---

## Task 8: Web UI — Minimap with Objective Markers

**Files:**
- Create: `deadlock-companion/static/index.html`
- Create: `deadlock-companion/static/style.css`
- Create: `deadlock-companion/static/app.js`

- [ ] **Step 1: Create the HTML shell**

Create `deadlock-companion/static/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deadlock Companion</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div id="top-bar">
        <span id="status-indicator" class="disconnected"></span>
        <span id="status-text">Disconnected</span>
        <span id="match-state">Idle</span>
        <button id="recalibrate-btn">Recalibrate</button>
    </div>

    <div id="minimap-container">
        <div id="minimap">
            <div id="minimap-bg"></div>
            <div id="markers"></div>
        </div>
        <div id="waiting-overlay" class="hidden">
            <span>Waiting for match...</span>
        </div>
        <div id="calibration-overlay" class="hidden">
            <span>Calibration needed</span>
            <button id="calibrate-btn">Calibrate Minimap</button>
        </div>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create the CSS**

Create `deadlock-companion/static/style.css`:
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

#top-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    background: #15151f;
    border-bottom: 1px solid #2a2a3a;
    flex-shrink: 0;
}

#status-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

#status-indicator.connected { background: #4ade80; }
#status-indicator.disconnected { background: #ef4444; }

#match-state {
    margin-left: auto;
    font-size: 14px;
    color: #888;
}

#recalibrate-btn {
    padding: 4px 12px;
    background: #2a2a3a;
    color: #ccc;
    border: 1px solid #3a3a4a;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
}

#recalibrate-btn:hover { background: #3a3a4a; }

#minimap-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 20px;
}

#minimap {
    position: relative;
    width: min(80vh, 80vw);
    height: min(80vh, 80vw);
    border-radius: 50%;
    background: #1a1a2e;
    border: 2px solid #2a2a4a;
    overflow: hidden;
}

#minimap-bg {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: radial-gradient(circle, #1a1a2e 0%, #0d0d1a 100%);
}

.marker {
    position: absolute;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transform: translate(-50%, -50%);
    transition: background-color 0.3s ease;
    z-index: 10;
    font-size: 10px;
    font-weight: bold;
    color: #000;
    user-select: none;
}

.marker .timer-label {
    position: absolute;
    bottom: -16px;
    font-size: 11px;
    color: #fff;
    white-space: nowrap;
    text-shadow: 0 0 4px #000;
}

.marker .tooltip {
    display: none;
    position: absolute;
    top: -30px;
    background: #222;
    color: #fff;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    white-space: nowrap;
    z-index: 20;
}

.marker:hover .tooltip { display: block; }

/* State colors */
.marker.alive { background: #4ade80; }
.marker.dead-full { background: #ef4444; }
.marker.dead-high { background: #eab308; }
.marker.dead-low { background: #f97316; }
.marker.respawning-soon {
    background: #4ade80;
    animation: pulse 0.8s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    50% { opacity: 0.5; transform: translate(-50%, -50%) scale(1.2); }
}

/* Marker shapes by type */
.marker[data-type="t1_camp"] { border-radius: 50%; width: 22px; height: 22px; }
.marker[data-type="t2_camp"] { border-radius: 3px; width: 26px; height: 26px; }
.marker[data-type="t3_camp"] { border-radius: 3px; width: 32px; height: 32px; }
.marker[data-type="sinner"] { border-radius: 50%; width: 28px; height: 28px; border: 2px solid #a855f7; }
.marker[data-type="bridge_buff"] {
    width: 24px;
    height: 24px;
    transform: translate(-50%, -50%) rotate(45deg);
}
.marker[data-type="bridge_buff"] .timer-label {
    transform: rotate(-45deg);
}
.marker[data-type="bridge_buff"] .tooltip {
    transform: rotate(-45deg);
}

/* Overlays */
#waiting-overlay,
#calibration-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.7);
    border-radius: 50%;
    z-index: 50;
    gap: 16px;
    font-size: 20px;
}

#calibrate-btn {
    padding: 10px 24px;
    background: #4ade80;
    color: #000;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    font-weight: bold;
}

.hidden { display: none !important; }
```

- [ ] **Step 3: Create the JavaScript**

Create `deadlock-companion/static/app.js`:
```javascript
const RECONNECT_DELAY = 2000;

let ws = null;
let objectives = [];

function connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        document.getElementById("status-indicator").className = "connected";
        document.getElementById("status-text").textContent = "Connected";
    };

    ws.onclose = () => {
        document.getElementById("status-indicator").className = "disconnected";
        document.getElementById("status-text").textContent = "Disconnected";
        setTimeout(connect, RECONNECT_DELAY);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleUpdate(data);
    };
}

function handleUpdate(data) {
    const matchState = data.match_state;
    document.getElementById("match-state").textContent =
        matchState === "active" ? "Match Active" : "Idle";

    const waitingOverlay = document.getElementById("waiting-overlay");
    if (matchState === "idle") {
        waitingOverlay.classList.remove("hidden");
    } else {
        waitingOverlay.classList.add("hidden");
    }

    objectives = data.objectives;
    renderMarkers();
}

function renderMarkers() {
    const container = document.getElementById("markers");
    container.innerHTML = "";

    for (const obj of objectives) {
        const marker = document.createElement("div");
        marker.className = `marker ${getStateClass(obj)}`;
        marker.dataset.type = obj.type;

        // Position as percentage of minimap
        marker.style.left = `${obj.position[0] * 100}%`;
        marker.style.top = `${obj.position[1] * 100}%`;

        // Tooltip
        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.textContent = obj.name;
        marker.appendChild(tooltip);

        // Timer label
        if (obj.remaining_seconds != null) {
            const label = document.createElement("div");
            label.className = "timer-label";
            label.textContent = formatTime(obj.remaining_seconds);
            marker.appendChild(label);
        }

        // Type icon text
        const icons = {
            t1_camp: "1",
            t2_camp: "2",
            t3_camp: "3",
            sinner: "S",
            bridge_buff: "B",
        };
        marker.insertBefore(
            document.createTextNode(icons[obj.type] || "?"),
            marker.firstChild
        );

        // Right-click to manually toggle
        marker.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            toggleObjective(obj.id);
        });

        container.appendChild(marker);
    }
}

function getStateClass(obj) {
    if (obj.state === "alive") return "alive";
    if (obj.remaining_seconds == null) return "alive";

    const ratio = obj.remaining_seconds / obj.respawn_total;

    if (obj.remaining_seconds <= 15) return "respawning-soon";
    if (ratio > 0.75) return "dead-full";
    if (ratio > 0.5) return "dead-high";
    return "dead-low";
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
}

function toggleObjective(id) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle", id: id }));
    }
}

// Recalibrate button
document.getElementById("recalibrate-btn").addEventListener("click", () => {
    fetch("/api/recalibrate", { method: "POST" });
});

// Poll state on load as fallback
async function pollState() {
    try {
        const resp = await fetch("/api/state");
        const data = await resp.json();
        handleUpdate(data);
    } catch (e) {
        // Server not ready yet
    }
}

// Initial load
pollState();
connect();
```

- [ ] **Step 4: Commit**

```bash
git add deadlock-companion/static/
git commit -m "feat: add web UI with minimap markers and timer display"
```

---

## Task 9: Objective Registry — Map All Objective Positions

**Files:**
- Create: `deadlock-companion/src/objectives.py`

This task defines all tracked objectives with their positions on the minimap. Positions are expressed as (x%, y%) relative to the minimap circle — (0,0) is top-left, (1,1) is bottom-right. These positions will need to be refined once we have high-resolution minimap screenshots, but this establishes the structure.

- [ ] **Step 1: Create objective registry**

Create `deadlock-companion/src/objectives.py`:
```python
from src.models import Objective, ObjectiveType


def get_all_objectives() -> list[Objective]:
    """Return all tracked objectives with their minimap positions.

    Positions are (x%, y%) relative to the minimap bounding box.
    (0, 0) = top-left, (1, 1) = bottom-right.
    These are approximate and should be refined with high-res screenshots.
    """
    objectives = []

    # --- T1 Neutral Camps (1 arrow) ---
    t1_camps = [
        ("t1_camp_nw", "T1 Camp NW", (0.22, 0.38)),
        ("t1_camp_ne", "T1 Camp NE", (0.78, 0.38)),
        ("t1_camp_w", "T1 Camp W", (0.18, 0.55)),
        ("t1_camp_e", "T1 Camp E", (0.82, 0.55)),
        ("t1_camp_sw", "T1 Camp SW", (0.28, 0.72)),
        ("t1_camp_se", "T1 Camp SE", (0.72, 0.72)),
    ]
    for id_, name, pos in t1_camps:
        objectives.append(Objective(
            id=id_, name=name,
            objective_type=ObjectiveType.T1_CAMP,
            position=pos, template_name="t1_camp.png",
        ))

    # --- T2 Neutral Camps (2 arrows) ---
    t2_camps = [
        ("t2_camp_nw", "T2 Camp NW", (0.30, 0.30)),
        ("t2_camp_ne", "T2 Camp NE", (0.70, 0.30)),
        ("t2_camp_sw", "T2 Camp SW", (0.30, 0.70)),
        ("t2_camp_se", "T2 Camp SE", (0.70, 0.70)),
    ]
    for id_, name, pos in t2_camps:
        objectives.append(Objective(
            id=id_, name=name,
            objective_type=ObjectiveType.T2_CAMP,
            position=pos, template_name="t2_camp.png",
        ))

    # --- T3 Neutral Camps (3 arrows) ---
    t3_camps = [
        ("t3_camp_w", "T3 Camp W", (0.20, 0.50)),
        ("t3_camp_e", "T3 Camp E", (0.80, 0.50)),
    ]
    for id_, name, pos in t3_camps:
        objectives.append(Objective(
            id=id_, name=name,
            objective_type=ObjectiveType.T3_CAMP,
            position=pos, template_name="t3_camp.png",
        ))

    # --- Sinner's Sacrifice ---
    sinners = [
        ("sinner_nw", "Sinner NW", (0.25, 0.35)),
        ("sinner_n", "Sinner N", (0.50, 0.20)),
        ("sinner_ne", "Sinner NE", (0.75, 0.35)),
        ("sinner_w", "Sinner W", (0.15, 0.50)),
        ("sinner_e", "Sinner E", (0.85, 0.50)),
        ("sinner_sw", "Sinner SW", (0.25, 0.65)),
        ("sinner_s", "Sinner S", (0.50, 0.80)),
        ("sinner_se", "Sinner SE", (0.75, 0.65)),
    ]
    for id_, name, pos in sinners:
        objectives.append(Objective(
            id=id_, name=name,
            objective_type=ObjectiveType.SINNER,
            position=pos, template_name="sinner.png",
        ))

    # --- Bridge Buffs ---
    bridge_buffs = [
        ("bridge_buff_w", "Bridge Buff West", (0.30, 0.50)),
        ("bridge_buff_e", "Bridge Buff East", (0.70, 0.50)),
    ]
    for id_, name, pos in bridge_buffs:
        objectives.append(Objective(
            id=id_, name=name,
            objective_type=ObjectiveType.BRIDGE_BUFF,
            position=pos, template_name="bridge_buff.png",
        ))

    return objectives
```

- [ ] **Step 2: Quick verification**

```bash
python -c "from src.objectives import get_all_objectives; objs = get_all_objectives(); print(f'{len(objs)} objectives registered'); [print(f'  {o.id}: {o.objective_type.key} at {o.position}') for o in objs]"
```

Expected: Prints all objectives with their positions.

- [ ] **Step 3: Commit**

```bash
git add deadlock-companion/src/objectives.py
git commit -m "feat: add objective registry with minimap positions"
```

---

## Task 10: Main Loop — Wire Everything Together

**Files:**
- Modify: `deadlock-companion/src/main.py`
- Modify: `deadlock-companion/src/server.py`

- [ ] **Step 1: Implement the main loop**

Replace `deadlock-companion/src/main.py` with:
```python
"""Deadlock Companion — Objective Timer App entry point."""

import asyncio
import sys
import time
import threading
import webbrowser
from pathlib import Path

import uvicorn

from src.calibration import select_region
from src.capture import CaptureEngine
from src.config import Config
from src.detector import Detector, DetectionResult
from src.models import MatchState, ObjectiveState
from src.objectives import get_all_objectives
from src.server import create_app
from src.timers import TimerManager


def load_templates(templates_dir: Path) -> dict:
    """Load reference template images from the templates directory."""
    import cv2
    templates = {}
    for path in templates_dir.glob("*.png"):
        img = cv2.imread(str(path))
        if img is not None:
            templates[path.name] = img
    return templates


def detection_loop(
    capture_engine: CaptureEngine,
    detector: Detector,
    timer_manager: TimerManager,
    config: Config,
    app_state: dict,
):
    """Run the capture → detect → update loop in a background thread."""
    ACTIVE_FPS = 2
    IDLE_FPS = 0.5

    while app_state["running"]:
        fps = ACTIVE_FPS if timer_manager.match_state == MatchState.ACTIVE else IDLE_FPS
        interval = 1.0 / fps

        if config.capture_region is None:
            time.sleep(1)
            continue

        try:
            frame = capture_engine.capture_frame()
            objectives = timer_manager.objectives
            results = detector.detect(frame, objectives)

            minimap_visible = detector.is_minimap_visible(results)

            if minimap_visible and timer_manager.match_state == MatchState.IDLE:
                timer_manager.start_match()
            elif not minimap_visible and timer_manager.match_state == MatchState.ACTIVE:
                timer_manager.end_match()

            if timer_manager.match_state == MatchState.ACTIVE:
                for result in results:
                    obj = timer_manager.get_objective(result.objective_id)
                    if obj is None:
                        continue
                    if not result.is_present and obj.state == ObjectiveState.ALIVE:
                        timer_manager.mark_killed(result.objective_id)
                    elif result.is_present and obj.state == ObjectiveState.DEAD:
                        timer_manager.mark_respawned(result.objective_id)

            timer_manager.update()

        except Exception as e:
            print(f"Detection error: {e}")

        time.sleep(interval)


async def broadcast_loop(app):
    """Periodically broadcast state to all WebSocket clients."""
    while True:
        timer_manager = app.state.timer_manager
        ws_manager = app.state.ws_manager
        timer_manager.update()
        state = {
            "match_state": timer_manager.match_state.value,
            "objectives": timer_manager.get_all_states(),
        }
        await ws_manager.broadcast(state)
        await asyncio.sleep(0.5)


def main():
    config = Config()
    objectives = get_all_objectives()
    timer_manager = TimerManager(objectives)

    templates_dir = Path(__file__).parent.parent / "templates"
    templates = load_templates(templates_dir)

    if not templates:
        print("Warning: No template images found in templates/ directory.")
        print("Detection will not work until templates are added.")
        print("The UI will still work with manual toggle (right-click markers).")

    detector = Detector(templates=templates)

    capture_region = config.capture_region or {"x": 0, "y": 0, "width": 100, "height": 100}
    capture_engine = CaptureEngine(capture_region)

    app = create_app(timer_manager, config=config)
    app_state = {"running": True}

    # Add recalibrate endpoint
    @app.post("/api/recalibrate")
    def recalibrate():
        region = select_region()
        if region:
            config.capture_region = region
            config.save()
            capture_engine.update_region(region)
            return {"ok": True, "region": region}
        return {"ok": False}

    # Start detection thread
    detection_thread = threading.Thread(
        target=detection_loop,
        args=(capture_engine, detector, timer_manager, config, app_state),
        daemon=True,
    )
    detection_thread.start()

    # Start broadcast as background task
    @app.on_event("startup")
    async def startup():
        asyncio.create_task(broadcast_loop(app))
        # Open browser after short delay
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8080")).start()

    print("Starting Deadlock Companion on http://localhost:8080")

    if config.needs_calibration:
        print("First run detected — calibrate your minimap in the browser.")

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="warning")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Update server.py to accept config**

Add the `config` parameter to `create_app` in `deadlock-companion/src/server.py`. Replace the function signature and the `needs_calibration` endpoint:

```python
def create_app(
    timer_manager: TimerManager,
    static_dir: str | None = None,
    config=None,
) -> FastAPI:
    app = FastAPI(title="Deadlock Companion")
    ws_manager = ConnectionManager()
    app.state.ws_manager = ws_manager
    app.state.timer_manager = timer_manager

    if static_dir is None:
        static_dir = str(Path(__file__).parent.parent / "static")

    @app.get("/api/health")
    def health():
        return {"status": "healthy"}

    @app.get("/api/state")
    def get_state():
        return {
            "match_state": timer_manager.match_state.value,
            "objectives": timer_manager.get_all_states(),
        }

    @app.post("/api/toggle/{objective_id}")
    def toggle_objective(objective_id: str):
        timer_manager.toggle_manual(objective_id)
        return {"ok": True}

    @app.get("/api/needs-calibration")
    def needs_calibration():
        needs = config.needs_calibration if config else True
        return {"needs_calibration": needs}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "toggle":
                    timer_manager.toggle_manual(msg["id"])
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    static_path = Path(static_dir)
    if static_path.exists():
        @app.get("/")
        def index():
            return FileResponse(static_path / "index.html")

        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
```

- [ ] **Step 3: Run all tests to verify nothing is broken**

```bash
python -m pytest tests/ -v
```

Expected: All existing tests PASS.

- [ ] **Step 4: Commit**

```bash
git add deadlock-companion/src/main.py deadlock-companion/src/server.py
git commit -m "feat: wire up main loop with detection, timers, and broadcast"
```

---

## Task 11: PyInstaller Build Configuration

**Files:**
- Create: `deadlock-companion/build.spec`
- Create: `deadlock-companion/build.py`

- [ ] **Step 1: Add PyInstaller to requirements**

Append to `deadlock-companion/requirements.txt`:
```
pyinstaller==6.11.1
```

Install:
```bash
pip install pyinstaller==6.11.1
```

- [ ] **Step 2: Create build script**

Create `deadlock-companion/build.py`:
```python
"""Build script for creating the standalone exe."""
import PyInstaller.__main__
from pathlib import Path

root = Path(__file__).parent

PyInstaller.__main__.run([
    str(root / "src" / "main.py"),
    "--name=deadlock-companion",
    "--onefile",
    "--noconsole",
    f"--add-data={root / 'static'};static",
    f"--add-data={root / 'templates'};templates",
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.protocols.websockets",
    "--hidden-import=uvicorn.protocols.websockets.auto",
    "--hidden-import=uvicorn.lifespan",
    "--hidden-import=uvicorn.lifespan.on",
])
```

- [ ] **Step 3: Test the build (won't produce working exe without templates, but verifies bundling)**

```bash
cd deadlock-companion
python build.py
```

Expected: Build completes. `dist/deadlock-companion.exe` is created.

- [ ] **Step 4: Commit**

```bash
git add deadlock-companion/build.py deadlock-companion/requirements.txt
git commit -m "feat: add PyInstaller build configuration"
```

---

## Task 12: Template Image Extraction

**Files:**
- Create: `deadlock-companion/tools/extract_templates.py`
- Create: placeholder files in `deadlock-companion/templates/`

This task creates a helper tool for extracting reference icon templates from high-resolution minimap screenshots. The user will provide full-res screenshots, and this tool will help crop individual icons.

- [ ] **Step 1: Create template extraction tool**

Create `deadlock-companion/tools/extract_templates.py`:
```python
"""Interactive tool to extract objective icon templates from a minimap screenshot.

Usage:
    python tools/extract_templates.py path/to/screenshot.png

Click on each objective icon center when prompted. Press 'q' to skip.
Extracted templates are saved to the templates/ directory.
"""

import sys
from pathlib import Path
import cv2
import numpy as np


TEMPLATE_SIZE = 40  # Size of the crop around each icon (pixels)

OBJECTIVES_TO_EXTRACT = [
    ("t1_camp.png", "Click on a T1 camp icon (small, 1 arrow)"),
    ("t2_camp.png", "Click on a T2 camp icon (medium, 2 arrows)"),
    ("t3_camp.png", "Click on a T3 camp icon (large, 3 arrows)"),
    ("sinner.png", "Click on a Sinner's Sacrifice icon"),
    ("bridge_buff.png", "Click on a Bridge Buff icon"),
]


def extract_template(image: np.ndarray, center_x: int, center_y: int, size: int) -> np.ndarray:
    half = size // 2
    h, w = image.shape[:2]
    x1 = max(0, center_x - half)
    y1 = max(0, center_y - half)
    x2 = min(w, center_x + half)
    y2 = min(h, center_y + half)
    return image[y1:y2, x1:x2].copy()


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/extract_templates.py path/to/screenshot.png")
        sys.exit(1)

    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image: {image_path}")
        sys.exit(1)

    templates_dir = Path(__file__).parent.parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    click_pos = {"x": -1, "y": -1}

    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            click_pos["x"] = x
            click_pos["y"] = y

    window_name = "Template Extractor"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, on_click)

    for filename, prompt in OBJECTIVES_TO_EXTRACT:
        print(f"\n{prompt}")
        print("Left-click on the icon center. Press 'q' to skip, 's' to save.")

        display = image.copy()
        cv2.putText(display, prompt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(window_name, display)

        click_pos["x"] = -1
        click_pos["y"] = -1

        while True:
            key = cv2.waitKey(50) & 0xFF
            if key == ord("q"):
                print(f"  Skipped {filename}")
                break
            if click_pos["x"] >= 0:
                template = extract_template(image, click_pos["x"], click_pos["y"], TEMPLATE_SIZE)
                out_path = templates_dir / filename
                cv2.imwrite(str(out_path), template)
                print(f"  Saved {filename} ({template.shape[1]}x{template.shape[0]})")

                # Show what was extracted
                preview = image.copy()
                half = TEMPLATE_SIZE // 2
                cv2.rectangle(
                    preview,
                    (click_pos["x"] - half, click_pos["y"] - half),
                    (click_pos["x"] + half, click_pos["y"] + half),
                    (0, 255, 0), 2,
                )
                cv2.imshow(window_name, preview)
                cv2.waitKey(1000)
                break

    cv2.destroyAllWindows()
    print("\nDone! Check templates/ directory.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create placeholder template files**

```bash
mkdir -p deadlock-companion/templates
mkdir -p deadlock-companion/tools
```

Create a `deadlock-companion/templates/README.md`:
```markdown
# Template Images

This directory contains reference template images used for detecting objectives on the minimap.

## How to generate templates

1. Launch Deadlock and start a match
2. Take a high-resolution screenshot when the minimap is fully visible with objectives
3. Run the extraction tool:
   ```bash
   python tools/extract_templates.py path/to/screenshot.png
   ```
4. Click on each objective icon when prompted
5. Templates are saved here automatically

## Required templates

- `t1_camp.png` — T1 neutral camp icon (small, 1 arrow)
- `t2_camp.png` — T2 neutral camp icon (medium, 2 arrows)
- `t3_camp.png` — T3 neutral camp icon (large, 3 arrows)
- `sinner.png` — Sinner's Sacrifice icon
- `bridge_buff.png` — Bridge Buff icon
```

- [ ] **Step 3: Commit**

```bash
git add deadlock-companion/tools/ deadlock-companion/templates/
git commit -m "feat: add template extraction tool and templates directory"
```

---

## Task 13: README and Documentation

**Files:**
- Create: `deadlock-companion/README.md`

- [ ] **Step 1: Write README**

Create `deadlock-companion/README.md`:
```markdown
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
3. Click **Calibrate Minimap** and drag a rectangle over your in-game minimap
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

```bash
python tools/extract_templates.py path/to/minimap-screenshot.png
```

## How It Works

1. **Screen Capture** — captures a user-defined region of the screen at ~2 FPS using `mss`
2. **Detection** — uses OpenCV template matching to detect objective icon presence/absence
3. **Timers** — when an icon disappears, starts a countdown based on the objective type
4. **UI** — pushes state over WebSocket to a browser-based minimap display
```

- [ ] **Step 2: Commit**

```bash
git add deadlock-companion/README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

## Summary

| Task | Component | Tests |
|------|-----------|-------|
| 1 | Project scaffolding + data models | 4 tests |
| 2 | Configuration management | 5 tests |
| 3 | Timer state management | 9 tests |
| 4 | Screen capture engine | 3 tests |
| 5 | Detection engine | 5 tests |
| 6 | Calibration overlay | Manual |
| 7 | WebSocket server & API | 5 tests |
| 8 | Web UI (HTML/CSS/JS) | Manual |
| 9 | Objective registry | Manual verify |
| 10 | Main loop wiring | Integration |
| 11 | PyInstaller build | Build verify |
| 12 | Template extraction tool | Manual |
| 13 | README | N/A |

**Total: 13 tasks, 31 automated tests**
