"""FastAPI server with WebSocket support for real-time timer updates."""
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.timers import TimerManager
from src.config import Config
from src.resources import get_resource_path


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)


def create_app(
    timer_manager: TimerManager,
    static_dir: str | None = None,
    config: Optional[Config] = None,
) -> FastAPI:
    app = FastAPI(title="Deadlock Companion")
    ws_manager = ConnectionManager()
    app.state.ws_manager = ws_manager
    app.state.timer_manager = timer_manager

    if static_dir is None:
        static_dir = str(get_resource_path("static"))

    @app.get("/api/health")
    def health():
        return {"status": "healthy"}

    @app.get("/api/state")
    def get_state():
        return {
            "match_state": timer_manager.match_state.value,
            "objectives": timer_manager.get_all_states(),
        }

    @app.post("/api/toggle/{objective_id}")
    def toggle_objective(objective_id: str):
        timer_manager.toggle_manual(objective_id)
        return {"ok": True}

    @app.get("/api/needs-calibration")
    def needs_calibration():
        needs = config.needs_calibration if config else True
        return {"needs_calibration": needs}

    @app.get("/api/needs-position-calibration")
    def needs_position_calibration():
        needs = config.needs_position_calibration if config else True
        return {"needs_calibration": needs}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "toggle":
                    timer_manager.toggle_manual(msg["id"])
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    static_path = Path(static_dir)
    if static_path.exists():
        @app.get("/")
        def index():
            return FileResponse(static_path / "index.html")

        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
