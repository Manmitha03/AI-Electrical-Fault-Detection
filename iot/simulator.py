"""
IoT Sensor Simulator
======================
Simulates realistic sensor readings from 4 electrical monitoring devices.
Supports normal operation and configurable fault injection for demo scenarios.

Devices:
    PANEL-001       — Main Electrical Panel
    MOTOR-002       — Industrial Motor
    TRANSFORMER-003 — Distribution Transformer
    MACHINE-004     — CNC Machine

The simulator is designed so that real ESP32/Arduino/MQTT data
can replace the simulated data by swapping the data source.
"""

import asyncio
import random
import time
import math
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class DeviceConfig:
    """Configuration for a simulated device."""
    device_id: str
    name: str
    device_type: str
    location: str
    # Normal operating ranges
    voltage_range: tuple = (228, 232)
    current_range: tuple = (8, 12)
    temperature_range: tuple = (25, 40)
    frequency_range: tuple = (49.8, 50.2)
    power_factor_range: tuple = (0.90, 0.96)
    resistance_range: tuple = (15, 35)
    vibration_range: tuple = (0.02, 0.10)


# Default device configurations
DEFAULT_DEVICES = [
    DeviceConfig(
        device_id="PANEL-001",
        name="Main Electrical Panel",
        device_type="panel",
        location="Building A, Floor 1",
        voltage_range=(228, 234),
        current_range=(8, 14),
        temperature_range=(22, 38),
    ),
    DeviceConfig(
        device_id="MOTOR-002",
        name="Industrial Motor Unit",
        device_type="motor",
        location="Workshop B, Zone 3",
        voltage_range=(225, 235),
        current_range=(10, 15),
        temperature_range=(30, 50),
        vibration_range=(0.03, 0.12),
    ),
    DeviceConfig(
        device_id="TRANSFORMER-003",
        name="Distribution Transformer",
        device_type="transformer",
        location="Substation C",
        voltage_range=(230, 236),
        current_range=(5, 10),
        temperature_range=(35, 55),
        power_factor_range=(0.92, 0.98),
    ),
    DeviceConfig(
        device_id="MACHINE-004",
        name="CNC Machine Controller",
        device_type="machine",
        location="Workshop B, Zone 5",
        voltage_range=(226, 234),
        current_range=(6, 12),
        temperature_range=(25, 45),
        vibration_range=(0.04, 0.15),
    ),
]


# Fault injection profiles
FAULT_PROFILES = {
    "normal": {},
    "overheating": {
        "temperature_range": (75, 110),
        "current_range": (14, 22),
        "power_factor_range": (0.65, 0.80),
        "vibration_range": (0.12, 0.35),
    },
    "short_circuit": {
        "voltage_range": (80, 160),
        "current_range": (40, 85),
        "temperature_range": (90, 140),
        "resistance_range": (0.5, 3.0),
        "power_factor_range": (0.35, 0.55),
        "vibration_range": (0.35, 0.70),
    },
    "overvoltage": {
        "voltage_range": (265, 300),
        "temperature_range": (35, 60),
        "power_factor_range": (0.78, 0.90),
    },
    "undervoltage": {
        "voltage_range": (155, 195),
        "current_range": (12, 20),
        "power_factor_range": (0.68, 0.82),
    },
    "overcurrent": {
        "current_range": (22, 45),
        "temperature_range": (60, 90),
        "power_factor_range": (0.62, 0.80),
        "vibration_range": (0.18, 0.45),
    },
    "loose_connection": {
        "voltage_range": (195, 255),  # fluctuating
        "current_range": (6, 22),     # unstable
        "temperature_range": (45, 75),
        "resistance_range": (40, 90),
        "power_factor_range": (0.58, 0.78),
        "vibration_range": (0.12, 0.40),
    },
    "critical_failure": {
        "voltage_range": (50, 140),
        "current_range": (50, 100),
        "temperature_range": (100, 155),
        "resistance_range": (0.1, 2.0),
        "power_factor_range": (0.25, 0.45),
        "vibration_range": (0.50, 0.90),
        "frequency_range": (47.5, 49.0),
    },
}

# Demo scenarios
DEMO_SCENARIOS = {
    "normal": {
        "name": "Normal Operation",
        "description": "All devices operating within normal parameters.",
        "devices": {},
    },
    "overheating": {
        "name": "Overheating Scenario",
        "description": "MOTOR-002 experiencing overheating due to overload.",
        "devices": {"MOTOR-002": "overheating"},
    },
    "overcurrent": {
        "name": "Overcurrent Scenario",
        "description": "PANEL-001 drawing excessive current.",
        "devices": {"PANEL-001": "overcurrent"},
    },
    "overvoltage": {
        "name": "Overvoltage Scenario",
        "description": "TRANSFORMER-003 output voltage is too high.",
        "devices": {"TRANSFORMER-003": "overvoltage"},
    },
    "loose_connection": {
        "name": "Loose Connection Scenario",
        "description": "MACHINE-004 has an intermittent loose connection.",
        "devices": {"MACHINE-004": "loose_connection"},
    },
    "short_circuit": {
        "name": "Short Circuit Scenario",
        "description": "PANEL-001 experiencing a developing short circuit.",
        "devices": {"PANEL-001": "short_circuit"},
    },
    "critical_failure": {
        "name": "Critical Failure Scenario",
        "description": "MOTOR-002 in critical failure condition.",
        "devices": {"MOTOR-002": "critical_failure"},
    },
    "multi_fault": {
        "name": "Multi-Device Fault Scenario",
        "description": "Multiple devices experiencing different faults simultaneously.",
        "devices": {
            "PANEL-001": "overcurrent",
            "MOTOR-002": "overheating",
            "TRANSFORMER-003": "overvoltage",
        },
    },
}


class SensorReading:
    """A single set of sensor readings from a device."""

    def __init__(self, device_id: str, voltage: float, current: float,
                 temperature: float, power: float, power_factor: float,
                 frequency: float, resistance: float, vibration: float):
        self.device_id = device_id
        self.timestamp = datetime.utcnow()
        self.voltage = round(voltage, 2)
        self.current = round(current, 2)
        self.temperature = round(temperature, 2)
        self.power = round(power, 2)
        self.power_factor = round(power_factor, 4)
        self.frequency = round(frequency, 2)
        self.resistance = round(resistance, 2)
        self.vibration = round(vibration, 4)

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "voltage": self.voltage,
            "current": self.current,
            "temperature": self.temperature,
            "power": self.power,
            "power_factor": self.power_factor,
            "frequency": self.frequency,
            "resistance": self.resistance,
            "vibration": self.vibration,
        }


class IoTSimulator:
    """
    Simulates realistic sensor data from multiple electrical devices.

    Features:
    - Realistic value generation with Gaussian noise and time-varying drift
    - Configurable fault injection per device
    - Demo scenario support
    - Async generator for WebSocket streaming
    """

    def __init__(self, devices: List[DeviceConfig] = None):
        self.devices = {d.device_id: d for d in (devices or DEFAULT_DEVICES)}
        self._fault_states: Dict[str, str] = {}  # device_id -> fault profile
        self._running = False
        self._callbacks: List[Callable] = []
        self._tick = 0
        self._interval = float(2)  # seconds between readings

    def set_fault(self, device_id: str, fault_profile: str):
        """Inject a fault profile into a device."""
        if device_id in self.devices and fault_profile in FAULT_PROFILES:
            self._fault_states[device_id] = fault_profile
            print(f"  [IoT] Fault injected: {device_id} → {fault_profile}")

    def clear_fault(self, device_id: str):
        """Clear fault from a device."""
        if device_id in self._fault_states:
            del self._fault_states[device_id]
            print(f"  [IoT] Fault cleared: {device_id}")

    def clear_all_faults(self):
        """Clear all fault injections."""
        self._fault_states.clear()

    def set_scenario(self, scenario_name: str) -> dict:
        """Apply a demo scenario."""
        scenario = DEMO_SCENARIOS.get(scenario_name)
        if not scenario:
            return {"error": f"Unknown scenario: {scenario_name}"}

        self.clear_all_faults()
        for device_id, fault_profile in scenario["devices"].items():
            self.set_fault(device_id, fault_profile)

        return {
            "name": scenario["name"],
            "description": scenario["description"],
            "active_faults": dict(self._fault_states),
        }

    def get_scenarios(self) -> List[dict]:
        """Get all available demo scenarios."""
        return [
            {
                "id": key,
                "name": sc["name"],
                "description": sc["description"],
                "affected_devices": list(sc["devices"].keys()),
            }
            for key, sc in DEMO_SCENARIOS.items()
        ]

    def generate_reading(self, device_id: str) -> SensorReading:
        """Generate a single sensor reading for a device."""
        config = self.devices.get(device_id)
        if not config:
            raise ValueError(f"Unknown device: {device_id}")

        # Get fault profile if active
        fault_name = self._fault_states.get(device_id, "normal")
        fault = FAULT_PROFILES.get(fault_name, {})

        # Time-varying component for realistic fluctuation
        t = self._tick * 0.1
        time_drift = math.sin(t) * 0.02  # subtle periodic drift

        def gen(normal_range: tuple, fault_key: str) -> float:
            """Generate a value from the appropriate range with noise."""
            rng = fault.get(fault_key, normal_range)
            base = random.uniform(rng[0], rng[1])
            noise = random.gauss(0, (rng[1] - rng[0]) * 0.05)
            drift = base * time_drift
            return base + noise + drift

        voltage = gen(config.voltage_range, "voltage_range")
        current = gen(config.current_range, "current_range")
        temperature = gen(config.temperature_range, "temperature_range")
        power_factor = gen(config.power_factor_range, "power_factor_range")
        frequency = gen(config.frequency_range, "frequency_range")
        resistance = gen(config.resistance_range, "resistance_range")
        vibration = gen(config.vibration_range, "vibration_range")

        # Derived: power = voltage * current * power_factor
        power = abs(voltage * current * power_factor)

        # Clamp to physically possible values
        voltage = max(0, voltage)
        current = max(0, current)
        temperature = max(-10, temperature)
        power = max(0, power)
        power_factor = max(0, min(1.0, power_factor))
        frequency = max(45, min(55, frequency))
        resistance = max(0.01, resistance)
        vibration = max(0, vibration)

        return SensorReading(
            device_id=device_id,
            voltage=voltage,
            current=current,
            temperature=temperature,
            power=power,
            power_factor=power_factor,
            frequency=frequency,
            resistance=resistance,
            vibration=vibration,
        )

    def generate_all_readings(self) -> List[SensorReading]:
        """Generate readings for all devices."""
        self._tick += 1
        return [self.generate_reading(did) for did in self.devices]

    async def stream(self, interval: float = None):
        """
        Async generator that continuously yields sensor readings.
        Use with WebSocket or SSE endpoints.
        """
        self._running = True
        interval = interval or self._interval

        while self._running:
            readings = self.generate_all_readings()
            yield readings
            await asyncio.sleep(interval)

    def stop(self):
        """Stop the streaming loop."""
        self._running = False

    def get_device_info(self) -> List[dict]:
        """Get info about all simulated devices."""
        devices = []
        for did, config in self.devices.items():
            fault = self._fault_states.get(did, "normal")
            status = "online"
            if fault == "critical_failure":
                status = "critical"
            elif fault != "normal":
                status = "warning"

            devices.append({
                "device_id": did,
                "name": config.name,
                "device_type": config.device_type,
                "location": config.location,
                "status": status,
                "fault_profile": fault,
            })
        return devices

    def get_device_status(self, device_id: str) -> Optional[dict]:
        """Get status for a single device."""
        config = self.devices.get(device_id)
        if not config:
            return None

        fault = self._fault_states.get(device_id, "normal")
        reading = self.generate_reading(device_id)

        return {
            "device_id": device_id,
            "name": config.name,
            "device_type": config.device_type,
            "location": config.location,
            "status": "critical" if fault == "critical_failure" else (
                "warning" if fault != "normal" else "online"
            ),
            "fault_profile": fault,
            "latest_reading": reading.to_dict(),
        }
