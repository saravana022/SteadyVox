"""SteadyVox Tabular MLP Training Script for Oxford Parkinson's Dataset.

Trains a deep neural network on 22 acoustic features from sustained phonations
(Little et al., 2007, UCI Machine Learning Repository).
Computes optimal decision threshold using Youden's J on the validation set.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
    roc_curve,
)
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn

from ml.models.tabular_mlp import FEATURE_NAMES, TabularMLP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("steadyvox.train_tabular")


def train_tabular_model(
    data_dir: str = "ml/data/real",
    saved_models_dir: str = "ml/saved_models",
    reports_dir: str = "ml/reports",
    epochs: int = 60,
    lr: float = 0.002,
    weight_decay: float = 1e-3,
    seed: int = 42,
) -> Dict[str, Any]:
    """Trains and evaluates TabularMLP on the Oxford Parkinson's Dataset."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data_path = Path(data_dir)
    train_csv = data_path / "train.csv"
    val_csv = data_path / "val.csv"
    test_csv = data_path / "test.csv"

    if not (train_csv.exists() and val_csv.exists() and test_csv.exists()):
        raise FileNotFoundError(f"Missing split CSVs in {data_dir}. Run download_dataset.py first.")

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)

    X_train_raw = train_df[FEATURE_NAMES].values.astype(np.float32)
    y_train = train_df["status"].values.astype(np.float32)

    X_val_raw = val_df[FEATURE_NAMES].values.astype(np.float32)
    y_val = val_df["status"].values.astype(np.float32)

    X_test_raw = test_df[FEATURE_NAMES].values.astype(np.float32)
    y_test = test_df["status"].values.astype(np.float32)

    # Standardize features (fit ONLY on train)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_val = scaler.transform(X_val_raw)
    X_test = scaler.transform(X_test_raw)

    # Save scaler
    models_path = Path(saved_models_dir)
    models_path.mkdir(parents=True, exist_ok=True)
    scaler_path = models_path / "tabular_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    logger.info("Saved feature scaler to %s", scaler_path)

    # Convert to Tensors
    X_train_t = torch.from_numpy(X_train).float().to(device)
    y_train_t = torch.from_numpy(y_train).float().unsqueeze(1).to(device)
    X_val_t = torch.from_numpy(X_val).float().to(device)
    y_val_t = torch.from_numpy(y_val).float().unsqueeze(1).to(device)
    X_test_t = torch.from_numpy(X_test).float().to(device)
    y_test_t = torch.from_numpy(y_test).float().unsqueeze(1).to(device)

    model = TabularMLP(in_features=len(FEATURE_NAMES), hidden_dim1=64, hidden_dim2=32, dropout_rate=0.20)
    model.to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    best_val_loss = float("inf")
    best_state = None
    best_epoch = 0
    history = {"train_loss": [], "val_loss": [], "val_auc": []}
    best_model_path = models_path / "tabular_mlp_best.pt"

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        logits = model(X_train_t)
        loss = criterion(logits, y_train_t)
        loss.backward()
        optimizer.step()
        train_loss = loss.item()

        # Validation
        model.eval()
        with torch.no_grad():
            val_logits = model(X_val_t)
            val_loss = criterion(val_logits, y_val_t).item()
            val_probs = torch.sigmoid(val_logits).cpu().numpy().flatten()

        try:
            val_auc = roc_auc_score(y_val, val_probs)
        except ValueError:
            val_auc = 0.5

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_auc"].append(val_auc)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_auc = val_auc
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    logger.info("Training complete. Best Epoch: %d | Best Val Loss: %.4f | Val AUC: %.4f", best_epoch, best_val_loss, best_val_auc)

    # Restore best checkpoint
    model.load_state_dict(best_state)
    model.eval()

    # Compute optimal decision threshold via Youden's J statistic on validation set
    with torch.no_grad():
        val_probs = torch.sigmoid(model(X_val_t)).cpu().numpy().flatten()
    
    fpr_v, tpr_v, thresholds_v = roc_curve(y_val, val_probs)
    j_scores = tpr_v - fpr_v
    opt_idx = np.argmax(j_scores)
    calibrated_threshold = float(thresholds_v[opt_idx])
    calibrated_threshold = float(np.clip(calibrated_threshold, 0.40, 0.96))
    logger.info("Calibrated decision threshold (Youden's J on val): %.4f", calibrated_threshold)

    # Update model threshold and save final checkpoint
    model.calibrated_threshold = calibrated_threshold
    torch.save(
        {
            "epoch": best_epoch,
            "model_state_dict": model.state_dict(),
            "val_loss": best_val_loss,
            "val_auc": best_val_auc,
            "calibrated_threshold": calibrated_threshold,
            "feature_names": FEATURE_NAMES,
        },
        best_model_path,
    )
    logger.info("Saved best model to %s", best_model_path)

    # Evaluate on Test Set
    with torch.no_grad():
        test_logits = model(X_test_t)
        test_probs = torch.sigmoid(test_logits).cpu().numpy().flatten()

    test_preds_calibrated = (test_probs >= calibrated_threshold).astype(int)
    test_preds_default = (test_probs >= 0.50).astype(int)

    test_auc = roc_auc_score(y_test, test_probs)
    test_pr_auc = average_precision_score(y_test, test_probs)
    test_acc_cal = accuracy_score(y_test, test_preds_calibrated)
    test_bal_acc_cal = balanced_accuracy_score(y_test, test_preds_calibrated)
    test_f1_cal = f1_score(y_test, test_preds_calibrated, zero_division=0)
    test_prec_cal = precision_score(y_test, test_preds_calibrated, zero_division=0)
    test_rec_cal = recall_score(y_test, test_preds_calibrated, zero_division=0)
    cm_cal = confusion_matrix(y_test, test_preds_calibrated).tolist()

    test_acc_def = accuracy_score(y_test, test_preds_default)
    test_bal_acc_def = balanced_accuracy_score(y_test, test_preds_default)
    test_f1_def = f1_score(y_test, test_preds_default, zero_division=0)
    cm_def = confusion_matrix(y_test, test_preds_default).tolist()

    test_metrics = {
        "model_name": "tabular_mlp_best",
        "dataset": "Oxford Parkinson's Disease Detection Dataset (UCI ML Repository, Little et al., 2007)",
        "provenance": "real_dataset",
        "test_samples": len(y_test),
        "calibrated_threshold": round(float(calibrated_threshold), 4),
        "test_roc_auc": round(float(test_auc), 4),
        "test_pr_auc": round(float(test_pr_auc), 4),
        "calibrated": {
            "accuracy": round(float(test_acc_cal), 4),
            "balanced_accuracy": round(float(test_bal_acc_cal), 4),
            "precision": round(float(test_prec_cal), 4),
            "recall": round(float(test_rec_cal), 4),
            "f1_score": round(float(test_f1_cal), 4),
            "confusion_matrix": cm_cal,
        },
        "default_threshold_0_5": {
            "accuracy": round(float(test_acc_def), 4),
            "balanced_accuracy": round(float(test_bal_acc_def), 4),
            "f1_score": round(float(test_f1_def), 4),
            "confusion_matrix": cm_def,
        },
        "test_accuracy": round(float(test_acc_cal), 4),
        "test_balanced_accuracy": round(float(test_bal_acc_cal), 4),
        "test_precision": round(float(test_prec_cal), 4),
        "test_recall": round(float(test_rec_cal), 4),
        "test_f1": round(float(test_f1_cal), 4),
        "confusion_matrix": cm_cal,
        "best_val_loss": round(float(best_val_loss), 4),
        "best_val_auc": round(float(best_val_auc), 4),
        "best_epoch": best_epoch,
    }

    logger.info("=== Real Oxford Tabular MLP Test Results ===")
    logger.info("  ROC-AUC:               %.4f", test_auc)
    logger.info("  PR-AUC:                %.4f", test_pr_auc)
    logger.info("  Calibrated Threshold:  %.4f", calibrated_threshold)
    logger.info("  Calibrated Accuracy:   %.4f", test_acc_cal)
    logger.info("  Balanced Accuracy:     %.4f", test_bal_acc_cal)
    logger.info("  Precision:             %.4f", test_prec_cal)
    logger.info("  Recall:                %.4f", test_rec_cal)
    logger.info("  F1-Score:              %.4f", test_f1_cal)
    logger.info("  Confusion Matrix:      %s", cm_cal)

    # Save metrics JSON
    rep_path = Path(reports_dir)
    rep_path.mkdir(parents=True, exist_ok=True)
    plots_path = rep_path / "plots"
    plots_path.mkdir(parents=True, exist_ok=True)

    metrics_file = rep_path / "tabular_mlp_best_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(test_metrics, f, indent=2)

    # Plot 1: Training curves
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history["train_loss"], label="Train Loss", color="#2563eb")
    plt.plot(history["val_loss"], label="Val Loss", color="#dc2626")
    plt.axvline(best_epoch - 1, color="gray", linestyle="--", label=f"Best Ep {best_epoch}")
    plt.title("Tabular MLP Loss Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history["val_auc"], label="Val ROC-AUC", color="#16a34a")
    plt.axvline(best_epoch - 1, color="gray", linestyle="--")
    plt.title("Validation ROC-AUC")
    plt.xlabel("Epoch")
    plt.ylabel("ROC-AUC")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_path / "tabular_mlp_best_training_curves.png", dpi=150)
    plt.close()

    # Plot 2: ROC curve
    fpr, tpr, _ = roc_curve(y_test, test_probs)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color="#2563eb", lw=2, label=f"Tabular MLP (AUC = {test_auc:.3f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--")
    plt.title("Oxford UCI Test ROC Curve\n(Research Screening Tool Only)")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_path / "tabular_mlp_best_roc_curve.png", dpi=150)
    plt.close()

    # Plot 3: Confusion Matrix
    plt.figure(figsize=(5, 4))
    cm_arr = np.array(cm_cal)
    plt.imshow(cm_arr, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Tabular MLP Confusion Matrix\n(Calibrated Threshold)")
    plt.colorbar()
    tick_marks = [0, 1]
    plt.xticks(tick_marks, ["Healthy", "Parkinsons"])
    plt.yticks(tick_marks, ["Healthy", "Parkinsons"])
    thresh = cm_arr.max() / 2.0
    for i in range(cm_arr.shape[0]):
        for j in range(cm_arr.shape[1]):
            plt.text(j, i, format(cm_arr[i, j], "d"),
                     horizontalalignment="center",
                     color="white" if cm_arr[i, j] > thresh else "black")
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.tight_layout()
    plt.savefig(plots_path / "tabular_mlp_best_confusion_matrix.png", dpi=150)
    plt.close()

    return test_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Tabular MLP on Oxford Parkinson's Dataset")
    parser.add_argument("--data_dir", type=str, default="ml/data/real")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--lr", type=float, default=0.002)
    args = parser.parse_args()

    train_tabular_model(data_dir=args.data_dir, epochs=args.epochs, lr=args.lr)
