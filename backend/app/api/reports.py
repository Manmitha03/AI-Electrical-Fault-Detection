"""Reports API Routes"""
from fastapi import APIRouter, HTTPException
from backend.app.schemas.schemas import ReportGenerateInput
from backend.app.state import ml_predictor, diagnostic_engine, iot_simulator
from datetime import datetime

router = APIRouter()
_reports = {}
_report_counter = 0

@router.post("/reports/generate")
async def generate_report(data: ReportGenerateInput):
    """Generate a comprehensive diagnostic report."""
    global _report_counter
    device_status = iot_simulator.get_device_status(data.device_id)
    if not device_status:
        raise HTTPException(status_code=404, detail=f"Device {data.device_id} not found")
    reading = device_status["latest_reading"]
    sensor_data = {k: reading[k] for k in ["voltage","current","temperature","power","power_factor","frequency","resistance","vibration"]}
    ml_result = ml_predictor.predict(sensor_data)
    diagnosis = diagnostic_engine.diagnose(sensor_prediction=ml_result, sensor_data=sensor_data)
    _report_counter += 1
    report = {
        "report_id": _report_counter,
        "device_id": data.device_id,
        "device_name": device_status.get("name", data.device_id),
        "device_type": device_status.get("device_type", "unknown"),
        "location": device_status.get("location", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "fault_type": diagnosis.fault_type,
        "confidence": round(diagnosis.confidence, 4),
        "severity": diagnosis.severity,
        "risk_score": diagnosis.risk_score,
        "sensor_data": sensor_data,
        "evidence": diagnosis.evidence,
        "contributing_factors": diagnosis.contributing_factors,
        "possible_causes": diagnosis.possible_causes,
        "recommended_actions": diagnosis.recommended_actions,
        "safety_warnings": diagnosis.safety_warnings,
        "troubleshooting_steps": diagnosis.troubleshooting_steps,
        "severity_breakdown": diagnosis.severity_breakdown,
        "ml_model_info": ml_predictor.get_model_info(),
        "disclaimer": diagnosis.disclaimer,
    }
    _reports[_report_counter] = report
    return report

@router.get("/reports/{report_id}")
async def get_report(report_id: int):
    """Retrieve a diagnostic report."""
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return report

@router.get("/reports")
async def list_reports():
    """List all reports."""
    return list(_reports.values())
