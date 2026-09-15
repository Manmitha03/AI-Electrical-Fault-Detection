"""
Optional MQTT Client for IoT Integration
===========================================
Provides MQTT publish/subscribe for sensor data.
Gracefully falls back when MQTT broker is unavailable.

Configuration via environment variables:
    MQTT_ENABLED=true|false
    MQTT_BROKER=localhost
    MQTT_PORT=1883
    MQTT_TOPIC_PREFIX=electrical/sensors

To connect real ESP32/Arduino devices:
    Publish sensor JSON to: electrical/sensors/{device_id}
    Subscribe to commands: electrical/commands/{device_id}
"""

import os
import json
import threading
from typing import Callable, Optional

MQTT_ENABLED = os.getenv("MQTT_ENABLED", "false").lower() == "true"
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "electrical/sensors")

# Try to import paho-mqtt
try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False


class MQTTClient:
    """
    Optional MQTT client for IoT sensor data.

    Falls back gracefully when MQTT is not available or disabled.
    Designed so that real IoT devices (ESP32, Arduino) can publish
    sensor data to the MQTT broker and this client will receive it.
    """

    def __init__(self):
        self._client = None
        self._connected = False
        self._on_message_callback: Optional[Callable] = None
        self._enabled = MQTT_ENABLED and PAHO_AVAILABLE

    @property
    def is_available(self) -> bool:
        return self._enabled and self._connected

    def connect(self) -> bool:
        """Connect to MQTT broker. Returns False if unavailable."""
        if not self._enabled:
            print("  [MQTT] MQTT is disabled or paho-mqtt not installed. Using simulator only.")
            return False

        try:
            self._client = mqtt.Client(client_id="fault-detection-server")
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message

            self._client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self._client.loop_start()
            return True
        except Exception as e:
            print(f"  [MQTT] Connection failed: {e}. Using simulator only.")
            self._enabled = False
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self._client and self._connected:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def publish_reading(self, device_id: str, reading: dict):
        """Publish a sensor reading to MQTT."""
        if not self.is_available:
            return

        topic = f"{MQTT_TOPIC_PREFIX}/{device_id}"
        payload = json.dumps(reading)
        self._client.publish(topic, payload, qos=1)

    def subscribe_readings(self, callback: Callable):
        """Subscribe to sensor readings from all devices."""
        self._on_message_callback = callback
        if self.is_available:
            topic = f"{MQTT_TOPIC_PREFIX}/+"
            self._client.subscribe(topic, qos=1)
            print(f"  [MQTT] Subscribed to {topic}")

    def publish_command(self, device_id: str, command: dict):
        """Publish a command to a device."""
        if not self.is_available:
            return

        topic = f"electrical/commands/{device_id}"
        payload = json.dumps(command)
        self._client.publish(topic, payload, qos=1)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            print(f"  [MQTT] Connected to {MQTT_BROKER}:{MQTT_PORT}")
            # Re-subscribe on reconnect
            if self._on_message_callback:
                client.subscribe(f"{MQTT_TOPIC_PREFIX}/+", qos=1)
        else:
            print(f"  [MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            print(f"  [MQTT] Unexpected disconnection (rc={rc})")

    def _on_message(self, client, userdata, msg):
        if self._on_message_callback:
            try:
                payload = json.loads(msg.payload.decode())
                device_id = msg.topic.split("/")[-1]
                payload["device_id"] = device_id
                self._on_message_callback(payload)
            except Exception as e:
                print(f"  [MQTT] Error processing message: {e}")
