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

    @app.post("/api/recalibrate")
    def recalibrate():
        region = select_region()
        if region:
            config.capture_region = region
            config.save()
            capture_engine.update_region(region)
            return {"ok": True, "region": region}
        return {"ok": False}

    detection_thread = threading.Thread(
        target=detection_loop,
        args=(capture_engine, detector, timer_manager, config, app_state),
        daemon=True,
    )
    detection_thread.start()

    @app.on_event("startup")
    async def startup():
        asyncio.create_task(broadcast_loop(app))
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8080")).start()

    print("Starting Deadlock Companion on http://localhost:8080")

    if config.needs_calibration:
        print("First run detected — calibrate your minimap in the browser.")

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="warning")


if __name__ == "__main__":
    main()
