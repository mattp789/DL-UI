import json
from pathlib import Path
from typing import Optional


class Config:
    DEFAULT_DIR = Path.home() / ".deadlock-companion"

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self.DEFAULT_DIR
        self.config_file = self.config_dir / "config.json"
        self.capture_region: Optional[dict] = None
        self.audio_alerts: bool = True
        self.load()

    def load(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                data = json.load(f)
            self.capture_region = data.get("capture_region")
            self.audio_alerts = data.get("audio_alerts", True)

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "capture_region": self.capture_region,
            "audio_alerts": self.audio_alerts,
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def needs_calibration(self) -> bool:
        return self.capture_region is None
