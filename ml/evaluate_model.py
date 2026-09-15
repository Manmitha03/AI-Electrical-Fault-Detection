"""
Model Evaluation Script for Electrical Fault Detection
========================================================
Loads the trained model and evaluates on the held-out test set.
Generates a comprehensive evaluation report.

Usage:
    python evaluate_model.py [--model-dir PATH] [--dataset PATH]
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ml.generate_dataset import FAULT_TYPES

FEATURE_COLUMNS = [
    "voltage", "current", "temperature", "power",
    "power_factor", "frequency", "resistance", "vibration",
]


def load_model(model_dir: str):
    """Load the trained model, scaler, and label encoder."""
    model = joblib.load(os.path.join(model_dir, "fault_classifier.joblib"))
    scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
    label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.joblib"))

    with open(os.path.join(model_dir, "model_metadata.json"), "r") as f:
        metadata = json.load(f)

    return model, scaler, label_encoder, metadata


def evaluate(model, scaler, label_encoder, dataset_path: str):
    """Run full evaluation and return results."""
    # Load dataset
    df = pd.read_csv(dataset_path, comment="#")
    X = df[FEATURE_COLUMNS].values
    y = df["fault_type"].values

    # Use same split as training to get the test set
    y_encoded = label_encoder.transform(y)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y_encoded, test_size=0.15, random_state=42, stratify=y_encoded
    )

    # Scale
    X_test_scaled = scaler.transform(X_test)

    # Predict
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)

    # Metrics
    target_names = [FAULT_TYPES[c] for c in label_encoder.classes_]
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    # Per-class metrics
    per_class = {}
    for i, name in enumerate(target_names):
        if name in report:
            per_class[name] = {
                "precision": round(report[name]["precision"], 4),
                "recall": round(report[name]["recall"], 4),
                "f1_score": round(report[name]["f1-score"], 4),
                "support": int(report[name]["support"]),
            }

    # Overall metrics
    overall = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_weighted": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
    }

    # AUC-ROC (one-vs-rest)
    try:
        n_classes = len(label_encoder.classes_)
        y_test_bin = label_binarize(y_test, classes=range(n_classes))
        auc = roc_auc_score(y_test_bin, y_proba, average="weighted", multi_class="ovr")
        overall["auc_roc_weighted"] = float(auc)
    except Exception:
        overall["auc_roc_weighted"] = None

    return {
        "overall_metrics": overall,
        "per_class_metrics": per_class,
        "confusion_matrix": cm.tolist(),
        "test_samples": int(len(X_test)),
        "classification_report_text": classification_report(y_test, y_pred, target_names=target_names),
    }


def print_evaluation(results: dict):
    """Pretty-print evaluation results."""
    print("=" * 60)
    print("  MODEL EVALUATION REPORT")
    print("=" * 60)

    overall = results["overall_metrics"]
    print(f"\n  Test Samples: {results['test_samples']}")
    print(f"\n  Overall Metrics:")
    print(f"    Accuracy:          {overall['accuracy']:.4f}")
    print(f"    Precision (wt):    {overall['precision_weighted']:.4f}")
    print(f"    Recall (wt):       {overall['recall_weighted']:.4f}")
    print(f"    F1-Score (wt):     {overall['f1_weighted']:.4f}")
    print(f"    F1-Score (macro):  {overall['f1_macro']:.4f}")
    if overall.get("auc_roc_weighted"):
        print(f"    AUC-ROC (wt):      {overall['auc_roc_weighted']:.4f}")

    print(f"\n  Per-Class Metrics:")
    print(f"  {'Class':<22s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'Support':>10s}")
    print("  " + "-" * 62)
    for name, metrics in results["per_class_metrics"].items():
        print(f"  {name:<22s} {metrics['precision']:>10.4f} {metrics['recall']:>10.4f} "
              f"{metrics['f1_score']:>10.4f} {metrics['support']:>10d}")

    print(f"\n  Classification Report:")
    print(results["classification_report_text"])

    print(f"  Confusion Matrix:")
    cm = np.array(results["confusion_matrix"])
    print(f"  {cm}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Evaluate fault detection model")
    parser.add_argument("--model-dir", type=str, default=None,
                        help="Directory containing trained model")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset CSV")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(__file__))
    model_dir = args.model_dir or os.path.join(os.path.dirname(__file__), "models")
    dataset_path = args.dataset or os.path.join(project_root, "data", "synthetic_fault_dataset.csv")

    # Load model
    print(f"\n  Loading model from {model_dir}...")
    model, scaler, label_encoder, metadata = load_model(model_dir)
    print(f"  Model type: {metadata['model_type']}")
    print(f"  Model name: {metadata['model_name']}")

    # Evaluate
    print(f"\n  Evaluating on {dataset_path}...")
    results = evaluate(model, scaler, label_encoder, dataset_path)
    results["model_metadata"] = metadata

    # Print
    print_evaluation(results)

    # Save report
    report_path = os.path.join(model_dir, "evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Evaluation report saved: {report_path}\n")


if __name__ == "__main__":
    main()
