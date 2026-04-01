"""Resource path resolution for both normal and PyInstaller frozen builds."""
import sys
from pathlib import Path


def get_resource_path(relative: str) -> Path:
    """Return absolute path to a bundled resource.

    When running as a PyInstaller onefile exe, data files are extracted to
    sys._MEIPASS at runtime. When running normally, they live two levels up
    from this file (i.e. the deadlock-companion/ package root).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / relative
