import cv2
import numpy as np
from dataclasses import dataclass
from src.models import Objective


@dataclass
class DetectionResult:
    objective_id: str
    is_present: bool
    confidence: float


class Detector:
    def __init__(self, templates: dict[str, np.ndarray], threshold: float = 0.8):
        self.templates = templates
        self.threshold = threshold

    def detect(self, frame: np.ndarray, objectives: list[Objective]) -> list[DetectionResult]:
        results = []
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for obj in objectives:
            template = self.templates.get(obj.template_name)
            if template is None:
                results.append(DetectionResult(obj.id, False, 0.0))
                continue

            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            search_region, offset = self._get_search_region(
                gray_frame, obj.position, template.shape
            )

            match = cv2.matchTemplate(search_region, gray_template, cv2.TM_SQDIFF_NORMED)
            min_val, _, _, _ = cv2.minMaxLoc(match)
            confidence = 1.0 - float(min_val)

            results.append(DetectionResult(
                objective_id=obj.id,
                is_present=confidence >= self.threshold,
                confidence=confidence,
            ))

        return results

    def _get_search_region(
        self, frame: np.ndarray, position: tuple[float, float], template_shape: tuple
    ) -> tuple[np.ndarray, tuple[int, int]]:
        h, w = frame.shape[:2]
        th, tw = template_shape[:2]

        cx = int(position[0] * w)
        cy = int(position[1] * h)

        margin = max(tw, th) * 3
        x1 = max(0, cx - margin)
        y1 = max(0, cy - margin)
        x2 = min(w, cx + margin)
        y2 = min(h, cy + margin)

        if (x2 - x1) < tw or (y2 - y1) < th:
            return frame, (0, 0)

        return frame[y1:y2, x1:x2], (x1, y1)

    def is_minimap_visible(self, results: list[DetectionResult]) -> bool:
        if not results:
            return False
        return any(r.is_present for r in results)
