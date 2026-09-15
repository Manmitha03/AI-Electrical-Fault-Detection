"""
FastAPI Main Application
==========================
Entry point for the AI Electric Fault Detection backend.
"""

import os
import sys
import json
import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.app.api import devices, diagnostics, sensors, alerts, chatbot, demo, reports
from backend.app.state import (
    ml_predictor, iot_simulator, alert_engine, sensor_processor
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

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
        for conn in disconnected:
            self.disconnect(conn)


ws_manager = ConnectionManager()


async def iot_background_task():
    """Background task that runs the IoT simulator and broadcasts readings."""
    print("  [IoT] Background simulator started")
    try:
        async for readings in iot_simulator.stream(interval=2.0):
            all_readings = []
            all_alerts = []

            for reading in readings:
                reading_dict = reading.to_dict()
                enriched = sensor_processor.process_reading(reading_dict)
                new_alerts = alert_engine.check_reading(reading.device_id, reading_dict)
                for alert in new_alerts:
                    all_alerts.append(alert.to_dict())
                all_readings.append(enriched)

            await ws_manager.broadcast({
                "type": "sensor_update",
                "readings": all_readings,
                "alerts": [a for a in all_alerts],
                "device_count": len(readings),
            })
    except asyncio.CancelledError:
        print("  [IoT] Background simulator stopped")
    except Exception as e:
        print(f"  [IoT] Simulator error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 60)
    print("  AI Electric Fault Detection System")
    print("  Starting up...")
    print("=" * 60)

    try:
        from backend.app.database.database import init_db
        init_db()
    except Exception as e:
        print(f"  [DB] Init warning: {e}")

    try:
        if ml_predictor.is_available:
            print("  [ML] Model ready for predictions")
        else:
            print("  [ML] Model not available — run: python ml/train_model.py")
    except Exception as e:
        print(f"  [ML] Model load warning: {e}")

    iot_task = asyncio.create_task(iot_background_task())

    print("  [OK] System ready")
    print("=" * 60 + "\n")

    yield

    print("\n  Shutting down...")
    iot_simulator.stop()
    iot_task.cancel()
    try:
        await iot_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI Electric Fault Detection & Diagnostic System",
    description=(
        "AI-powered electrical fault detection using ML, computer vision, "
        "and IoT sensor monitoring.\n\n"
        "⚠ DISCLAIMER: This is an AI diagnostic assistant, NOT a certified "
        "electrical safety system."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router, prefix="/api", tags=["Devices"])
app.include_router(diagnostics.router, prefix="/api", tags=["Diagnostics"])
app.include_router(sensors.router, prefix="/api", tags=["Sensors"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
app.include_router(demo.router, prefix="/api", tags=["Demo"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])


@app.websocket("/ws/sensors")
async def websocket_sensors(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                if cmd.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "AI Electric Fault Detection & Diagnostic System",
        "version": "1.0.0",
        "status": "running",
        "ml_model_loaded": ml_predictor.is_available,
        "endpoints": {
            "docs": "/docs",
            "devices": "/api/devices",
            "diagnose": "/api/diagnose",
            "chat": "/api/chat",
            "websocket": "/ws/sensors",
        },
    }


@app.get("/health", tags=["Root"])
async def health():
    return {
        "status": "healthy",
        "ml_available": ml_predictor.is_available,
        "iot_running": iot_simulator._running,
        "ws_connections": len(ws_manager.active_connections),
    }
