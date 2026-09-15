"""Alerts API Routes"""
from fastapi import APIRouter
from backend.app.state import alert_engine

router = APIRouter()

@router.get("/alerts")
async def get_alerts(limit: int = 50, device_id: str = None):
    """Get recent alerts."""
    return alert_engine.get_recent_alerts(limit=limit, device_id=device_id)

@router.get("/alerts/count")
async def get_alert_count():
    """Get alert counts."""
    return {
        "unacknowledged": alert_engine.get_unacknowledged_count(),
        "total": len(alert_engine._recent_alerts),
    }
