"""Sensor API Routes"""
from fastapi import APIRouter
from backend.app.schemas.schemas import SensorReadingInput
from backend.app.state import ml_predictor, alert_engine, sensor_processor, iot_simulator

router = APIRouter()

@router.post("/sensor/readings")
async def ingest_sensor_reading(reading: SensorReadingInput):
    """Ingest a sensor reading from an IoT device."""
    reading_dict = reading.dict()
    enriched = sensor_processor.process_reading(reading_dict)
    new_alerts = alert_engine.check_reading(reading.device_id, reading_dict)
    sensor_data = {
        "voltage": reading.voltage, "current": reading.current,
        "temperature": reading.temperature, "power": reading.power,
        "power_factor": reading.power_factor, "frequency": reading.frequency,
        "resistance": reading.resistance, "vibration": reading.vibration,
    }
    prediction = ml_predictor.predict(sensor_data)
    return {
        "status": "received", "device_id": reading.device_id,
        "enriched_reading": enriched, "alerts_generated": len(new_alerts),
        "prediction": prediction,
    }

@router.get("/statistics")
async def get_statistics():
    """Get system-wide statistics."""
    devices = iot_simulator.get_device_info()
    total = len(devices)
    critical = sum(1 for d in devices if d["status"] == "critical")
    warning = sum(1 for d in devices if d["status"] == "warning")
    device_summaries = {}
    for device in devices:
        did = device["device_id"]
        summary = sensor_processor.get_device_summary(did)
        if summary:
            device_summaries[did] = summary
    return {
        "total_devices": total, "critical_devices": critical,
        "warning_devices": warning, "online_devices": total - critical,
        "total_alerts": len(alert_engine._recent_alerts),
        "unacknowledged_alerts": alert_engine.get_unacknowledged_count(),
        "device_summaries": device_summaries,
        "active_faults": dict(iot_simulator._fault_states),
    }
