"""
Fault Predictor — Inference Module
====================================
Thread-safe singleton for loading the trained ML model and making
predictions with confidence scores and feature importance.

Usage:
    from ml.predictor import FaultPredictor

    predictor = FaultPredictor()
    result = predictor.predict({
        "voltage": 185, "current": 17.5, "temperature": 81,
        "power": 3330, "power_factor": 0.72, "frequency": 50,
        "resistance": 25, "vibration": 0.45
    })
"""

import os
import json
import threading
import numpy as np
import joblib
from typing import Dict, List, Optional

FEATURE_COLUMNS = [
    "voltage", "current", "temperature", "power",
    "power_factor", "frequency", "resistance", "vibration",
]

FAULT_TYPES = {
    0: "Normal",
    1: "Overheating",
    2: "Short Circuit",
    3: "Overvoltage",
    4: "Undervoltage",
    5: "Overcurrent",
    6: "Loose Connection",
    7: "Burnt Component",
    8: "Insulation Damage",
    9: "Corrosion",
}

# Normal operating ranges for feature importance context
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


class PredictionResult:
    """Structured result from fault prediction."""

    def __init__(
        self,
        fault_type: str,
        fault_code: int,
        confidence: float,
        all_probabilities: Dict[str, float],
        feature_importance: Dict[str, float],
        contributing_factors: List[str],
        sensor_values: Dict[str, float],
    ):
        self.fault_type = fault_type
        self.fault_code = fault_code
        self.confidence = confidence
        self.all_probabilities = all_probabilities
        self.feature_importance = feature_importance
        self.contributing_factors = contributing_factors
        self.sensor_values = sensor_values

    def to_dict(self) -> dict:
        return {
            "fault_type": self.fault_type,
            "fault_code": self.fault_code,
            "confidence": round(self.confidence, 4),
            "all_probabilities": {k: round(v, 4) for k, v in self.all_probabilities.items()},
            "feature_importance": {k: round(v, 4) for k, v in self.feature_importance.items()},
            "contributing_factors": self.contributing_factors,
            "sensor_values": self.sensor_values,
        }


class FaultPredictor:
    """
    Thread-safe fault prediction engine.

    Loads the trained model once and provides prediction with
    confidence scores and explainability features.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_dir: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_dir: str = None):
        if self._initialized:
            return

        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), "models")

        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.metadata = None
        self._model_loaded = False
        self._initialized = True

    def load_model(self) -> bool:
        """Load the trained model from disk."""
        try:
            model_path = os.path.join(self.model_dir, "fault_classifier.joblib")
            scaler_path = os.path.join(self.model_dir, "scaler.joblib")
            encoder_path = os.path.join(self.model_dir, "label_encoder.joblib")
            metadata_path = os.path.join(self.model_dir, "model_metadata.json")

            if not os.path.exists(model_path):
                print(f"  [WARNING] Model not found at {model_path}")
                return False

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(encoder_path)

            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

            self._model_loaded = True
            print(f"  [ML] Model loaded: {self.metadata.get('model_name', 'Unknown')}")
            return True

        except Exception as e:
            print(f"  [ERROR] Failed to load model: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._model_loaded

    def predict(self, sensor_data: Dict[str, float]) -> PredictionResult:
        """
        Make a fault prediction from sensor readings.

        Args:
            sensor_data: Dict with keys matching FEATURE_COLUMNS.

        Returns:
            PredictionResult with fault type, confidence, and contributing factors.
        """
        if not self._model_loaded:
            if not self.load_model():
                raise RuntimeError("ML model not loaded. Run train_model.py first.")

        # Build feature vector
        features = np.array([[sensor_data.get(col, 0.0) for col in FEATURE_COLUMNS]])

        # Scale
        features_scaled = self.scaler.transform(features)

        # Predict with probabilities
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        # Map to fault type
        fault_code = int(self.label_encoder.inverse_transform([prediction])[0])
        fault_type = FAULT_TYPES.get(fault_code, "Unknown")
        confidence = float(probabilities[prediction])

        # All class probabilities
        all_probs = {}
        for i, prob in enumerate(probabilities):
            class_code = int(self.label_encoder.inverse_transform([i])[0])
            all_probs[FAULT_TYPES.get(class_code, f"Class_{class_code}")] = float(prob)

        # Feature importance from model
        feature_imp = {}
        if hasattr(self.model, "feature_importances_"):
            for i, col in enumerate(FEATURE_COLUMNS):
                feature_imp[col] = float(self.model.feature_importances_[i])

        # Contributing factors analysis
        contributing_factors = self._analyze_contributing_factors(sensor_data)

        return PredictionResult(
            fault_type=fault_type,
            fault_code=fault_code,
            confidence=confidence,
            all_probabilities=all_probs,
            feature_importance=feature_imp,
            contributing_factors=contributing_factors,
            sensor_values=sensor_data,
        )

    def predict_top_n(self, sensor_data: Dict[str, float], n: int = 3) -> List[dict]:
        """Return top-N most likely fault predictions."""
        result = self.predict(sensor_data)
        sorted_probs = sorted(
            result.all_probabilities.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {"fault_type": ft, "confidence": round(conf, 4)}
            for ft, conf in sorted_probs[:n]
        ]

    def _analyze_contributing_factors(self, sensor_data: Dict[str, float]) -> List[str]:
        """Analyze which sensor values are outside normal ranges."""
        factors = []

        for feature, (low, high) in NORMAL_RANGES.items():
            value = sensor_data.get(feature, None)
            if value is None:
                continue

            if feature == "voltage":
                if value > high * 1.1:
                    factors.append(f"Voltage is significantly above normal range ({value:.1f}V vs {low}-{high}V)")
                elif value < low * 0.85:
                    factors.append(f"Voltage is significantly below normal range ({value:.1f}V vs {low}-{high}V)")
            elif feature == "current":
                if value > high * 1.3:
                    factors.append(f"Current is significantly above normal range ({value:.1f}A vs {low}-{high}A)")
            elif feature == "temperature":
                if value > high * 1.5:
                    factors.append(f"Temperature is critically elevated ({value:.1f}°C vs normal {low}-{high}°C)")
                elif value > high * 1.2:
                    factors.append(f"Temperature is above normal range ({value:.1f}°C vs normal {low}-{high}°C)")
            elif feature == "power_factor":
                if value < low * 0.85:
                    factors.append(f"Power factor is significantly reduced ({value:.2f} vs normal {low}-{high})")
            elif feature == "resistance":
                if value > high * 2:
                    factors.append(f"Resistance is abnormally high ({value:.1f}Ω vs normal {low}-{high}Ω)")
                elif value < low * 0.3:
                    factors.append(f"Resistance is abnormally low ({value:.1f}Ω vs normal {low}-{high}Ω)")
            elif feature == "vibration":
                if value > high * 2:
                    factors.append(f"Vibration level is elevated ({value:.3f}g vs normal {low}-{high}g)")
            elif feature == "power":
                if value > high * 1.5:
                    factors.append(f"Power consumption is elevated ({value:.0f}W vs normal {low}-{high}W)")
            elif feature == "frequency":
                if abs(value - 50.0) > 1.5:
                    factors.append(f"Frequency deviation detected ({value:.1f}Hz vs normal {low}-{high}Hz)")

        if not factors:
            factors.append("All sensor readings are within normal ranges")

        return factors

    def get_model_info(self) -> Optional[dict]:
        """Return model metadata for API responses."""
        if self.metadata:
            return {
                "model_name": self.metadata.get("model_name"),
                "model_type": self.metadata.get("model_type"),
                "features": FEATURE_COLUMNS,
                "fault_types": list(FAULT_TYPES.values()),
                "training_date": self.metadata.get("training_date"),
                "metrics": self.metadata.get("metrics"),
                "feature_importance": self.metadata.get("feature_importance"),
            }
        return None
