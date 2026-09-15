"""
Shared Application State
===========================
Global service instances shared across the application.
Avoids circular imports between main.py and API route files.
"""

from backend.app.services.ml_predictor import MLPredictorService
from backend.app.services.diagnostic_engine import DiagnosticEngine
from backend.app.services.alert_engine import AlertEngine
from backend.app.services.chatbot_service import ChatbotService
from backend.app.services.image_processor import ImageProcessor
from iot.simulator import IoTSimulator
from iot.sensor_processor import SensorProcessor

# ─── Singleton Service Instances ──────────────────────────────

ml_predictor = MLPredictorService()
diagnostic_engine = DiagnosticEngine()
alert_engine = AlertEngine()
chatbot_service = ChatbotService()
image_processor = ImageProcessor()
iot_simulator = IoTSimulator()
sensor_processor = SensorProcessor()
