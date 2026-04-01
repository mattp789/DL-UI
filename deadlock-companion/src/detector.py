"""Detection engine — OpenCV template matching for objective icon detection."""
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
        self.threshold = threshold
        self._gray_templates: dict[str, np.ndarray] = {
            name: cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)
            for name, t in templates.items()
        }

    def detect(self, frame: np.ndarray, objectives: list[Objective]) -> list[DetectionResult]:
        results = []
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for obj in objectives:
            gray_template = self._gray_templates.get(obj.template_name)
            if gray_template is None:
                results.append(DetectionResult(obj.id, False, 0.0))
                continue

            search_region = self._get_search_region(
                gray_frame, obj.position, gray_template.shape
            )

            match = cv2.matchTemplate(search_region, gray_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(match)
            confidence = float(max_val)

            results.append(DetectionResult(
                objective_id=obj.id,
                is_present=confidence >= self.threshold,
                confidence=confidence,
            ))

        return results

    def _get_search_region(
        self, frame: np.ndarray, position: tuple[float, float], template_shape: tuple
    ) -> np.ndarray:
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
            return frame

        return frame[y1:y2, x1:x2]

    def is_minimap_visible(self, results: list[DetectionResult]) -> bool:
        if not results:
            return False
        return any(r.is_present for r in results)
