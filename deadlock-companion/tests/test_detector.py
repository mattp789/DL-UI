import numpy as np
import cv2
from src.detector import Detector, DetectionResult
from src.models import Objective, ObjectiveType


def _make_test_template(size=30, color=200):
    """Create a template with a distinctive pattern (non-uniform for TM_CCOEFF_NORMED)."""
    img = np.zeros((size, size, 3), dtype=np.uint8)
    # Add a cross pattern that is visually distinct from the background
    img[size//4:3*size//4, size//2, :] = color
    img[size//2, size//4:3*size//4, :] = color
    return img


def _make_test_frame(width=300, height=300, bg_color=50):
    """Create a uniform dark background frame."""
    return np.full((height, width, 3), bg_color, dtype=np.uint8)


def _place_template_in_frame(frame, template, x, y):
    h, w = template.shape[:2]
    result = frame.copy()
    result[y : y + h, x : x + w] = template
    return result


def test_detect_present_icon():
    template = _make_test_template(size=30, color=200)
    frame = _make_test_frame(300, 300, bg_color=50)
    frame = _place_template_in_frame(frame, template, 100, 100)

    objective = Objective(
        id="t1_camp_1", name="T1 Camp 1",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.33, 0.33),
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

    objective = Objective(
        id="t1_camp_1", name="T1 Camp 1",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.33, 0.33),
        template_name="t1_camp.png",
    )

    detector = Detector(templates={"t1_camp.png": template}, threshold=0.8)
    results = detector.detect(frame, [objective])
    assert len(results) == 1
    assert results[0].is_present is False


def test_detect_multiple_objectives():
    t1_template = _make_test_template(size=30, color=200)
    sinner_template = _make_test_template(size=30, color=150)
    frame = _make_test_frame(300, 300, bg_color=50)
    frame = _place_template_in_frame(frame, t1_template, 50, 50)

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


def test_detect_missing_template():
    frame = _make_test_frame(300, 300, bg_color=50)
    objective = Objective(
        id="t1_camp_1", name="T1 Camp 1",
        objective_type=ObjectiveType.T1_CAMP,
        position=(0.33, 0.33),
        template_name="nonexistent.png",
    )
    detector = Detector(templates={}, threshold=0.8)
    results = detector.detect(frame, [objective])
    assert len(results) == 1
    assert results[0].is_present is False
    assert results[0].confidence == 0.0
