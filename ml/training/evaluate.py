"""SteadyVox Model Evaluation & Visualization Suite.

Computes comprehensive classification metrics on the held-out test set
and generates publication-quality diagnostic plots (ROC Curve, PR Curve,
Confusion Matrix, and Loss/Accuracy curves).

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    classification_report,
)

from ml.data.dataset import create_dataloaders
from ml.models.cnn_baseline import CNNBaseline
from ml.models.cnn_bilstm import CNNBiLSTM

DISCLAIMER_NOTE = "Research screening tool only — not a medical diagnosis."


def evaluate_test_set(
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
    
    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.5

    cm = confusion_matrix(y_true, y_pred)
    # TN, FP, FN, TP
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    else:
        specificity = 0.0

    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall_sensitivity": float(rec),
        "specificity": float(specificity),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "confusion_matrix": cm.tolist(),
        "y_true": y_true,
        "y_prob": y_prob,
        "y_pred": y_pred,
        "disclaimer": DISCLAIMER_NOTE,
    }


def plot_metrics(
    eval_results: Dict[str, Any],
    history: Dict[str, list],
    output_dir: Path,
    model_name: str = "cnn_baseline",
):
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true = eval_results["y_true"]
    y_prob = eval_results["y_prob"]
    cm = np.array(eval_results["confusion_matrix"])

    # 1. Confusion Matrix Plot
    plt.figure(figsize=(6, 5), dpi=150)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Healthy", "Parkinson's"],
        yticklabels=["Healthy", "Parkinson's"],
        cbar=False,
    )
    plt.title(f"Confusion Matrix ({model_name})\n{DISCLAIMER_NOTE}", fontsize=10, pad=10)
    plt.xlabel("Predicted Label", fontsize=10)
    plt.ylabel("Ground Truth Label", fontsize=10)
    plt.tight_layout()
    cm_path = output_dir / f"{model_name}_confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()

    # 2. ROC-AUC Curve
    if len(np.unique(y_true)) > 1:
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        plt.figure(figsize=(6, 5), dpi=150)
        plt.plot(fpr, tpr, color="#0d9488", lw=2, label=f"ROC (AUC = {eval_results['roc_auc']:.3f})")
        plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Chance")
        plt.xlim([-0.02, 1.02])
        plt.ylim([-0.02, 1.05])
        plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=10)
        plt.ylabel("True Positive Rate (Sensitivity)", fontsize=10)
        plt.title(f"ROC Curve - {model_name}\n{DISCLAIMER_NOTE}", fontsize=10, pad=10)
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        roc_path = output_dir / f"{model_name}_roc_curve.png"
        plt.savefig(roc_path)
        plt.close()

    # 3. Training & Validation Curves (if history exists)
    if history and "train_loss" in history:
        epochs = range(1, len(history["train_loss"]) + 1)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=150)

        # Loss
        ax1.plot(epochs, history["train_loss"], label="Train Loss", color="#0284c7", lw=2)
        ax1.plot(epochs, history["val_loss"], label="Val Loss", color="#e11d48", lw=2)
        ax1.set_title("Training vs Validation Loss", fontsize=11)
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Binary Cross Entropy")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Accuracy / AUC
        ax2.plot(epochs, history["train_acc"], label="Train Acc", color="#0284c7", lw=2)
        ax2.plot(epochs, history["val_acc"], label="Val Acc", color="#e11d48", lw=2)
        if "val_auc" in history:
            ax2.plot(epochs, history["val_auc"], label="Val AUC", color="#0d9488", lw=2, linestyle=":")
        ax2.set_title("Training vs Validation Accuracy & AUC", fontsize=11)
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Score")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.suptitle(f"SteadyVox Training Dynamics ({model_name}) | {DISCLAIMER_NOTE}", fontsize=10)
        plt.tight_layout()
        curves_path = output_dir / f"{model_name}_training_curves.png"
        plt.savefig(curves_path)
        plt.close()


def run_evaluation(
    data_dir: str = "ml/data/processed",
    model_path: str = "ml/saved_models/cnn_baseline_best.pt",
    reports_dir: str = "ml/reports",
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running evaluation using {device}...")

    # Load test loader
    _, _, test_loader, _ = create_dataloaders(data_dir=data_dir, batch_size=8)

    # Load model checkpoint
    ckpt_path = Path(model_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found at {model_path}")

    checkpoint = torch.load(ckpt_path, map_location=device)
    model_type = checkpoint.get("model_type", "cnn_baseline")
    if model_type == "cnn_bilstm":
        model = CNNBiLSTM().to(device)
    else:
        model = CNNBaseline().to(device)
    model.load_state_dict(checkpoint["model_state_dict"])

    eval_results = evaluate_test_set(model, test_loader, device)

    # Print summary table
    print("\n" + "=" * 55)
    print("      STEADYVOX EVALUATION RESULTS (HELD-OUT TEST SET)")
    print("   Notice: " + DISCLAIMER_NOTE)
    print("=" * 55)
    print(f"Accuracy:            {eval_results['accuracy']:.4f} ({eval_results['accuracy']*100:.1f}%)")
    print(f"Precision:           {eval_results['precision']:.4f}")
    print(f"Recall/Sensitivity:  {eval_results['recall_sensitivity']:.4f}")
    print(f"Specificity:         {eval_results['specificity']:.4f}")
    print(f"F1-Score:            {eval_results['f1_score']:.4f}")
    print(f"ROC-AUC:             {eval_results['roc_auc']:.4f}")
    print("=" * 55 + "\n")

    # Load training history if available
    history_file = ckpt_path.parent / f"{ckpt_path.stem.replace('_best', '')}_history.json"
    history = {}
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)

    # Generate plots
    plots_dir = Path(reports_dir) / "plots"
    plot_metrics(eval_results, history, plots_dir, model_name=ckpt_path.stem)

    # Save JSON metrics report (stripping arrays)
    report_data = {
        "model_name": ckpt_path.stem,
        "checkpoint_epoch": checkpoint.get("epoch"),
        "accuracy": eval_results["accuracy"],
        "precision": eval_results["precision"],
        "recall_sensitivity": eval_results["recall_sensitivity"],
        "specificity": eval_results["specificity"],
        "f1_score": eval_results["f1_score"],
        "roc_auc": eval_results["roc_auc"],
        "confusion_matrix": eval_results["confusion_matrix"],
        "test_samples": len(eval_results["y_true"]),
        "disclaimer": DISCLAIMER_NOTE,
    }

    report_path = Path(reports_dir) / f"{ckpt_path.stem}_metrics.json"
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"Saved evaluation metrics report to: {report_path}")
    print(f"Saved plots to: {plots_dir}")
    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SteadyVox Model")
    parser.add_argument("--data_dir", type=str, default="ml/data/processed")
    parser.add_argument("--model_path", type=str, default="ml/saved_models/cnn_baseline_best.pt")
    parser.add_argument("--reports_dir", type=str, default="ml/reports")
    args = parser.parse_args()

    run_evaluation(
        data_dir=args.data_dir,
        model_path=args.model_path,
        reports_dir=args.reports_dir,
    )
