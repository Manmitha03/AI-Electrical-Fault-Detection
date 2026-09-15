"""
Multi-Modal Diagnostic Engine
================================
Core diagnostic engine that combines ML sensor analysis, image analysis,
and user-provided symptoms to produce comprehensive diagnostic results.

This is the central intelligence of the system — it orchestrates
predictions from multiple sources into a unified diagnosis.
"""

import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from backend.app.services.severity_engine import SeverityEngine
from backend.app.services.troubleshooting import TroubleshootingService


@dataclass
class DiagnosticResult:
    """Comprehensive diagnostic result combining all analysis sources."""
    fault_type: str = "Normal"
    confidence: float = 0.0
    severity: str = "LOW"
    risk_score: int = 0
    evidence: List[str] = field(default_factory=list)
    possible_causes: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    safety_warnings: List[str] = field(default_factory=list)
    troubleshooting_steps: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    sensor_diagnosis: Optional[Dict] = None
    image_diagnosis: Optional[Dict] = None
    symptom_analysis: Optional[Dict] = None
    severity_breakdown: Optional[Dict] = None
    disclaimer: str = (
        "This is an AI-assisted diagnostic tool. It is NOT a certified "
        "electrical safety system. Always consult qualified personnel for "
        "electrical work. Never perform live electrical work without proper "
        "authorization and safety procedures."
    )

    def to_dict(self) -> dict:
        return {
            "fault_type": self.fault_type,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "risk_score": self.risk_score,
            "evidence": self.evidence,
            "possible_causes": self.possible_causes,
            "recommended_actions": self.recommended_actions,
            "safety_warnings": self.safety_warnings,
            "troubleshooting_steps": self.troubleshooting_steps,
            "contributing_factors": self.contributing_factors,
            "sensor_diagnosis": self.sensor_diagnosis,
            "image_diagnosis": self.image_diagnosis,
            "symptom_analysis": self.symptom_analysis,
            "severity_breakdown": self.severity_breakdown,
            "disclaimer": self.disclaimer,
        }


class DiagnosticEngine:
    """
    Central diagnostic engine that combines multiple data sources.

    Data Sources:
    1. ML Sensor Analysis — fault classification from electrical parameters
    2. Image Analysis — visual fault detection from uploaded images
    3. User Symptoms — natural language symptom descriptions
    """

    def __init__(self):
        self.severity_engine = SeverityEngine()
        self.troubleshooting = TroubleshootingService()

    def diagnose(
        self,
        sensor_prediction: Optional[Dict] = None,
        image_analysis: Optional[Dict] = None,
        symptoms: Optional[str] = None,
        sensor_data: Optional[Dict[str, float]] = None,
    ) -> DiagnosticResult:
        """
        Run multi-modal diagnosis.

        Args:
            sensor_prediction: Result from ML predictor (fault_type, confidence, etc.)
            image_analysis: Result from image processor
            symptoms: User-provided symptom description
            sensor_data: Raw sensor readings for severity analysis

        Returns:
            DiagnosticResult combining all evidence sources.
        """
        result = DiagnosticResult()
        evidence = []
        fault_votes = {}  # fault_type -> weighted score

        # ── Source 1: ML Sensor Prediction ──
        if sensor_prediction:
            fault_type = sensor_prediction.get("fault_type", "Normal")
            confidence = sensor_prediction.get("confidence", 0.0)

            # Weight sensor prediction heavily
            fault_votes[fault_type] = fault_votes.get(fault_type, 0) + confidence * 0.5

            result.sensor_diagnosis = {
                "fault_type": fault_type,
                "confidence": confidence,
                "contributing_factors": sensor_prediction.get("contributing_factors", []),
            }

            if fault_type != "Normal":
                evidence.append(f"ML sensor analysis: {fault_type} (confidence: {confidence:.1%})")
                for factor in sensor_prediction.get("contributing_factors", []):
                    evidence.append(f"  ✓ {factor}")

        # ── Source 2: Image Analysis ──
        if image_analysis and image_analysis.get("valid", False):
            indicators = image_analysis.get("fault_indicators", [])
            img_confidence = image_analysis.get("confidence", 0.0)
            img_severity = image_analysis.get("severity", "LOW")

            result.image_diagnosis = {
                "fault_indicators": indicators,
                "confidence": img_confidence,
                "severity": img_severity,
            }

            # Map image indicators to fault types
            for indicator in indicators:
                indicator_lower = indicator.lower()
                if "burn" in indicator_lower or "char" in indicator_lower:
                    fault_votes["Burnt Component"] = fault_votes.get("Burnt Component", 0) + 0.2
                    fault_votes["Overheating"] = fault_votes.get("Overheating", 0) + 0.15
                    evidence.append(f"Image analysis: {indicator}")
                elif "corrosion" in indicator_lower or "oxidation" in indicator_lower:
                    fault_votes["Corrosion"] = fault_votes.get("Corrosion", 0) + 0.25
                    evidence.append(f"Image analysis: {indicator}")
                elif "discoloration" in indicator_lower:
                    fault_votes["Overheating"] = fault_votes.get("Overheating", 0) + 0.15
                    evidence.append(f"Image analysis: {indicator}")
                elif "thermal" in indicator_lower or "hotspot" in indicator_lower:
                    fault_votes["Overheating"] = fault_votes.get("Overheating", 0) + 0.25
                    evidence.append(f"Image analysis: {indicator}")
                elif "crack" in indicator_lower or "damage" in indicator_lower:
                    fault_votes["Insulation Damage"] = fault_votes.get("Insulation Damage", 0) + 0.2
                    evidence.append(f"Image analysis: {indicator}")
                elif "no obvious" not in indicator_lower:
                    evidence.append(f"Image analysis: {indicator}")

        # ── Source 3: User Symptoms ──
        if symptoms:
            symptom_faults = self._analyze_symptoms(symptoms)
            result.symptom_analysis = {
                "original_text": symptoms,
                "matched_faults": symptom_faults,
            }

            for fault_type, score in symptom_faults.items():
                fault_votes[fault_type] = fault_votes.get(fault_type, 0) + score * 0.3
                evidence.append(f"User symptom match: {fault_type}")

        # ── Determine Final Fault Type ──
        if fault_votes:
            # Remove "Normal" if other faults have votes
            if len(fault_votes) > 1 and "Normal" in fault_votes:
                del fault_votes["Normal"]

            # Select highest-scoring fault
            final_fault = max(fault_votes, key=fault_votes.get)
            final_score = fault_votes[final_fault]
            result.fault_type = final_fault
            result.confidence = min(0.99, final_score)
        else:
            result.fault_type = "Normal"
            result.confidence = 0.85

        result.evidence = evidence

        # ── Severity Analysis ──
        if sensor_data:
            severity_result = self.severity_engine.analyze(
                sensor_data=sensor_data,
                fault_type=result.fault_type,
                ml_confidence=result.confidence,
                image_severity=image_analysis.get("severity") if image_analysis else None,
                visual_damage_score=image_analysis.get("confidence", 0.0) if image_analysis else 0.0,
            )
            result.severity = severity_result.severity
            result.risk_score = severity_result.risk_score
            result.severity_breakdown = severity_result.to_dict()
        else:
            # Estimate severity from confidence
            if result.confidence > 0.85:
                result.severity = "HIGH"
                result.risk_score = 75
            elif result.confidence > 0.6:
                result.severity = "MEDIUM"
                result.risk_score = 50
            else:
                result.severity = "LOW"
                result.risk_score = 25

        # ── Troubleshooting ──
        ts_entry = self.troubleshooting.get_troubleshooting(result.fault_type)
        if ts_entry:
            result.possible_causes = ts_entry.possible_causes
            result.recommended_actions = ts_entry.recommended_actions
            result.safety_warnings = ts_entry.safety_warnings
            result.troubleshooting_steps = ts_entry.diagnostic_steps
        else:
            result.recommended_actions = [
                "Inspect the equipment for visible damage.",
                "Isolate power if any safety concern exists.",
                "Contact qualified personnel for evaluation.",
            ]
            result.safety_warnings = [
                "⚠ Always follow proper electrical safety procedures.",
                "🚨 Never work on energized equipment without authorization.",
            ]

        # ── Contributing Factors (from ML) ──
        if sensor_prediction:
            result.contributing_factors = sensor_prediction.get("contributing_factors", [])

        return result

    def _analyze_symptoms(self, symptoms: str) -> Dict[str, float]:
        """Map natural language symptoms to fault types with relevance scores."""
        symptoms_lower = symptoms.lower()
        matches = {}

        symptom_map = {
            "Overheating": [
                ("hot", 0.7), ("heat", 0.7), ("warm", 0.5), ("burning", 0.8),
                ("smoke", 0.6), ("smell", 0.5), ("temperature", 0.6),
                ("thermal", 0.7), ("overheating", 1.0),
            ],
            "Short Circuit": [
                ("spark", 0.8), ("arc", 0.7), ("pop", 0.5), ("flash", 0.7),
                ("explosion", 0.6), ("short", 0.8), ("bang", 0.5),
            ],
            "Overvoltage": [
                ("high voltage", 0.9), ("surge", 0.7), ("overvoltage", 1.0),
                ("bright", 0.3), ("spike", 0.6),
            ],
            "Undervoltage": [
                ("low voltage", 0.9), ("dim", 0.6), ("undervoltage", 1.0),
                ("weak", 0.4), ("brownout", 0.8), ("sag", 0.6),
            ],
            "Overcurrent": [
                ("trip", 0.6), ("breaker", 0.7), ("overload", 0.8),
                ("overcurrent", 1.0), ("fuse", 0.5), ("amperage", 0.5),
            ],
            "Loose Connection": [
                ("flicker", 0.7), ("intermittent", 0.7), ("loose", 0.9),
                ("unstable", 0.5), ("fluctuat", 0.6), ("connection", 0.5),
                ("noise", 0.4), ("rattle", 0.5), ("vibrat", 0.5),
            ],
            "Burnt Component": [
                ("burnt", 0.9), ("burned", 0.9), ("melted", 0.8),
                ("charred", 0.9), ("blackened", 0.7), ("destroyed", 0.5),
            ],
            "Insulation Damage": [
                ("shock", 0.7), ("tingle", 0.7), ("insulation", 0.9),
                ("crack", 0.5), ("exposed wire", 0.8), ("bare", 0.5),
                ("damaged cable", 0.7), ("frayed", 0.7),
            ],
            "Corrosion": [
                ("corroded", 0.9), ("corrosion", 1.0), ("rust", 0.7),
                ("green", 0.4), ("oxidiz", 0.7), ("deteriorat", 0.5),
            ],
        }

        for fault_type, keywords in symptom_map.items():
            for keyword, weight in keywords:
                if keyword in symptoms_lower:
                    matches[fault_type] = max(matches.get(fault_type, 0), weight)

        return matches
