"""Demo Mode API Routes"""
from fastapi import APIRouter, HTTPException
from backend.app.schemas.schemas import DemoScenarioInput
from backend.app.state import iot_simulator, alert_engine
from iot.simulator import FAULT_PROFILES

router = APIRouter()

@router.get("/demo/scenarios")
async def list_scenarios():
    """List all available demo scenarios."""
    return iot_simulator.get_scenarios()

@router.post("/demo/scenario")
async def activate_scenario(data: DemoScenarioInput):
    """Activate a demo scenario."""
    result = iot_simulator.set_scenario(data.scenario)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/demo/reset")
async def reset_demo():
    """Reset all devices to normal."""
    iot_simulator.clear_all_faults()
    alert_engine.clear_alerts()
    return {"status": "reset", "message": "All devices returned to normal operation."}

@router.post("/demo/inject-fault")
async def inject_fault(device_id: str, fault_type: str):
    """Inject a specific fault into a device."""
    if device_id not in iot_simulator.devices:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    if fault_type not in FAULT_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown fault. Available: {list(FAULT_PROFILES.keys())}")
    iot_simulator.set_fault(device_id, fault_type)
    return {"status": "injected", "device_id": device_id, "fault_type": fault_type}
