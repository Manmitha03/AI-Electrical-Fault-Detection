"""Diagnostics API Routes"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from backend.app.schemas.schemas import DiagnoseInput
from backend.app.state import ml_predictor, diagnostic_engine, image_processor, iot_simulator

router = APIRouter()

@router.post("/diagnose")
async def diagnose_sensor(data: DiagnoseInput):
    """Diagnose electrical fault from sensor readings."""
    sensor_data = {
        "voltage": data.voltage, "current": data.current,
        "temperature": data.temperature, "power": data.power,
        "power_factor": data.power_factor, "frequency": data.frequency,
        "resistance": data.resistance, "vibration": data.vibration,
    }
    ml_result = ml_predictor.predict(sensor_data)
    result = diagnostic_engine.diagnose(
        sensor_prediction=ml_result, symptoms=data.symptoms, sensor_data=sensor_data,
    )
    return result.to_dict()

@router.post("/diagnose/image")
async def diagnose_image(
    file: UploadFile = File(...),
    device_id: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
):
    """Diagnose electrical fault from an uploaded image."""
    file_data = await file.read()
    filename = file.filename or "upload.jpg"
    image_result = image_processor.analyze(file_data, filename)
    if not image_result.valid:
        raise HTTPException(status_code=400, detail=image_result.error)

    sensor_prediction = None
    sensor_data = None
    if device_id and device_id in iot_simulator.devices:
        reading = iot_simulator.generate_reading(device_id)
        sensor_data = {
            "voltage": reading.voltage, "current": reading.current,
            "temperature": reading.temperature, "power": reading.power,
            "power_factor": reading.power_factor, "frequency": reading.frequency,
            "resistance": reading.resistance, "vibration": reading.vibration,
        }
        sensor_prediction = ml_predictor.predict(sensor_data)

    result = diagnostic_engine.diagnose(
        sensor_prediction=sensor_prediction,
        image_analysis=image_result.to_dict(),
        symptoms=symptoms, sensor_data=sensor_data,
    )
    response = result.to_dict()
    response["image_analysis_details"] = image_result.to_dict()
    return response

@router.get("/faults")
async def list_fault_types():
    """List all supported fault types."""
    from backend.app.services.troubleshooting import TroubleshootingService
    return TroubleshootingService().get_all_entries()

@router.get("/faults/{fault_type}")
async def get_fault_info(fault_type: str):
    """Get detailed info about a fault type."""
    from backend.app.services.troubleshooting import TroubleshootingService
    entry = TroubleshootingService().get_troubleshooting(fault_type)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Fault type '{fault_type}' not found")
    return entry.to_dict()
