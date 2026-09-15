"""
Pydantic Schemas for API Request/Response Validation
======================================================
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ─── Sensor Schemas ────────────────────────────────────────────

class SensorReadingInput(BaseModel):
    """Input schema for sensor readings."""
    device_id: str = Field(..., description="Device identifier", example="PANEL-001")
    voltage: float = Field(..., ge=0, le=500, example=231.4)
    current: float = Field(..., ge=0, le=200, example=8.7)
    temperature: float = Field(..., ge=-20, le=300, example=46.2)
    power: float = Field(default=0, ge=0, example=2017.18)
    power_factor: float = Field(default=0.95, ge=0, le=1.0, example=0.94)
    frequency: float = Field(default=50.0, ge=40, le=60, example=49.9)
    resistance: float = Field(default=25, ge=0, le=10000, example=22.5)
    vibration: float = Field(default=0.05, ge=0, le=10, example=0.12)


# ─── Diagnostic Schemas ───────────────────────────────────────

class DiagnoseInput(BaseModel):
    """Input schema for sensor-based diagnosis."""
    voltage: float = Field(..., example=185)
    current: float = Field(..., example=17.5)
    temperature: float = Field(..., example=81)
    power: float = Field(default=0, example=3330)
    power_factor: float = Field(default=0.95, example=0.72)
    frequency: float = Field(default=50.0, example=50)
    resistance: float = Field(default=25, example=25)
    vibration: float = Field(default=0.05, example=0.45)
    symptoms: Optional[str] = Field(default=None, example="Motor is getting hot and making unusual noise")
    device_id: Optional[str] = Field(default=None, example="MOTOR-002")


class DiagnoseResponse(BaseModel):
    """Response schema for diagnosis."""
    fault_type: str
    confidence: float
    severity: str
    risk_score: int
    evidence: List[str]
    possible_causes: List[str]
    recommended_actions: List[str]
    safety_warnings: List[str]
    troubleshooting_steps: List[str]
    contributing_factors: List[str]
    sensor_diagnosis: Optional[dict] = None
    image_diagnosis: Optional[dict] = None
    symptom_analysis: Optional[dict] = None
    severity_breakdown: Optional[dict] = None
    disclaimer: str


# ─── Chat Schemas ──────────────────────────────────────────────

class ChatInput(BaseModel):
    """Input schema for chatbot."""
    message: str = Field(..., min_length=1, max_length=2000, example="My motor is getting unusually hot.")
    device_id: Optional[str] = Field(default=None, example="MOTOR-002")


class ChatResponse(BaseModel):
    """Response schema for chatbot."""
    role: str
    content: str
    timestamp: str
    metadata: dict


# ─── Device Schemas ────────────────────────────────────────────

class DeviceResponse(BaseModel):
    """Response schema for a device."""
    device_id: str
    name: str
    device_type: str
    location: str
    status: str
    fault_profile: str = "normal"
    latest_reading: Optional[dict] = None


# ─── Alert Schemas ─────────────────────────────────────────────

class AlertResponse(BaseModel):
    """Response schema for an alert."""
    device_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: str
    acknowledged: bool


# ─── Demo Schemas ──────────────────────────────────────────────

class DemoScenarioInput(BaseModel):
    """Input schema for triggering a demo scenario."""
    scenario: str = Field(..., example="overheating",
                          description="Scenario name: normal, overheating, overcurrent, overvoltage, "
                                      "loose_connection, short_circuit, critical_failure, multi_fault")


class DemoScenarioResponse(BaseModel):
    """Response schema for demo scenario activation."""
    name: str
    description: str
    active_faults: dict


# ─── Report Schemas ────────────────────────────────────────────

class ReportGenerateInput(BaseModel):
    """Input schema for generating a diagnostic report."""
    device_id: str = Field(..., example="MOTOR-002")
    include_history: bool = Field(default=True)


class ReportResponse(BaseModel):
    """Response schema for a diagnostic report."""
    report_id: int
    device_id: str
    timestamp: str
    fault_type: str
    confidence: float
    severity: str
    risk_score: int
    sensor_data: dict
    evidence: List[str]
    possible_causes: List[str]
    recommended_actions: List[str]
    troubleshooting_steps: List[str]


# ─── Statistics Schema ─────────────────────────────────────────

class StatisticsResponse(BaseModel):
    """Response schema for system statistics."""
    total_devices: int
    total_readings: int
    total_faults: int
    total_alerts: int
    unacknowledged_alerts: int
    critical_devices: int
    severity_distribution: dict
    fault_distribution_24h: dict
