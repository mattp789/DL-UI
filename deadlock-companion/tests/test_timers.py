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
