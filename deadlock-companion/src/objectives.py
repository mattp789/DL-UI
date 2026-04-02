"""Objective registry — all tracked objectives with minimap positions."""
from typing import Optional

from src.models import Objective, ObjectiveType


def get_all_objectives(positions: Optional[dict] = None) -> list[Objective]:
    """Return all tracked objectives with their minimap positions.

    Positions are (x%, y%) relative to the minimap bounding box.
    (0, 0) = top-left, (1, 1) = bottom-right.

    Args:
        positions: Optional dict mapping type keys (e.g. ``"t1_camp"``) to
            lists of ``(x_pct, y_pct)`` tuples from click-to-calibrate.  When
            a type key is present in *positions*, those coordinates are used
            instead of the built-in hardcoded ones.  If ``None`` (default) or
            a key is absent, the hardcoded approximate positions are used so
            that backward-compatibility is maintained.

    Returns:
        A list of :class:`Objective` instances ready for use by the timer
        manager.
    """
    objectives = []

    def _add_type(type_key: str, objective_type: ObjectiveType,
                  template_name: str, display_label: str,
                  hardcoded: list[tuple]) -> None:
        """Append objectives for one type, preferring calibrated positions."""
        calibrated = positions.get(type_key) if positions else None
        if calibrated:
            for i, pos in enumerate(calibrated):
                objectives.append(Objective(
                    id=f"{type_key}_{i}",
                    name=f"{display_label} {i + 1}",
                    objective_type=objective_type,
                    position=tuple(pos),
                    template_name=template_name,
                ))
        else:
            for id_, name, pos in hardcoded:
                objectives.append(Objective(
                    id=id_, name=name,
                    objective_type=objective_type,
                    position=pos, template_name=template_name,
                ))

    # --- T1 Neutral Camps (1 arrow) ---
    _add_type(
        "t1_camp", ObjectiveType.T1_CAMP, "t1_camp.png", "T1 Camp",
        [
            ("t1_camp_nw", "T1 Camp NW", (0.22, 0.38)),
            ("t1_camp_ne", "T1 Camp NE", (0.78, 0.38)),
            ("t1_camp_w",  "T1 Camp W",  (0.18, 0.55)),
            ("t1_camp_e",  "T1 Camp E",  (0.82, 0.55)),
            ("t1_camp_sw", "T1 Camp SW", (0.28, 0.72)),
            ("t1_camp_se", "T1 Camp SE", (0.72, 0.72)),
        ],
    )

    # --- T2 Neutral Camps (2 arrows) ---
    _add_type(
        "t2_camp", ObjectiveType.T2_CAMP, "t2_camp.png", "T2 Camp",
        [
            ("t2_camp_nw", "T2 Camp NW", (0.30, 0.30)),
            ("t2_camp_ne", "T2 Camp NE", (0.70, 0.30)),
            ("t2_camp_sw", "T2 Camp SW", (0.30, 0.70)),
            ("t2_camp_se", "T2 Camp SE", (0.70, 0.70)),
        ],
    )

    # --- T3 Neutral Camps (3 arrows) ---
    _add_type(
        "t3_camp", ObjectiveType.T3_CAMP, "t3_camp.png", "T3 Camp",
        [
            ("t3_camp_w", "T3 Camp W", (0.20, 0.50)),
            ("t3_camp_e", "T3 Camp E", (0.80, 0.50)),
        ],
    )

    # --- Sinner's Sacrifice ---
    _add_type(
        "sinner", ObjectiveType.SINNER, "sinner.png", "Sinner",
        [
            ("sinner_nw", "Sinner NW", (0.25, 0.35)),
            ("sinner_n",  "Sinner N",  (0.50, 0.20)),
            ("sinner_ne", "Sinner NE", (0.75, 0.35)),
            ("sinner_w",  "Sinner W",  (0.15, 0.50)),
            ("sinner_e",  "Sinner E",  (0.85, 0.50)),
            ("sinner_sw", "Sinner SW", (0.25, 0.65)),
            ("sinner_s",  "Sinner S",  (0.50, 0.80)),
            ("sinner_se", "Sinner SE", (0.75, 0.65)),
        ],
    )

    # --- Bridge Buffs ---
    _add_type(
        "bridge_buff", ObjectiveType.BRIDGE_BUFF, "bridge_buff.png", "Bridge Buff",
        [
            ("bridge_buff_w", "Bridge Buff West", (0.30, 0.50)),
            ("bridge_buff_e", "Bridge Buff East", (0.70, 0.50)),
        ],
    )

    return objectives
