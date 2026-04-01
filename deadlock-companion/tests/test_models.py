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
