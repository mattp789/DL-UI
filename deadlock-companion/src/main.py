"""Deadlock Companion — Objective Timer App entry point."""

import asyncio
import sys
import time
import threading
import webbrowser
from pathlib import Path

import uvicorn

from src.calibration import select_region, calibrate_positions
from src.resources import get_resource_path
from src.capture import CaptureEngine
from src.config import Config
from src.detector import Detector, DetectionResult
from src.models import MatchState, ObjectiveState
from src.objectives import get_all_objectives
from src.server import create_app
from src.timers import TimerManager


def _pick_template_subdir(templates_dir: Path) -> Path:
    """Select the best-matching resolution subdirectory based on screen height."""
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_h = root.winfo_screenheight()
        root.destroy()
    except Exception:
        screen_h = 1080

    candidates = {
        "1080p": 1080,
        "1440p": 1440,
        "2160p": 2160,
    }
    best = min(candidates, key=lambda k: abs(candidates[k] - screen_h))
    subdir = templates_dir / best
    if subdir.exists():
        return subdir
    return templates_dir


def load_templates(templates_dir: Path) -> dict:
    """Load reference template images from the best-matching resolution subdirectory."""
    import cv2
    subdir = _pick_template_subdir(templates_dir)
    templates = {}
    for path in subdir.glob("*.png"):
        img = cv2.imread(str(path))
        if img is not None:
            templates[path.name] = img
    if templates:
        print(f"Loaded {len(templates)} templates from {subdir.name}/")
    return templates


def detection_loop(
    capture_engine: CaptureEngine,
    detector: Detector,
    timer_manager_holder: dict,
    config: Config,
    app_state: dict,
):
    """Run the capture → detect → update loop in a background thread.

    Args:
        timer_manager_holder: A dict with a ``"tm"`` key holding the current
            :class:`TimerManager`.  The loop reads ``holder["tm"]`` on every
            iteration so that a rebuilt manager (after position recalibration)
            is picked up automatically.
    """
    ACTIVE_FPS = 2
    IDLE_FPS = 0.5

    while app_state["running"]:
        timer_manager = timer_manager_holder["tm"]
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


def _rebuild_timer_manager(
    config: Config,
    timer_manager_holder: dict,
    app,
) -> None:
    """Rebuild the TimerManager from calibrated positions and update app state."""
    objectives = get_all_objectives(config.objective_positions)
    new_tm = TimerManager(objectives)
    timer_manager_holder["tm"] = new_tm
    app.state.timer_manager = new_tm


def main():
    config = Config()

    # Use calibrated positions if already available.
    objectives = get_all_objectives(
        config.objective_positions if not config.needs_position_calibration else None
    )
    timer_manager = TimerManager(objectives)

    # Holder allows the detection loop and recalibration endpoint to share
    # a reference to the current TimerManager even after it is rebuilt.
    timer_manager_holder: dict = {"tm": timer_manager}

    templates_dir = get_resource_path("templates")
    templates = load_templates(templates_dir)

    if not templates:
        print("Warning: No template images found in templates/ directory.")
        print("Detection will not work until templates are added.")
        print("The UI will still work with manual toggle (right-click markers).")

    detector = Detector(templates=templates)

    capture_region = config.capture_region or {"x": 0, "y": 0, "width": 100, "height": 100}
    capture_engine = CaptureEngine(capture_region)

    static_dir = get_resource_path("static")
    app = create_app(timer_manager, static_dir=str(static_dir), config=config)
    app_state = {"running": True}

    @app.post("/api/recalibrate")
    def recalibrate():
        region = select_region()
        if region:
            config.capture_region = region
            config.save()
            capture_engine.update_region(region)

            # Automatically proceed to position calibration when positions
            # have not yet been set.
            if config.needs_position_calibration:
                try:
                    frame = capture_engine.capture_frame()
                    pos_result = calibrate_positions(frame)
                    if pos_result is not None:
                        config.objective_positions = pos_result or None
                        config.save()
                        _rebuild_timer_manager(config, timer_manager_holder, app)
                except Exception as e:
                    print(f"Position calibration error (skipped): {e}")

            return {"ok": True, "region": region}
        return {"ok": False}

    @app.post("/api/recalibrate-positions")
    def recalibrate_positions():
        """Capture a fresh frame and open the position calibration window."""
        try:
            frame = capture_engine.capture_frame()
        except Exception as e:
            return {"ok": False, "error": f"Could not capture frame: {e}"}

        pos_result = calibrate_positions(frame)
        if pos_result is None:
            return {"ok": False, "cancelled": True}

        config.objective_positions = pos_result if pos_result else None
        config.save()
        _rebuild_timer_manager(config, timer_manager_holder, app)
        return {"ok": True, "types_calibrated": list(pos_result.keys())}

    detection_thread = threading.Thread(
        target=detection_loop,
        args=(capture_engine, detector, timer_manager_holder, config, app_state),
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
    elif config.needs_position_calibration:
        print("Minimap region set — use the browser to calibrate objective positions.")

    # When frozen by PyInstaller with --noconsole, stdout/stderr are None.
    # Uvicorn's color formatter calls .isatty() on them and crashes.
    # Disable uvicorn's log config entirely when running as an exe.
    if getattr(sys, "frozen", False):
        log_cfg = None
    else:
        log_cfg = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"default": {"class": "logging.StreamHandler", "stream": "ext://sys.stderr"}},
            "loggers": {"uvicorn": {"handlers": ["default"], "level": "WARNING"}},
        }
    uvicorn.run(app, host="127.0.0.1", port=8080, log_config=log_cfg)


if __name__ == "__main__":
    main()
