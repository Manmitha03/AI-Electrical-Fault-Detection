"""
Model Training Pipeline for Electrical Fault Detection
========================================================
Trains Random Forest and Gradient Boosting classifiers on the synthetic
sensor dataset. Selects the best model via cross-validation, saves the
trained model, scaler, and label encoder for inference.

Usage:
    python train_model.py [--dataset PATH] [--output-dir PATH]
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ml.generate_dataset import FAULT_TYPES

FEATURE_COLUMNS = [
    "voltage", "current", "temperature", "power",
    "power_factor", "frequency", "resistance", "vibration",
]


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """Load dataset, skipping comment lines."""
    df = pd.read_csv(dataset_path, comment="#")
    print(f"  Loaded {len(df)} samples from {dataset_path}")
    return df


def prepare_data(df: pd.DataFrame):
    """
    Split features and target, encode labels, scale features.

    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder
    """
    X = df[FEATURE_COLUMNS].values
    y = df["fault_type"].values

    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Split: 70% train, 15% validation, 15% test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y_encoded, test_size=0.15, random_state=42, stratify=y_encoded
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.176,  # 0.176 of 0.85 ≈ 0.15 of total
        random_state=42, stratify=y_train_val
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    print(f"  Train: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")

    return X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder


def train_random_forest(X_train, y_train):
    """Train a Random Forest classifier."""
    print("\n  Training Random Forest (n_estimators=200)...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    start = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"  Random Forest trained in {elapsed:.2f}s")
    return model


def train_gradient_boosting(X_train, y_train):
    """Train a Gradient Boosting classifier."""
    print("\n  Training Gradient Boosting (n_estimators=150)...")
    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42,
    )
    start = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"  Gradient Boosting trained in {elapsed:.2f}s")
    return model


def evaluate_model(model, X_val, y_val, model_name: str, label_encoder):
    """Evaluate a model on validation set and return metrics."""
    y_pred = model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    prec = precision_score(y_val, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_val, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_val, y_pred, average="weighted", zero_division=0)

    print(f"\n  {model_name} — Validation Results:")
    print(f"    Accuracy:  {acc:.4f}")
    print(f"    Precision: {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1-Score:  {f1:.4f}")

    return {
        "model_name": model_name,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
    }


def cross_validate(model, X_train, y_train, model_name: str):
    """Perform stratified k-fold cross-validation."""
    print(f"\n  Cross-validating {model_name} (5-fold)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1_weighted", n_jobs=-1)
    print(f"    CV F1 Scores: {[f'{s:.4f}' for s in scores]}")
    print(f"    CV Mean F1:   {scores.mean():.4f} (±{scores.std():.4f})")
    return float(scores.mean())


def get_feature_importance(model, feature_names: list) -> dict:
    """Extract and return feature importance."""
    importances = model.feature_importances_
    importance_dict = {}
    sorted_idx = np.argsort(importances)[::-1]

    print("\n  Feature Importance:")
    print("  " + "-" * 40)
    for idx in sorted_idx:
        name = feature_names[idx]
        imp = importances[idx]
        importance_dict[name] = float(imp)
        bar = "█" * int(imp * 50)
        print(f"    {name:<15s} {imp:.4f}  {bar}")

    return importance_dict


def save_model(model, scaler, label_encoder, metrics, feature_importance,
               output_dir: str, model_name: str):
    """Save the trained model, scaler, encoder, and metadata."""
    os.makedirs(output_dir, exist_ok=True)

    # Save model
    model_path = os.path.join(output_dir, "fault_classifier.joblib")
    joblib.dump(model, model_path)
    print(f"\n  Model saved: {model_path}")

    # Save scaler
    scaler_path = os.path.join(output_dir, "scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"  Scaler saved: {scaler_path}")

    # Save label encoder
    encoder_path = os.path.join(output_dir, "label_encoder.joblib")
    joblib.dump(label_encoder, encoder_path)
    print(f"  Encoder saved: {encoder_path}")

    # Save metadata
    metadata = {
        "model_name": model_name,
        "model_type": type(model).__name__,
        "features": FEATURE_COLUMNS,
        "fault_types": {str(k): v for k, v in FAULT_TYPES.items()},
        "metrics": metrics,
        "feature_importance": feature_importance,
        "training_date": datetime.now().isoformat(),
        "scikit_learn_version": __import__("sklearn").__version__,
        "note": "SYNTHETIC DATA - This model was trained on artificially generated data for prototype purposes.",
    }
    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(description="Train fault detection ML model")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to training dataset CSV")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save trained model")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(__file__))

    dataset_path = args.dataset or os.path.join(project_root, "data", "synthetic_fault_dataset.csv")
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), "models")

    print("=" * 60)
    print("  ELECTRICAL FAULT DETECTION — MODEL TRAINING")
    print("=" * 60)

    # Check if dataset exists, if not generate it
    if not os.path.exists(dataset_path):
        print(f"\n  Dataset not found at {dataset_path}")
        print("  Generating synthetic dataset first...")
        from ml.generate_dataset import generate_dataset, save_dataset
        dataset = generate_dataset(total_samples=15000)
        dataset_path = save_dataset(dataset, os.path.dirname(dataset_path))
        print(f"  Dataset generated: {dataset_path}")

    # Load and prepare data
    print("\n  Loading dataset...")
    df = load_dataset(dataset_path)

    print("\n  Preparing data (split + scale)...")
    X_train, X_val, X_test, y_train, y_val, y_test, scaler, label_encoder = prepare_data(df)

    # Train both models
    rf_model = train_random_forest(X_train, y_train)
    gb_model = train_gradient_boosting(X_train, y_train)

    # Evaluate on validation set
    rf_metrics = evaluate_model(rf_model, X_val, y_val, "Random Forest", label_encoder)
    gb_metrics = evaluate_model(gb_model, X_val, y_val, "Gradient Boosting", label_encoder)

    # Cross-validation
    rf_cv = cross_validate(rf_model, X_train, y_train, "Random Forest")
    gb_cv = cross_validate(gb_model, X_train, y_train, "Gradient Boosting")

    # Select best model
    print("\n" + "=" * 60)
    print("  MODEL SELECTION")
    print("=" * 60)

    rf_score = rf_metrics["f1_score"] * 0.5 + rf_cv * 0.5
    gb_score = gb_metrics["f1_score"] * 0.5 + gb_cv * 0.5

    print(f"  Random Forest combined score:     {rf_score:.4f}")
    print(f"  Gradient Boosting combined score:  {gb_score:.4f}")

    if rf_score >= gb_score:
        best_model = rf_model
        best_metrics = rf_metrics
        best_name = "Random Forest"
    else:
        best_model = gb_model
        best_metrics = gb_metrics
        best_name = "Gradient Boosting"

    print(f"\n  ✓ Selected: {best_name}")

    # Feature importance
    feature_importance = get_feature_importance(best_model, FEATURE_COLUMNS)

    # Final evaluation on test set
    print("\n" + "=" * 60)
    print("  FINAL TEST SET EVALUATION")
    print("=" * 60)

    y_test_pred = best_model.predict(X_test)
    target_names = [FAULT_TYPES[le_class] for le_class in label_encoder.classes_]

    print("\n  Classification Report:")
    print(classification_report(y_test, y_test_pred, target_names=target_names))

    print("  Confusion Matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"  {cm}")

    # Final test metrics
    test_metrics = {
        "accuracy": float(accuracy_score(y_test, y_test_pred)),
        "precision": float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)),
    }
    best_metrics["test_metrics"] = test_metrics
    best_metrics["confusion_matrix"] = cm.tolist()

    # Save best model
    save_model(best_model, scaler, label_encoder, best_metrics, feature_importance,
               output_dir, best_name)

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print(f"  Model: {best_name}")
    print(f"  Test Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"  Test F1-Score: {test_metrics['f1_score']:.4f}")
    print(f"  Saved to: {output_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
