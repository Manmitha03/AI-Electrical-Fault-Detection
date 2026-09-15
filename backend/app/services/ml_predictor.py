"""
ML Predictor Service — FastAPI Integration Wrapper
=====================================================
Thin wrapper around ml/predictor.py for FastAPI integration.
Handles lazy model loading on first request.
"""

import os
import sys
from typing import Dict, Optional

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ml.predictor import FaultPredictor, PredictionResult


class MLPredictorService:
    """Service wrapper for the ML fault predictor."""

    def __init__(self):
        self._predictor = None
        self._model_dir = os.path.join(PROJECT_ROOT, "ml", "models")

    def _ensure_loaded(self):
        """Lazy-load the model on first use."""
        if self._predictor is None:
            self._predictor = FaultPredictor(model_dir=self._model_dir)
            if not self._predictor.is_loaded:
                loaded = self._predictor.load_model()
                if not loaded:
                    print("  [WARNING] ML model not available. Run train_model.py first.")

    def predict(self, sensor_data: Dict[str, float]) -> Optional[Dict]:
        """
        Make a fault prediction from sensor data.

        Returns dict with fault_type, confidence, contributing_factors, etc.
        Returns None if model is not available.
        """
        self._ensure_loaded()

        if self._predictor is None or not self._predictor.is_loaded:
            return None

        try:
            result = self._predictor.predict(sensor_data)
            return result.to_dict()
        except Exception as e:
            print(f"  [ERROR] ML prediction failed: {e}")
            return None

    def predict_top_n(self, sensor_data: Dict[str, float], n: int = 3) -> list:
        """Return top-N predictions."""
        self._ensure_loaded()

        if self._predictor is None or not self._predictor.is_loaded:
            return []

        try:
            return self._predictor.predict_top_n(sensor_data, n=n)
        except Exception as e:
            print(f"  [ERROR] ML prediction failed: {e}")
            return []

    def get_model_info(self) -> Optional[dict]:
        """Get model metadata."""
        self._ensure_loaded()
        if self._predictor:
            return self._predictor.get_model_info()
        return None

    @property
    def is_available(self) -> bool:
        """Check if ML model is loaded and ready."""
        self._ensure_loaded()
        return self._predictor is not None and self._predictor.is_loaded
