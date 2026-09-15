"""
Alert Engine
==============
Generates alerts when sensor readings become abnormal.
Supports threshold-based detection with deduplication.
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


# Alert thresholds
THRESHOLDS = {
    "temperature": {
        "warning": 60,
        "high": 80,
        "critical": 100,
        "unit": "°C",
        "alert_type": "overtemperature",
    },
    "current": {
        "warning": 18,
        "high": 25,
        "critical": 40,
        "unit": "A",
        "alert_type": "overcurrent",
    },
    "voltage_high": {
        "warning": 250,
        "high": 270,
        "critical": 300,
        "unit": "V",
        "alert_type": "overvoltage",
    },
    "voltage_low": {
        "warning": 210,
        "high": 190,
        "critical": 160,
        "unit": "V",
        "alert_type": "undervoltage",
    },
    "vibration": {
        "warning": 0.25,
        "high": 0.40,
        "critical": 0.60,
        "unit": "g",
        "alert_type": "vibration_anomaly",
    },
    "power_factor_low": {
        "warning": 0.80,
        "high": 0.65,
        "critical": 0.45,
        "unit": "",
        "alert_type": "power_factor",
    },
}

# Minimum interval between same-type alerts for same device (seconds)
DEDUP_INTERVAL = 30


class AlertEntry:
    """A single alert."""

    def __init__(self, device_id: str, alert_type: str, severity: str,
                 title: str, message: str, value: float = None,
                 threshold: float = None):
        self.device_id = device_id
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.message = message
        self.value = value
        self.threshold = threshold
        self.timestamp = datetime.utcnow()
        self.acknowledged = False

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
        }


class AlertEngine:
    """
    Threshold-based alert engine with deduplication.

    Checks sensor readings against defined thresholds and generates
    alerts when values exceed warning, high, or critical levels.
    """

    def __init__(self):
        self._recent_alerts: List[AlertEntry] = []
        self._last_alert_time: Dict[str, float] = defaultdict(float)
        self._max_stored = 500

    def check_reading(self, device_id: str, reading: Dict[str, float]) -> List[AlertEntry]:
        """
        Check a sensor reading against all thresholds.

        Returns list of generated alerts.
        """
        alerts = []

        # Temperature check
        temp = reading.get("temperature", 0)
        t = THRESHOLDS["temperature"]
        if temp >= t["critical"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "CRITICAL",
                f"🚨 CRITICAL TEMPERATURE: {temp:.1f}{t['unit']}",
                f"Device {device_id} temperature has reached {temp:.1f}{t['unit']}, "
                f"exceeding critical threshold of {t['critical']}{t['unit']}. "
                f"Immediate action required — isolate power if safe to do so.",
                temp, t["critical"]
            )
            if alert:
                alerts.append(alert)
        elif temp >= t["high"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "HIGH",
                f"⚠ HIGH TEMPERATURE: {temp:.1f}{t['unit']}",
                f"Device {device_id} temperature is {temp:.1f}{t['unit']}, "
                f"above high threshold of {t['high']}{t['unit']}. "
                f"Inspect equipment and monitor closely.",
                temp, t["high"]
            )
            if alert:
                alerts.append(alert)
        elif temp >= t["warning"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "MEDIUM",
                f"⚠ ELEVATED TEMPERATURE: {temp:.1f}{t['unit']}",
                f"Device {device_id} temperature is {temp:.1f}{t['unit']}, "
                f"above warning threshold of {t['warning']}{t['unit']}.",
                temp, t["warning"]
            )
            if alert:
                alerts.append(alert)

        # Current check
        current = reading.get("current", 0)
        t = THRESHOLDS["current"]
        if current >= t["critical"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "CRITICAL",
                f"🚨 CRITICAL OVERCURRENT: {current:.1f}{t['unit']}",
                f"Device {device_id} current draw is {current:.1f}{t['unit']}, "
                f"exceeding critical threshold. Possible short circuit or severe overload.",
                current, t["critical"]
            )
            if alert:
                alerts.append(alert)
        elif current >= t["high"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "HIGH",
                f"⚠ HIGH CURRENT: {current:.1f}{t['unit']}",
                f"Device {device_id} current is {current:.1f}{t['unit']}. "
                f"Check for overload conditions.",
                current, t["high"]
            )
            if alert:
                alerts.append(alert)
        elif current >= t["warning"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "MEDIUM",
                f"⚠ ELEVATED CURRENT: {current:.1f}{t['unit']}",
                f"Device {device_id} current is {current:.1f}{t['unit']}.",
                current, t["warning"]
            )
            if alert:
                alerts.append(alert)

        # Voltage checks (high and low)
        voltage = reading.get("voltage", 230)
        t = THRESHOLDS["voltage_high"]
        if voltage >= t["critical"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "CRITICAL",
                f"🚨 CRITICAL OVERVOLTAGE: {voltage:.1f}V",
                f"Device {device_id} voltage is {voltage:.1f}V. "
                f"Disconnect sensitive equipment immediately.",
                voltage, t["critical"]
            )
            if alert:
                alerts.append(alert)
        elif voltage >= t["high"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "HIGH",
                f"⚠ OVERVOLTAGE: {voltage:.1f}V",
                f"Device {device_id} voltage is above normal at {voltage:.1f}V.",
                voltage, t["high"]
            )
            if alert:
                alerts.append(alert)

        t = THRESHOLDS["voltage_low"]
        if voltage <= t["critical"]:
            alert = self._create_alert(
                device_id, "undervoltage", "CRITICAL",
                f"🚨 CRITICAL UNDERVOLTAGE: {voltage:.1f}V",
                f"Device {device_id} voltage has dropped to {voltage:.1f}V. "
                f"Equipment may malfunction or overheat.",
                voltage, t["critical"]
            )
            if alert:
                alerts.append(alert)
        elif voltage <= t["high"]:
            alert = self._create_alert(
                device_id, "undervoltage", "HIGH",
                f"⚠ LOW VOLTAGE: {voltage:.1f}V",
                f"Device {device_id} voltage is below normal at {voltage:.1f}V.",
                voltage, t["high"]
            )
            if alert:
                alerts.append(alert)

        # Vibration check
        vibration = reading.get("vibration", 0)
        t = THRESHOLDS["vibration"]
        if vibration >= t["critical"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "HIGH",
                f"⚠ HIGH VIBRATION: {vibration:.3f}{t['unit']}",
                f"Device {device_id} vibration is abnormally high at {vibration:.3f}{t['unit']}.",
                vibration, t["critical"]
            )
            if alert:
                alerts.append(alert)
        elif vibration >= t["warning"]:
            alert = self._create_alert(
                device_id, t["alert_type"], "MEDIUM",
                f"⚠ ELEVATED VIBRATION: {vibration:.3f}{t['unit']}",
                f"Device {device_id} vibration level is elevated.",
                vibration, t["warning"]
            )
            if alert:
                alerts.append(alert)

        return alerts

    def _create_alert(self, device_id: str, alert_type: str, severity: str,
                      title: str, message: str, value: float,
                      threshold: float) -> Optional[AlertEntry]:
        """Create alert with deduplication."""
        key = f"{device_id}:{alert_type}"
        now = time.time()

        # Dedup: skip if same alert type was raised recently
        if now - self._last_alert_time.get(key, 0) < DEDUP_INTERVAL:
            return None

        self._last_alert_time[key] = now

        alert = AlertEntry(
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            value=value,
            threshold=threshold,
        )

        self._recent_alerts.append(alert)

        # Trim stored alerts
        if len(self._recent_alerts) > self._max_stored:
            self._recent_alerts = self._recent_alerts[-self._max_stored:]

        return alert

    def add_fault_alert(self, device_id: str, fault_type: str,
                        severity: str, confidence: float) -> Optional[AlertEntry]:
        """Generate an alert for a detected fault."""
        key = f"{device_id}:fault:{fault_type}"
        now = time.time()

        if now - self._last_alert_time.get(key, 0) < DEDUP_INTERVAL * 2:
            return None

        self._last_alert_time[key] = now

        alert = AlertEntry(
            device_id=device_id,
            alert_type="detected_fault",
            severity=severity,
            title=f"{'🚨' if severity == 'CRITICAL' else '⚠'} FAULT DETECTED: {fault_type}",
            message=(
                f"AI diagnostic system detected '{fault_type}' on device {device_id} "
                f"with {confidence:.1%} confidence. Severity: {severity}. "
                f"Review diagnostic report for details and recommended actions."
            ),
            value=confidence,
        )

        self._recent_alerts.append(alert)
        return alert

    def get_recent_alerts(self, limit: int = 50, device_id: str = None) -> List[dict]:
        """Get recent alerts, optionally filtered by device."""
        alerts = self._recent_alerts
        if device_id:
            alerts = [a for a in alerts if a.device_id == device_id]

        alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        return [a.to_dict() for a in alerts[:limit]]

    def get_unacknowledged_count(self) -> int:
        return sum(1 for a in self._recent_alerts if not a.acknowledged)

    def clear_alerts(self, device_id: str = None):
        """Clear alerts, optionally for a specific device."""
        if device_id:
            self._recent_alerts = [a for a in self._recent_alerts if a.device_id != device_id]
        else:
            self._recent_alerts.clear()
