import numpy as np
import mss


class CaptureEngine:
    def __init__(self, region: dict):
        self.region = region

    def _region_to_monitor(self) -> dict:
        return {
            "left": self.region["x"],
            "top": self.region["y"],
            "width": self.region["width"],
            "height": self.region["height"],
        }

    def capture_frame(self) -> np.ndarray:
        monitor = self._region_to_monitor()
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
        return frame[:, :, :3]

    def update_region(self, region: dict):
        self.region = region
