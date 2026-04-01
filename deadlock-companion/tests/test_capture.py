import numpy as np
from unittest.mock import patch, MagicMock
from src.capture import CaptureEngine


def test_capture_returns_numpy_array():
    region = {"x": 0, "y": 0, "width": 100, "height": 100}
    engine = CaptureEngine(region)

    fake_pixels = np.zeros((100, 100, 4), dtype=np.uint8)
    mock_sct = MagicMock()
    mock_grab = fake_pixels  # np.array() of an ndarray returns the array itself
    mock_sct.grab.return_value = mock_grab
    mock_sct.__enter__ = lambda s: mock_sct
    mock_sct.__exit__ = MagicMock(return_value=False)

    with patch("mss.mss", return_value=mock_sct):
        frame = engine.capture_frame()

    assert isinstance(frame, np.ndarray)
    assert frame.shape[0] == 100
    assert frame.shape[1] == 100


def test_capture_region_to_monitor():
    region = {"x": 150, "y": 250, "width": 300, "height": 300}
    engine = CaptureEngine(region)
    monitor = engine._region_to_monitor()
    assert monitor == {"left": 150, "top": 250, "width": 300, "height": 300}


def test_update_region():
    region = {"x": 0, "y": 0, "width": 100, "height": 100}
    engine = CaptureEngine(region)
    new_region = {"x": 50, "y": 50, "width": 200, "height": 200}
    engine.update_region(new_region)
    assert engine.region == new_region
