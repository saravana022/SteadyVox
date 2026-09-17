"""SteadyVox Model Comparison Suite.

Compares:
1. Tabular MLP (Oxford Parkinson's Disease Detection Dataset, Little et al., 2007) — Real Clinical Acoustic Benchmark
2. CNN Baseline (2D Log Mel-Spectrogram) — Biophysical Phonation Benchmark
3. CNN + BiLSTM (2D Log Mel-Spectrogram + Recurrent Temporal Context) — Biophysical Phonation Benchmark

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    average_precision_score,
    confusion_matrix,
)

from ml.data.dataset import create_dataloaders
from ml.models.cnn_baseline import CNNBaseline
from ml.models.cnn_bilstm import CNNBiLSTM
from ml.models.tabular_mlp import FEATURE_NAMES, TabularMLP

DISCLAIMER_NOTE = "Research screening tool only — not a medical diagnosis."


def evaluate_audio_model(
    model: torch.nn.Module,
    test_loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> Dict[str, Any]:
    model.eval()
    all_targets = []
    all_probs = []

    with torch.no_grad():
        for batch_x, batch_y, _ in test_loader:
            batch_x = batch_x.to(device)
            logits = model(batch_x)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()
            targets = batch_y.numpy().flatten()

            all_probs.extend(probs)
            all_targets.extend(targets)

    y_true = np.array(all_targets, dtype=int)
    y_prob = np.array(all_probs, dtype=float)
    y_pred = (y_prob >= 0.50).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": cm,
        "y_true": y_true,
        "y_prob": y_prob,
    }


def evaluate_tabular_model(
    model_path: str = "ml/saved_models/tabular_mlp_best.pt",
    scaler_path: str = "ml/saved_models/tabular_scaler.joblib",
    real_data_dir: str = "ml/data/real",
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    test_csv = Path(real_data_dir) / "test.csv"
    if not test_csv.exists():
        raise FileNotFoundError(f"Missing {test_csv}")

    test_df = pd.read_csv(test_csv)
    scaler = joblib.load(scaler_path)

    X_test_raw = test_df[FEATURE_NAMES].values.astype(np.float32)
    y_true = test_df["status"].values.astype(int)

    X_test = scaler.transform(X_test_raw)
    X_test_t = torch.from_numpy(X_test).float().to(device)

    ckpt = torch.load(model_path, map_location=device, weights_only=False)
    model = TabularMLP()
    model.load_state_dict(ckpt["model_state_dict"])
    cal_thresh = ckpt.get("calibrated_threshold", 0.93)
    model.calibrated_threshold = cal_thresh
    model.to(device)
    model.eval()

    with torch.no_grad():
        logits = model(X_test_t)
        probs = torch.sigmoid(logits).cpu().numpy().flatten()

    preds = (probs >= cal_thresh).astype(int)

    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, zero_division=0)
    rec = recall_score(y_true, preds, zero_division=0)
    f1 = f1_score(y_true, preds, zero_division=0)
    auc = roc_auc_score(y_true, probs)
    pr_auc = average_precision_score(y_true, probs)
    cm = confusion_matrix(y_true, preds).tolist()

    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": cm,
        "calibrated_threshold": float(cal_thresh),
        "y_true": y_true,
        "y_prob": probs,
    }


def run_full_comparison(
    audio_data_dir: str = "ml/data/processed",
    real_data_dir: str = "ml/data/real",
    saved_models_dir: str = "ml/saved_models",
    reports_dir: str = "ml/reports",
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running SteadyVox Comprehensive Model Comparison on: {device}")

    # 1. Evaluate Tabular MLP on Oxford Real Dataset
    tab_res = evaluate_tabular_model(
        model_path=f"{saved_models_dir}/tabular_mlp_best.pt",
        scaler_path=f"{saved_models_dir}/tabular_scaler.joblib",
        real_data_dir=real_data_dir,
        device=device,
    )

    # 2. Evaluate Audio Models on Audio Benchmark Dataset
    _, _, test_loader, _ = create_dataloaders(data_dir=audio_data_dir, batch_size=16)

    cnn_ckpt = torch.load(f"{saved_models_dir}/cnn_baseline_best.pt", map_location=device, weights_only=False)
    cnn_model = CNNBaseline().to(device)
    cnn_model.load_state_dict(cnn_ckpt["model_state_dict"])
    cnn_res = evaluate_audio_model(cnn_model, test_loader, device)

    bilstm_ckpt = torch.load(f"{saved_models_dir}/cnn_bilstm_best.pt", map_location=device, weights_only=False)
    bilstm_model = CNNBiLSTM().to(device)
    bilstm_model.load_state_dict(bilstm_ckpt["model_state_dict"])
    bilstm_res = evaluate_audio_model(bilstm_model, test_loader, device)

    # Unified Comparison Table
    records = [
        {
            "Model Name": "Tabular MLP (Primary)",
            "Architecture": "MLP (22 Biomarkers, LayerNorm)",
            "Dataset": "Oxford Parkinson's (Real UCI, Little et al.)",
            "Provenance": "Real Clinical Dataset",
            "ROC-AUC": round(tab_res["roc_auc"], 4),
            "PR-AUC": round(tab_res["pr_auc"], 4),
            "Accuracy": round(tab_res["accuracy"], 4),
            "Precision": round(tab_res["precision"], 4),
            "Recall": round(tab_res["recall"], 4),
            "F1-Score": round(tab_res["f1_score"], 4),
        },
        {
            "Model Name": "CNN + BiLSTM",
            "Architecture": "CNN + Bidirectional LSTM (Mel-Spec)",
            "Dataset": "Sustained /a/ Phonation Benchmark (600 spk)",
            "Provenance": "Synthetic Audio Benchmark",
            "ROC-AUC": round(bilstm_res["roc_auc"], 4),
            "PR-AUC": round(bilstm_res["pr_auc"], 4),
            "Accuracy": round(bilstm_res["accuracy"], 4),
            "Precision": round(bilstm_res["precision"], 4),
            "Recall": round(bilstm_res["recall"], 4),
            "F1-Score": round(bilstm_res["f1_score"], 4),
        },
        {
            "Model Name": "CNN Baseline",
            "Architecture": "4-Stage 2D CNN (Log Mel-Spec)",
            "Dataset": "Sustained /a/ Phonation Benchmark (600 spk)",
            "Provenance": "Synthetic Audio Benchmark",
            "ROC-AUC": round(cnn_res["roc_auc"], 4),
            "PR-AUC": round(cnn_res["pr_auc"], 4),
            "Accuracy": round(cnn_res["accuracy"], 4),
            "Precision": round(cnn_res["precision"], 4),
            "Recall": round(cnn_res["recall"], 4),
            "F1-Score": round(cnn_res["f1_score"], 4),
        },
    ]

    df_cmp = pd.DataFrame(records)
    print("\n" + "=" * 92)
    print("             STEADYVOX COMPREHENSIVE MULTI-MODEL BENCHMARK COMPARISON")
    print(f"                      {DISCLAIMER_NOTE}")
    print("=" * 92)
    print(df_cmp[["Model Name", "Provenance", "ROC-AUC", "PR-AUC", "Accuracy", "Recall", "F1-Score"]].to_string(index=False))
    print("=" * 92)

    # Save comparison CSV and JSON
    rep_path = Path(reports_dir)
    rep_path.mkdir(parents=True, exist_ok=True)
    plots_path = rep_path / "plots"
    plots_path.mkdir(parents=True, exist_ok=True)

    csv_path = rep_path / "model_comparison_table.csv"
    df_cmp.to_csv(csv_path, index=False)

    json_report = {
        "disclaimer": DISCLAIMER_NOTE,
        "models": records,
        "details": {
            "tabular_mlp": {
                "dataset": "Oxford Parkinson's (Little et al., 2007)",
                "provenance": "real_dataset",
                "test_samples": len(tab_res["y_true"]),
                "calibrated_threshold": tab_res["calibrated_threshold"],
                "roc_auc": tab_res["roc_auc"],
                "pr_auc": tab_res["pr_auc"],
                "accuracy": tab_res["accuracy"],
                "precision": tab_res["precision"],
                "recall": tab_res["recall"],
                "f1_score": tab_res["f1_score"],
                "confusion_matrix": tab_res["confusion_matrix"],
            },
            "cnn_bilstm": {
                "dataset": "Synthetic Sustained Phonation Benchmark",
                "provenance": "synthetic_audio",
                "test_samples": len(bilstm_res["y_true"]),
                "roc_auc": bilstm_res["roc_auc"],
                "pr_auc": bilstm_res["pr_auc"],
                "accuracy": bilstm_res["accuracy"],
                "precision": bilstm_res["precision"],
                "recall": bilstm_res["recall"],
                "f1_score": bilstm_res["f1_score"],
                "confusion_matrix": bilstm_res["confusion_matrix"],
            },
            "cnn_baseline": {
                "dataset": "Synthetic Sustained Phonation Benchmark",
                "provenance": "synthetic_audio",
                "test_samples": len(cnn_res["y_true"]),
                "roc_auc": cnn_res["roc_auc"],
                "pr_auc": cnn_res["pr_auc"],
                "accuracy": cnn_res["accuracy"],
                "precision": cnn_res["precision"],
                "recall": cnn_res["recall"],
                "f1_score": cnn_res["f1_score"],
                "confusion_matrix": cnn_res["confusion_matrix"],
            },
        },
    }

    with open(rep_path / "model_comparison_report.json", "w") as f:
        json.dump(json_report, f, indent=2)

    # Plot Multi-Model Overlaid ROC Curves
    fpr_tab, tpr_tab, _ = roc_curve(tab_res["y_true"], tab_res["y_prob"])
    fpr_cnn, tpr_cnn, _ = roc_curve(cnn_res["y_true"], cnn_res["y_prob"])
    fpr_bilstm, tpr_bilstm, _ = roc_curve(bilstm_res["y_true"], bilstm_res["y_prob"])

    plt.figure(figsize=(8, 7), dpi=150)
    plt.plot(
        fpr_tab,
        tpr_tab,
        color="#2563eb",
        lw=2.5,
        label=f"Tabular MLP [Real Oxford UCI] (AUC = {tab_res['roc_auc']:.3f})",
    )
    plt.plot(
        fpr_bilstm,
        tpr_bilstm,
        color="#0d9488",
        lw=2.5,
        label=f"CNN + BiLSTM [Audio Benchmark] (AUC = {bilstm_res['roc_auc']:.3f})",
    )
    plt.plot(
        fpr_cnn,
        tpr_cnn,
        color="#64748b",
        lw=2.0,
        linestyle="--",
        label=f"CNN Baseline [Audio Benchmark] (AUC = {cnn_res['roc_auc']:.3f})",
    )
    plt.plot([0, 1], [0, 1], color="#9ca3af", lw=1, linestyle=":", label="Chance Baseline (AUC = 0.500)")
    
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    plt.ylabel("True Positive Rate (Sensitivity)", fontsize=11)
    plt.title(f"SteadyVox Model Comparison: Held-Out Test ROC Curves\n{DISCLAIMER_NOTE}", fontsize=10, pad=10)
    plt.legend(loc="lower right", frameon=True, fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    cmp_plot_path = plots_path / "model_comparison_roc.png"
    plt.savefig(cmp_plot_path)
    plt.close()

    print(f"Saved comparative report to: {rep_path / 'model_comparison_report.json'}")
    print(f"Saved comparison plot to: {cmp_plot_path}")
    return json_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SteadyVox Multi-Model Comparison")
    parser.add_argument("--audio_data_dir", type=str, default="ml/data/processed")
    parser.add_argument("--real_data_dir", type=str, default="ml/data/real")
    parser.add_argument("--saved_models_dir", type=str, default="ml/saved_models")
    parser.add_argument("--reports_dir", type=str, default="ml/reports")
    args = parser.parse_args()

    run_full_comparison(
        audio_data_dir=args.audio_data_dir,
        real_data_dir=args.real_data_dir,
        saved_models_dir=args.saved_models_dir,
        reports_dir=args.reports_dir,
    )
