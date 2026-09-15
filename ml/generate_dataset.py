"""
Synthetic Dataset Generator for Electrical Fault Detection
===========================================================
Generates realistic synthetic sensor data for training fault classification models.

IMPORTANT: This dataset is SYNTHETIC (artificially generated) for prototype/demo purposes.
It does NOT represent real industrial measurements. Real deployment would require
validated sensor data from actual electrical systems.

Fault Categories:
    0: Normal
    1: Overheating
    2: Short Circuit
    3: Overvoltage
    4: Undervoltage
    5: Overcurrent
    6: Loose Connection
    7: Burnt Component
    8: Insulation Damage
    9: Corrosion

Features:
    voltage (V), current (A), temperature (°C), power (W),
    power_factor, frequency (Hz), resistance (Ω), vibration (g)
"""

import numpy as np
import pandas as pd
import os
import sys

# Fault type mapping
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

# Normal operating ranges (baseline)
NORMAL_RANGES = {
    "voltage": (220, 240),       # Volts
    "current": (5, 15),          # Amps
    "temperature": (20, 45),     # Celsius
    "power": (1100, 3600),       # Watts
    "power_factor": (0.85, 0.99),
    "frequency": (49.5, 50.5),   # Hz
    "resistance": (10, 50),      # Ohms
    "vibration": (0.01, 0.15),   # g (acceleration)
}


def add_noise(values: np.ndarray, noise_pct: float = 0.05) -> np.ndarray:
    """Add Gaussian noise to prevent perfect separability."""
    noise = np.random.normal(0, noise_pct * np.std(values), size=values.shape)
    return values + noise


def generate_normal(n: int) -> dict:
    """Generate normal operating condition samples."""
    return {
        "voltage": np.random.uniform(220, 240, n),
        "current": np.random.uniform(5, 15, n),
        "temperature": np.random.uniform(20, 45, n),
        "power": np.random.uniform(1100, 3600, n),
        "power_factor": np.random.uniform(0.85, 0.99, n),
        "frequency": np.random.uniform(49.5, 50.5, n),
        "resistance": np.random.uniform(10, 50, n),
        "vibration": np.random.uniform(0.01, 0.15, n),
    }


def generate_overheating(n: int) -> dict:
    """Overheating: significantly elevated temperature, elevated current, reduced power factor."""
    return {
        "voltage": np.random.uniform(215, 240, n),
        "current": np.random.uniform(12, 25, n),          # elevated
        "temperature": np.random.uniform(70, 120, n),      # significantly elevated
        "power": np.random.uniform(2600, 6000, n),         # elevated
        "power_factor": np.random.uniform(0.60, 0.85, n),  # reduced
        "frequency": np.random.uniform(49.0, 50.5, n),
        "resistance": np.random.uniform(15, 60, n),        # slight increase
        "vibration": np.random.uniform(0.10, 0.40, n),     # elevated
    }


def generate_short_circuit(n: int) -> dict:
    """Short Circuit: very high current, voltage drop, temperature spike, very low resistance."""
    return {
        "voltage": np.random.uniform(50, 180, n),          # significant drop
        "current": np.random.uniform(30, 100, n),          # very high
        "temperature": np.random.uniform(80, 150, n),      # spike
        "power": np.random.uniform(1500, 18000, n),        # anomalous
        "power_factor": np.random.uniform(0.30, 0.65, n),  # poor
        "frequency": np.random.uniform(48.0, 50.5, n),     # may fluctuate
        "resistance": np.random.uniform(0.1, 5, n),        # very low
        "vibration": np.random.uniform(0.30, 0.80, n),     # high
    }


def generate_overvoltage(n: int) -> dict:
    """Overvoltage: voltage significantly above normal range."""
    return {
        "voltage": np.random.uniform(260, 320, n),         # significantly elevated
        "current": np.random.uniform(5, 18, n),            # slightly elevated
        "temperature": np.random.uniform(30, 65, n),       # moderate increase
        "power": np.random.uniform(1300, 5760, n),         # elevated
        "power_factor": np.random.uniform(0.75, 0.95, n),
        "frequency": np.random.uniform(49.0, 51.0, n),     # slight fluctuation
        "resistance": np.random.uniform(10, 50, n),
        "vibration": np.random.uniform(0.05, 0.25, n),
    }


def generate_undervoltage(n: int) -> dict:
    """Undervoltage: voltage significantly below expected range."""
    return {
        "voltage": np.random.uniform(140, 200, n),         # significantly low
        "current": np.random.uniform(8, 22, n),            # may increase to compensate
        "temperature": np.random.uniform(25, 55, n),       # moderate
        "power": np.random.uniform(1120, 4400, n),
        "power_factor": np.random.uniform(0.65, 0.88, n),  # reduced
        "frequency": np.random.uniform(48.5, 50.5, n),
        "resistance": np.random.uniform(10, 55, n),
        "vibration": np.random.uniform(0.05, 0.20, n),
    }


def generate_overcurrent(n: int) -> dict:
    """Overcurrent: current significantly above normal, elevated temperature."""
    return {
        "voltage": np.random.uniform(210, 240, n),         # near normal
        "current": np.random.uniform(20, 50, n),           # significantly elevated
        "temperature": np.random.uniform(55, 95, n),       # elevated
        "power": np.random.uniform(4200, 12000, n),        # elevated
        "power_factor": np.random.uniform(0.60, 0.85, n),  # reduced
        "frequency": np.random.uniform(49.0, 50.5, n),
        "resistance": np.random.uniform(5, 30, n),         # may decrease
        "vibration": np.random.uniform(0.15, 0.50, n),     # elevated
    }


def generate_loose_connection(n: int) -> dict:
    """Loose Connection: voltage fluctuations, current instability, temperature increase."""
    # Simulate fluctuations with higher variance
    voltage_base = np.random.uniform(190, 250, n)
    voltage_fluctuation = np.random.normal(0, 15, n)  # high variance
    current_base = np.random.uniform(5, 20, n)
    current_fluctuation = np.random.normal(0, 3, n)   # instability

    return {
        "voltage": voltage_base + voltage_fluctuation,
        "current": current_base + current_fluctuation,
        "temperature": np.random.uniform(40, 80, n),       # elevated
        "power": np.random.uniform(950, 5000, n),
        "power_factor": np.random.uniform(0.55, 0.82, n),  # poor
        "frequency": np.random.uniform(48.5, 51.0, n),     # fluctuates
        "resistance": np.random.uniform(30, 100, n),       # elevated/variable
        "vibration": np.random.uniform(0.10, 0.45, n),     # elevated
    }


def generate_burnt_component(n: int) -> dict:
    """Burnt Component: very high temperature, high resistance, poor power factor."""
    return {
        "voltage": np.random.uniform(180, 235, n),         # may drop
        "current": np.random.uniform(3, 12, n),            # may reduce due to high resistance
        "temperature": np.random.uniform(90, 160, n),      # very high
        "power": np.random.uniform(540, 2820, n),          # reduced
        "power_factor": np.random.uniform(0.35, 0.65, n),  # very poor
        "frequency": np.random.uniform(49.0, 50.5, n),
        "resistance": np.random.uniform(80, 500, n),       # very high
        "vibration": np.random.uniform(0.05, 0.30, n),
    }


def generate_insulation_damage(n: int) -> dict:
    """Insulation Damage: leakage current, reduced resistance, moderate temperature increase."""
    return {
        "voltage": np.random.uniform(200, 240, n),
        "current": np.random.uniform(10, 25, n),           # leakage current
        "temperature": np.random.uniform(35, 70, n),       # moderate increase
        "power": np.random.uniform(2000, 6000, n),
        "power_factor": np.random.uniform(0.55, 0.80, n),  # reduced
        "frequency": np.random.uniform(49.0, 50.5, n),
        "resistance": np.random.uniform(2, 15, n),         # significantly reduced
        "vibration": np.random.uniform(0.05, 0.25, n),
    }


def generate_corrosion(n: int) -> dict:
    """Corrosion: increased resistance, temperature increase, poor power factor, vibration increase."""
    return {
        "voltage": np.random.uniform(200, 240, n),
        "current": np.random.uniform(5, 14, n),            # may reduce
        "temperature": np.random.uniform(35, 65, n),       # moderate increase
        "power": np.random.uniform(1000, 3360, n),
        "power_factor": np.random.uniform(0.60, 0.82, n),  # reduced
        "frequency": np.random.uniform(49.0, 50.5, n),
        "resistance": np.random.uniform(50, 200, n),       # elevated
        "vibration": np.random.uniform(0.10, 0.35, n),     # elevated
    }


# Map fault codes to generator functions
FAULT_GENERATORS = {
    0: generate_normal,
    1: generate_overheating,
    2: generate_short_circuit,
    3: generate_overvoltage,
    4: generate_undervoltage,
    5: generate_overcurrent,
    6: generate_loose_connection,
    7: generate_burnt_component,
    8: generate_insulation_damage,
    9: generate_corrosion,
}


def generate_dataset(
    total_samples: int = 15000,
    noise_level: float = 0.08,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a complete synthetic fault detection dataset.

    Args:
        total_samples: Total number of samples to generate.
        noise_level: Gaussian noise level (fraction of std dev) to add.
        random_seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame with features and fault_type/fault_label columns.
    """
    np.random.seed(random_seed)

    # Distribute samples across fault types (slightly more normal samples)
    n_classes = len(FAULT_TYPES)
    normal_samples = int(total_samples * 0.15)  # 15% normal
    fault_samples_each = (total_samples - normal_samples) // (n_classes - 1)
    remainder = total_samples - normal_samples - fault_samples_each * (n_classes - 1)

    samples_per_class = {0: normal_samples + remainder}
    for i in range(1, n_classes):
        samples_per_class[i] = fault_samples_each

    all_data = []

    for fault_code, n_samples in samples_per_class.items():
        generator = FAULT_GENERATORS[fault_code]
        data = generator(n_samples)

        # Add controlled noise to all features
        for feature_name in data:
            data[feature_name] = add_noise(data[feature_name], noise_level)

        # Clip physically impossible values
        data["voltage"] = np.clip(data["voltage"], 0, 500)
        data["current"] = np.clip(data["current"], 0, 200)
        data["temperature"] = np.clip(data["temperature"], -10, 200)
        data["power"] = np.clip(data["power"], 0, 100000)
        data["power_factor"] = np.clip(data["power_factor"], 0, 1.0)
        data["frequency"] = np.clip(data["frequency"], 45, 55)
        data["resistance"] = np.clip(data["resistance"], 0.01, 1000)
        data["vibration"] = np.clip(data["vibration"], 0, 2.0)

        df = pd.DataFrame(data)
        df["fault_type"] = fault_code
        df["fault_label"] = FAULT_TYPES[fault_code]

        all_data.append(df)

    # Combine and shuffle
    dataset = pd.concat(all_data, ignore_index=True)
    dataset = dataset.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    return dataset


def save_dataset(dataset: pd.DataFrame, output_dir: str = None) -> str:
    """Save dataset to CSV with metadata header."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "synthetic_fault_dataset.csv")

    # Save with comment about synthetic nature
    with open(filepath, "w") as f:
        f.write("# SYNTHETIC DATASET - Generated for AI Electric Fault Detection Prototype\n")
        f.write("# This data is artificially generated and does NOT represent real industrial measurements.\n")
        f.write("# For production use, replace with validated sensor data from actual electrical systems.\n")
        f.write(f"# Total samples: {len(dataset)}\n")
        f.write(f"# Fault classes: {len(dataset['fault_type'].unique())}\n")
        f.write("#\n")

    dataset.to_csv(filepath, mode="a", index=False)

    return filepath


def print_dataset_summary(dataset: pd.DataFrame):
    """Print a summary of the generated dataset."""
    print("=" * 60)
    print("  SYNTHETIC FAULT DETECTION DATASET SUMMARY")
    print("=" * 60)
    print(f"\n  Total Samples: {len(dataset)}")
    print(f"  Features: {[c for c in dataset.columns if c not in ['fault_type', 'fault_label']]}")
    print(f"  Fault Classes: {len(dataset['fault_type'].unique())}")

    print("\n  Class Distribution:")
    print("  " + "-" * 40)
    for fault_code in sorted(dataset["fault_type"].unique()):
        count = len(dataset[dataset["fault_type"] == fault_code])
        label = FAULT_TYPES[fault_code]
        pct = count / len(dataset) * 100
        print(f"  {fault_code}: {label:<22s} {count:>5d} ({pct:.1f}%)")

    print("\n  Feature Statistics:")
    print("  " + "-" * 40)
    features = [c for c in dataset.columns if c not in ["fault_type", "fault_label"]]
    for feat in features:
        print(f"  {feat:<15s}  min={dataset[feat].min():.2f}  max={dataset[feat].max():.2f}  "
              f"mean={dataset[feat].mean():.2f}  std={dataset[feat].std():.2f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Parse optional arguments
    total_samples = 15000
    if len(sys.argv) > 1:
        try:
            total_samples = int(sys.argv[1])
        except ValueError:
            print(f"Usage: python generate_dataset.py [total_samples]")
            sys.exit(1)

    print(f"\nGenerating {total_samples} synthetic fault detection samples...\n")

    dataset = generate_dataset(total_samples=total_samples)
    filepath = save_dataset(dataset)
    print_dataset_summary(dataset)

    print(f"\n  Dataset saved to: {filepath}")
    print(f"  Ready for model training.\n")
