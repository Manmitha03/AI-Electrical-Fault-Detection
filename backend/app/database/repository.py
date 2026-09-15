"""
Database Repository — CRUD Operations
========================================
Separates data access from business logic.
All database queries are centralized here.
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend.app.database.models import (
    Device, SensorReading, FaultEvent, Alert, DiagnosticReport
)


# ─── Device Operations ────────────────────────────────────────

def get_all_devices(db: Session) -> List[Device]:
    return db.query(Device).all()


def get_device(db: Session, device_id: str) -> Optional[Device]:
    return db.query(Device).filter(Device.device_id == device_id).first()


def create_device(db: Session, device_id: str, name: str,
                  device_type: str, location: str = "") -> Device:
    device = Device(
        device_id=device_id, name=name,
        device_type=device_type, location=location,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device_status(db: Session, device_id: str, status: str):
    device = get_device(db, device_id)
    if device:
        device.status = status
        device.last_seen = datetime.utcnow()
        db.commit()


def ensure_device_exists(db: Session, device_id: str, name: str = None,
                         device_type: str = "unknown") -> Device:
    """Get or create a device."""
    device = get_device(db, device_id)
    if not device:
        device = create_device(
            db, device_id, name or device_id,
            device_type=device_type,
        )
    return device


# ─── Sensor Reading Operations ────────────────────────────────

def add_sensor_reading(db: Session, device_id: str,
                       voltage: float, current: float, temperature: float,
                       power: float = 0, power_factor: float = 0.95,
                       frequency: float = 50.0, resistance: float = 0,
                       vibration: float = 0) -> SensorReading:
    reading = SensorReading(
        device_id=device_id,
        voltage=voltage, current=current, temperature=temperature,
        power=power, power_factor=power_factor, frequency=frequency,
        resistance=resistance, vibration=vibration,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Update device last_seen
    update_device_status(db, device_id, "online")

    return reading


def get_device_readings(db: Session, device_id: str,
                        limit: int = 100,
                        hours: int = None) -> List[SensorReading]:
    query = db.query(SensorReading).filter(
        SensorReading.device_id == device_id
    )
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(SensorReading.timestamp >= since)

    return query.order_by(desc(SensorReading.timestamp)).limit(limit).all()


def get_latest_reading(db: Session, device_id: str) -> Optional[SensorReading]:
    return db.query(SensorReading).filter(
        SensorReading.device_id == device_id
    ).order_by(desc(SensorReading.timestamp)).first()


# ─── Fault Event Operations ──────────────────────────────────

def add_fault_event(db: Session, device_id: str, fault_type: str,
                    confidence: float, severity: str, risk_score: int,
                    evidence: list) -> FaultEvent:
    event = FaultEvent(
        device_id=device_id,
        fault_type=fault_type,
        confidence=confidence,
        severity=severity,
        risk_score=risk_score,
        evidence=json.dumps(evidence),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_device_faults(db: Session, device_id: str,
                      limit: int = 50) -> List[FaultEvent]:
    return db.query(FaultEvent).filter(
        FaultEvent.device_id == device_id
    ).order_by(desc(FaultEvent.timestamp)).limit(limit).all()


def get_recent_faults(db: Session, limit: int = 50) -> List[FaultEvent]:
    return db.query(FaultEvent).order_by(
        desc(FaultEvent.timestamp)
    ).limit(limit).all()


def get_fault_distribution(db: Session, hours: int = 24) -> Dict[str, int]:
    since = datetime.utcnow() - timedelta(hours=hours)
    results = db.query(
        FaultEvent.fault_type, func.count(FaultEvent.id)
    ).filter(
        FaultEvent.timestamp >= since
    ).group_by(FaultEvent.fault_type).all()

    return {fault_type: count for fault_type, count in results}


# ─── Alert Operations ────────────────────────────────────────

def add_alert(db: Session, device_id: str, alert_type: str,
              severity: str, title: str, message: str,
              value: float = None, threshold: float = None) -> Alert:
    alert = Alert(
        device_id=device_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        value=value,
        threshold=threshold,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_device_alerts(db: Session, device_id: str,
                      limit: int = 50) -> List[Alert]:
    return db.query(Alert).filter(
        Alert.device_id == device_id
    ).order_by(desc(Alert.timestamp)).limit(limit).all()


def get_recent_alerts(db: Session, limit: int = 100) -> List[Alert]:
    return db.query(Alert).order_by(
        desc(Alert.timestamp)
    ).limit(limit).all()


def get_unacknowledged_alerts(db: Session) -> List[Alert]:
    return db.query(Alert).filter(
        Alert.acknowledged == False
    ).order_by(desc(Alert.timestamp)).all()


def acknowledge_alert(db: Session, alert_id: int) -> bool:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        return True
    return False


# ─── Diagnostic Report Operations ────────────────────────────

def add_diagnostic_report(db: Session, device_id: str,
                          report_type: str, fault_type: str,
                          confidence: float, severity: str,
                          risk_score: int, sensor_data: dict,
                          image_analysis: dict, evidence: list,
                          possible_causes: list, recommended_actions: list,
                          troubleshooting_steps: list) -> DiagnosticReport:
    report = DiagnosticReport(
        device_id=device_id,
        report_type=report_type,
        fault_type=fault_type,
        confidence=confidence,
        severity=severity,
        risk_score=risk_score,
        sensor_data=json.dumps(sensor_data),
        image_analysis=json.dumps(image_analysis),
        evidence=json.dumps(evidence),
        possible_causes=json.dumps(possible_causes),
        recommended_actions=json.dumps(recommended_actions),
        troubleshooting_steps=json.dumps(troubleshooting_steps),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report(db: Session, report_id: int) -> Optional[DiagnosticReport]:
    return db.query(DiagnosticReport).filter(
        DiagnosticReport.id == report_id
    ).first()


def get_device_reports(db: Session, device_id: str,
                       limit: int = 20) -> List[DiagnosticReport]:
    return db.query(DiagnosticReport).filter(
        DiagnosticReport.device_id == device_id
    ).order_by(desc(DiagnosticReport.timestamp)).limit(limit).all()


# ─── Statistics ───────────────────────────────────────────────

def get_statistics(db: Session) -> dict:
    """Get overall system statistics."""
    total_devices = db.query(func.count(Device.id)).scalar() or 0
    total_readings = db.query(func.count(SensorReading.id)).scalar() or 0
    total_faults = db.query(func.count(FaultEvent.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    unack_alerts = db.query(func.count(Alert.id)).filter(
        Alert.acknowledged == False
    ).scalar() or 0

    # Severity distribution
    severity_dist = db.query(
        FaultEvent.severity, func.count(FaultEvent.id)
    ).group_by(FaultEvent.severity).all()

    # Fault distribution (last 24h)
    fault_dist = get_fault_distribution(db, hours=24)

    # Devices with active faults
    critical_devices = db.query(Device).filter(
        Device.status.in_(["warning", "critical"])
    ).count()

    return {
        "total_devices": total_devices,
        "total_readings": total_readings,
        "total_faults": total_faults,
        "total_alerts": total_alerts,
        "unacknowledged_alerts": unack_alerts,
        "critical_devices": critical_devices,
        "severity_distribution": {s: c for s, c in severity_dist},
        "fault_distribution_24h": fault_dist,
    }
