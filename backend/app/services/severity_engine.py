"""
Severity Analysis Engine
==========================
Multi-factor severity scoring for electrical faults.
Produces a risk score (0-100) and severity level (LOW/MEDIUM/HIGH/CRITICAL).

The scoring approach is explainable and transparent — not a black box.
This is NOT a certified electrical safety standard.
"""

from typing import Dict, List, Optional, Tuple


# Severity thresholds
SEVERITY_LEVELS = {
    "LOW": (0, 30),
    "MEDIUM": (31, 55),
    "HIGH": (56, 80),
    "CRITICAL": (81, 100),
}

# Normal operating ranges
NORMAL_RANGES = {
    "voltage": (220, 240),
    "current": (5, 15),
    "temperature": (20, 45),
    "power": (1100, 3600),
    "power_factor": (0.85, 0.99),
    "frequency": (49.5, 50.5),
    "resistance": (10, 50),
    "vibration": (0.01, 0.15),
}

# Weights for each factor in overall risk score
FACTOR_WEIGHTS = {
    "temperature": 0.25,
    "current": 0.20,
    "voltage": 0.15,
    "visual_damage": 0.15,
    "power_factor": 0.10,
    "vibration": 0.08,
    "resistance": 0.05,
    "frequency": 0.02,
}


class SeverityResult:
    """Structured severity analysis result."""

    def __init__(self, severity: str, risk_score: int,
                 factor_scores: Dict[str, dict], warnings: List[str]):
        self.severity = severity
        self.risk_score = risk_score
        self.factor_scores = factor_scores
        self.warnings = warnings

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "risk_score": self.risk_score,
            "factor_scores": self.factor_scores,
            "warnings": self.warnings,
        }


class SeverityEngine:
    """
    Calculates severity and risk score from sensor data and diagnostic results.

    The risk score is computed as a weighted sum of individual factor scores,
    each measuring how far a parameter deviates from its normal range.
    """

    def analyze(
        self,
        sensor_data: Dict[str, float],
        fault_type: str = "Normal",
        ml_confidence: float = 0.0,
        image_severity: Optional[str] = None,
        visual_damage_score: float = 0.0,
    ) -> SeverityResult:
        """
        Perform severity analysis.

        Args:
            sensor_data: Current sensor readings.
            fault_type: Detected fault type from ML.
            ml_confidence: ML prediction confidence.
            image_severity: Severity from image analysis (if available).
            visual_damage_score: 0-1 score from image analysis.

        Returns:
            SeverityResult with severity level, risk score, and breakdown.
        """
        factor_scores = {}
        warnings = []

        # ── Temperature Score ──
        temp = sensor_data.get("temperature", 25)
        temp_score, temp_detail = self._score_temperature(temp)
        factor_scores["temperature"] = {
            "value": temp,
            "score": temp_score,
            "weight": FACTOR_WEIGHTS["temperature"],
            "detail": temp_detail,
        }
        if temp_score > 70:
            warnings.append(f"⚠ Temperature critically high: {temp:.1f}°C")

        # ── Current Score ──
        current = sensor_data.get("current", 10)
        curr_score, curr_detail = self._score_current(current)
        factor_scores["current"] = {
            "value": current,
            "score": curr_score,
            "weight": FACTOR_WEIGHTS["current"],
            "detail": curr_detail,
        }
        if curr_score > 70:
            warnings.append(f"⚠ Current dangerously high: {current:.1f}A")

        # ── Voltage Score ──
        voltage = sensor_data.get("voltage", 230)
        volt_score, volt_detail = self._score_voltage(voltage)
        factor_scores["voltage"] = {
            "value": voltage,
            "score": volt_score,
            "weight": FACTOR_WEIGHTS["voltage"],
            "detail": volt_detail,
        }
        if volt_score > 70:
            warnings.append(f"⚠ Voltage significantly abnormal: {voltage:.1f}V")

        # ── Power Factor Score ──
        pf = sensor_data.get("power_factor", 0.95)
        pf_score, pf_detail = self._score_power_factor(pf)
        factor_scores["power_factor"] = {
            "value": pf,
            "score": pf_score,
            "weight": FACTOR_WEIGHTS["power_factor"],
            "detail": pf_detail,
        }

        # ── Vibration Score ──
        vib = sensor_data.get("vibration", 0.05)
        vib_score, vib_detail = self._score_vibration(vib)
        factor_scores["vibration"] = {
            "value": vib,
            "score": vib_score,
            "weight": FACTOR_WEIGHTS["vibration"],
            "detail": vib_detail,
        }

        # ── Resistance Score ──
        res = sensor_data.get("resistance", 25)
        res_score, res_detail = self._score_resistance(res)
        factor_scores["resistance"] = {
            "value": res,
            "score": res_score,
            "weight": FACTOR_WEIGHTS["resistance"],
            "detail": res_detail,
        }

        # ── Frequency Score ──
        freq = sensor_data.get("frequency", 50.0)
        freq_score, freq_detail = self._score_frequency(freq)
        factor_scores["frequency"] = {
            "value": freq,
            "score": freq_score,
            "weight": FACTOR_WEIGHTS["frequency"],
            "detail": freq_detail,
        }

        # ── Visual Damage Score ──
        vis_score = int(visual_damage_score * 100)
        factor_scores["visual_damage"] = {
            "value": visual_damage_score,
            "score": vis_score,
            "weight": FACTOR_WEIGHTS["visual_damage"],
            "detail": "Visual damage detected" if vis_score > 30 else "No visual damage",
        }
        if vis_score > 50:
            warnings.append("⚠ Significant visual damage detected in image analysis")

        # ── Calculate Weighted Risk Score ──
        risk_score = 0
        for factor_name, factor_data in factor_scores.items():
            weight = factor_data["weight"]
            score = factor_data["score"]
            risk_score += weight * score

        # Apply fault-type multiplier for known dangerous faults
        fault_multiplier = self._get_fault_multiplier(fault_type)
        risk_score = risk_score * fault_multiplier

        # Apply ML confidence boost (high confidence in a fault = more severe)
        if fault_type != "Normal" and ml_confidence > 0.8:
            confidence_boost = (ml_confidence - 0.8) * 50  # up to +10 points
            risk_score += confidence_boost

        # Image severity override check
        if image_severity == "CRITICAL":
            risk_score = max(risk_score, 85)
        elif image_severity == "HIGH":
            risk_score = max(risk_score, 60)

        risk_score = int(min(100, max(0, risk_score)))

        # Determine severity level
        severity = self._risk_to_severity(risk_score)

        # Safety warnings for critical conditions
        if severity == "CRITICAL":
            warnings.append("🚨 CRITICAL: Immediate attention required. Isolate power if safe to do so.")
        elif severity == "HIGH":
            warnings.append("⚠ HIGH severity: Schedule immediate inspection.")

        return SeverityResult(
            severity=severity,
            risk_score=risk_score,
            factor_scores=factor_scores,
            warnings=warnings,
        )

    def _score_temperature(self, temp: float) -> Tuple[int, str]:
        """Score temperature deviation. Max danger at 120°C+."""
        if temp <= 45:
            return 0, "Normal operating temperature"
        elif temp <= 60:
            return 25, "Slightly elevated temperature"
        elif temp <= 75:
            return 50, "Elevated temperature - monitor closely"
        elif temp <= 95:
            return 75, "High temperature - potential overheating"
        elif temp <= 120:
            return 90, "Very high temperature - likely overheating"
        else:
            return 100, "Critical temperature - immediate danger"

    def _score_current(self, current: float) -> Tuple[int, str]:
        """Score current deviation."""
        if 5 <= current <= 15:
            return 0, "Normal current range"
        elif current <= 20:
            return 25, "Slightly elevated current"
        elif current <= 30:
            return 55, "High current draw"
        elif current <= 50:
            return 80, "Very high current - overcurrent condition"
        else:
            return 100, "Dangerous current level - possible short circuit"

    def _score_voltage(self, voltage: float) -> Tuple[int, str]:
        """Score voltage deviation."""
        if 220 <= voltage <= 240:
            return 0, "Normal voltage range"
        elif 200 <= voltage < 220 or 240 < voltage <= 260:
            return 25, "Slight voltage deviation"
        elif 180 <= voltage < 200 or 260 < voltage <= 280:
            return 55, "Significant voltage deviation"
        elif 150 <= voltage < 180 or 280 < voltage <= 310:
            return 80, "Severe voltage abnormality"
        else:
            return 100, "Critical voltage abnormality"

    def _score_power_factor(self, pf: float) -> Tuple[int, str]:
        """Score power factor deviation."""
        if pf >= 0.85:
            return 0, "Good power factor"
        elif pf >= 0.70:
            return 30, "Reduced power factor"
        elif pf >= 0.50:
            return 60, "Poor power factor"
        else:
            return 85, "Very poor power factor - electrical issue likely"

    def _score_vibration(self, vib: float) -> Tuple[int, str]:
        """Score vibration level."""
        if vib <= 0.15:
            return 0, "Normal vibration"
        elif vib <= 0.30:
            return 30, "Elevated vibration"
        elif vib <= 0.50:
            return 60, "High vibration - mechanical issue possible"
        else:
            return 90, "Severe vibration - inspect immediately"

    def _score_resistance(self, res: float) -> Tuple[int, str]:
        """Score resistance deviation."""
        if 10 <= res <= 50:
            return 0, "Normal resistance"
        elif res < 10:
            if res < 2:
                return 80, "Very low resistance - possible short"
            return 40, "Low resistance"
        elif res <= 100:
            return 30, "Elevated resistance"
        elif res <= 200:
            return 60, "High resistance - connection issue"
        else:
            return 85, "Very high resistance - component damage likely"

    def _score_frequency(self, freq: float) -> Tuple[int, str]:
        """Score frequency deviation."""
        deviation = abs(freq - 50.0)
        if deviation <= 0.5:
            return 0, "Normal frequency"
        elif deviation <= 1.0:
            return 25, "Slight frequency deviation"
        elif deviation <= 2.0:
            return 55, "Frequency deviation detected"
        else:
            return 80, "Significant frequency deviation"

    def _get_fault_multiplier(self, fault_type: str) -> float:
        """Apply multiplier based on inherent danger of fault type."""
        multipliers = {
            "Normal": 0.3,
            "Overheating": 1.1,
            "Short Circuit": 1.3,
            "Overvoltage": 1.1,
            "Undervoltage": 0.9,
            "Overcurrent": 1.2,
            "Loose Connection": 1.0,
            "Burnt Component": 1.25,
            "Insulation Damage": 1.15,
            "Corrosion": 0.85,
        }
        return multipliers.get(fault_type, 1.0)

    def _risk_to_severity(self, risk_score: int) -> str:
        """Map risk score to severity level."""
        for level, (low, high) in SEVERITY_LEVELS.items():
            if low <= risk_score <= high:
                return level
        return "CRITICAL"
