"""
Database Models for Electrical Fault Detection System
======================================================
SQLAlchemy ORM models for devices, sensor readings, fault events,
alerts, and diagnostic reports.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, Index, Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from backend.app.database.database import Base


class Device(Base):
    """Monitored electrical device/equipment."""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)  # panel, motor, transformer, machine
    location = Column(String(200), default="")
    status = Column(String(20), default="online")  # online, offline, warning, critical
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
    fault_events = relationship("FaultEvent", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    reports = relationship("DiagnosticReport", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device {self.device_id}: {self.name}>"


class SensorReading(Base):
    """Individual sensor reading from a device."""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    power = Column(Float, default=0.0)
    power_factor = Column(Float, default=0.95)
    frequency = Column(Float, default=50.0)
    resistance = Column(Float, default=0.0)
    vibration = Column(Float, default=0.0)

    # Relationship
    device = relationship("Device", back_populates="readings")

    __table_args__ = (
        Index("ix_sensor_device_time", "device_id", "timestamp"),
    )

    def __repr__(self):
        return f"<SensorReading {self.device_id} @ {self.timestamp}>"


class FaultEvent(Base):
    """Detected fault event."""
    __tablename__ = "fault_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    fault_type = Column(String(50), nullable=False)
    confidence = Column(Float, default=0.0)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Integer, default=0)
    evidence = Column(Text, default="[]")  # JSON array
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationship
    device = relationship("Device", back_populates="fault_events")

    __table_args__ = (
        Index("ix_fault_device_time", "device_id", "timestamp"),
    )

    def __repr__(self):
        return f"<FaultEvent {self.fault_type} on {self.device_id}>"


class Alert(Base):
    """System alert generated from abnormal readings or faults."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)

    # Relationship
    device = relationship("Device", back_populates="alerts")

    __table_args__ = (
        Index("ix_alert_device_time", "device_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Alert {self.alert_type} on {self.device_id}>"


class DiagnosticReport(Base):
    """Generated diagnostic report."""
    __tablename__ = "diagnostic_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    report_type = Column(String(50), default="sensor")  # sensor, image, combined
    fault_type = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0)
    severity = Column(String(20), nullable=True)
    risk_score = Column(Integer, default=0)
    sensor_data = Column(Text, default="{}")  # JSON
    image_analysis = Column(Text, default="{}")  # JSON
    evidence = Column(Text, default="[]")  # JSON
    possible_causes = Column(Text, default="[]")  # JSON
    recommended_actions = Column(Text, default="[]")  # JSON
    troubleshooting_steps = Column(Text, default="[]")  # JSON

    # Relationship
    device = relationship("Device", back_populates="reports")

    def __repr__(self):
        return f"<DiagnosticReport {self.id}: {self.fault_type}>"
