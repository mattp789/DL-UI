"""Objective registry — all tracked objectives with minimap positions."""
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
