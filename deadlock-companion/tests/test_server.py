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


def test_needs_calibration_endpoint():
    mgr = _make_timer_manager()
    app = create_app(mgr)
    client = TestClient(app)
    resp = client.get("/api/needs-calibration")
    assert resp.status_code == 200
    data = resp.json()
    assert "needs_calibration" in data


def test_needs_calibration_with_config(tmp_path):
    from src.config import Config
    config = Config(config_dir=tmp_path)
    config.capture_region = {"x": 0, "y": 0, "width": 100, "height": 100}

    mgr = _make_timer_manager()
    app = create_app(mgr, config=config)
    client = TestClient(app)
    resp = client.get("/api/needs-calibration")
    assert resp.status_code == 200
    data = resp.json()
    assert data["needs_calibration"] is False


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
