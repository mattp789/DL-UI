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
        self.objective_positions: Optional[dict] = None
        self.load()

    def load(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                data = json.load(f)
            self.capture_region = data.get("capture_region")
            self.audio_alerts = data.get("audio_alerts", True)
            raw_positions = data.get("objective_positions")
            if raw_positions is not None:
                # Convert stored [[x, y], ...] lists back to (x, y) tuples.
                self.objective_positions = {
                    type_key: [tuple(pos) for pos in positions]
                    for type_key, positions in raw_positions.items()
                }
            else:
                self.objective_positions = None

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # Serialise tuple positions as [[x, y], ...] lists for JSON.
        if self.objective_positions is not None:
            serialised_positions = {
                type_key: [list(pos) for pos in positions]
                for type_key, positions in self.objective_positions.items()
            }
        else:
            serialised_positions = None
        data = {
            "capture_region": self.capture_region,
            "audio_alerts": self.audio_alerts,
            "objective_positions": serialised_positions,
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def needs_calibration(self) -> bool:
        """True when the minimap capture region has not yet been set."""
        return self.capture_region is None

    @property
    def needs_position_calibration(self) -> bool:
        """True when objective positions have not yet been calibrated."""
        return self.objective_positions is None
