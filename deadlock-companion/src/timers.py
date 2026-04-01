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
