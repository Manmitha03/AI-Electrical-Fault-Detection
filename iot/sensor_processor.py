"""
Sensor Data Processor
=======================
Processes raw sensor readings, detects anomalies via moving averages,
trend detection, and threshold checks. Feeds into the alert engine.
"""

from typing import Dict, List, Optional
from collections import deque
import numpy as np


class SensorProcessor:
    """
    Processes sensor streams for anomaly detection.

    Features:
    - Moving average calculation
    - Trend detection (rising, falling, stable)
    - Rate-of-change monitoring
    """

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        # Per-device, per-feature history
        self._history: Dict[str, Dict[str, deque]] = {}

    def _ensure_device(self, device_id: str):
        if device_id not in self._history:
            features = [
                "voltage", "current", "temperature", "power",
                "power_factor", "frequency", "resistance", "vibration",
            ]
            self._history[device_id] = {
                f: deque(maxlen=self.window_size) for f in features
            }

    def process_reading(self, reading: dict) -> dict:
        """
        Process a sensor reading and return enriched data with trends.

        Args:
            reading: Dict with device_id and sensor values.

        Returns:
            Enriched reading with moving averages and trends.
        """
        device_id = reading.get("device_id", "unknown")
        self._ensure_device(device_id)

        enriched = dict(reading)
        trends = {}
        moving_averages = {}
        anomalies = []

        features = ["voltage", "current", "temperature", "power",
                     "power_factor", "frequency", "resistance", "vibration"]

        for feature in features:
            value = reading.get(feature)
            if value is None:
                continue

            history = self._history[device_id][feature]
            history.append(value)

            if len(history) >= 3:
                # Moving average
                avg = float(np.mean(list(history)))
                moving_averages[feature] = round(avg, 3)

                # Trend detection
                recent = list(history)[-5:]  # last 5 readings
                if len(recent) >= 3:
                    trend = self._detect_trend(recent)
                    trends[feature] = trend

                    # Rate of change
                    if len(recent) >= 2:
                        roc = (recent[-1] - recent[0]) / max(len(recent), 1)
                        if abs(roc) > avg * 0.1:  # >10% change rate
                            anomalies.append({
                                "feature": feature,
                                "type": "rapid_change",
                                "rate": round(roc, 3),
                                "direction": "increasing" if roc > 0 else "decreasing",
                            })

        enriched["moving_averages"] = moving_averages
        enriched["trends"] = trends
        enriched["anomalies"] = anomalies

        return enriched

    def _detect_trend(self, values: list) -> str:
        """Detect trend direction from a series of values."""
        if len(values) < 3:
            return "stable"

        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        avg_diff = np.mean(diffs)
        std_diff = np.std(diffs) if len(diffs) > 1 else 0

        threshold = abs(np.mean(values)) * 0.02  # 2% of mean

        if avg_diff > threshold:
            return "rising"
        elif avg_diff < -threshold:
            return "falling"
        return "stable"

    def get_device_summary(self, device_id: str) -> dict:
        """Get statistical summary for a device."""
        if device_id not in self._history:
            return {}

        summary = {}
        for feature, history in self._history[device_id].items():
            if len(history) > 0:
                values = list(history)
                summary[feature] = {
                    "current": round(values[-1], 3),
                    "mean": round(float(np.mean(values)), 3),
                    "min": round(float(np.min(values)), 3),
                    "max": round(float(np.max(values)), 3),
                    "std": round(float(np.std(values)), 3),
                    "samples": len(values),
                }
        return summary

    def clear_device(self, device_id: str):
        """Clear history for a device."""
        if device_id in self._history:
            del self._history[device_id]
