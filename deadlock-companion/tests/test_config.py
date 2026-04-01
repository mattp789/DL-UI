import json
import os
from pathlib import Path
from src.config import Config


def test_default_config(tmp_path):
    config = Config(config_dir=tmp_path)
    assert config.capture_region is None
    assert config.audio_alerts is True


def test_save_and_load_config(tmp_path):
    config = Config(config_dir=tmp_path)
    config.capture_region = {"x": 100, "y": 200, "width": 300, "height": 300}
    config.audio_alerts = False
    config.save()

    loaded = Config(config_dir=tmp_path)
    loaded.load()
    assert loaded.capture_region == {"x": 100, "y": 200, "width": 300, "height": 300}
    assert loaded.audio_alerts is False


def test_config_creates_directory(tmp_path):
    config_dir = tmp_path / "subdir" / "deadlock-companion"
    config = Config(config_dir=config_dir)
    config.save()
    assert config_dir.exists()
    assert (config_dir / "config.json").exists()


def test_load_missing_file_uses_defaults(tmp_path):
    config = Config(config_dir=tmp_path)
    config.load()  # Should not raise
    assert config.capture_region is None
    assert config.audio_alerts is True


def test_needs_calibration(tmp_path):
    config = Config(config_dir=tmp_path)
    assert config.needs_calibration is True
    config.capture_region = {"x": 0, "y": 0, "width": 100, "height": 100}
    assert config.needs_calibration is False
