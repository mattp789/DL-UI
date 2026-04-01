"""Build script for creating the standalone exe."""
import PyInstaller.__main__
from pathlib import Path

root = Path(__file__).parent

PyInstaller.__main__.run([
    str(root / "src" / "main.py"),
    "--name=deadlock-companion",
    "--onefile",
    "--noconsole",
    f"--add-data={root / 'static'};static",
    f"--add-data={root / 'templates'};templates",
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.protocols.websockets",
    "--hidden-import=uvicorn.protocols.websockets.auto",
    "--hidden-import=uvicorn.lifespan",
    "--hidden-import=uvicorn.lifespan.on",
])
