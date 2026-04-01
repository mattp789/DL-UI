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
