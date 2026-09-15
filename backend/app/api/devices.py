"""Device API Routes"""
from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.state import iot_simulator, alert_engine

router = APIRouter()

@router.get("/devices", response_model=List[dict])
async def list_devices():
    """List all monitored devices."""
    return iot_simulator.get_device_info()

@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get detailed status for a specific device."""
    status = iot_simulator.get_device_status(device_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return status

@router.get("/devices/{device_id}/readings")
async def get_device_readings(device_id: str, limit: int = 50):
    """Get recent sensor readings for a device."""
    if device_id not in iot_simulator.devices:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    readings = []
    for _ in range(min(limit, 20)):
        reading = iot_simulator.generate_reading(device_id)
        readings.append(reading.to_dict())
    return readings

@router.get("/devices/{device_id}/alerts")
async def get_device_alerts(device_id: str, limit: int = 50):
    """Get recent alerts for a device."""
    return alert_engine.get_recent_alerts(limit=limit, device_id=device_id)
