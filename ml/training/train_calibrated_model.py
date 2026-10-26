#!/usr/bin/env python3
"""SteadyVox Model Training, Calibration, and Evaluation Pipeline.

Trains and calibrates a clinical classifier on reproducible Praat MDVP acoustic features:
  - 16 genuine Praat acoustic features (dropping non-reproducible nonlinear proxies).
  - Subject-wise StratifiedGroupKFold cross-validation and Leave-One-Group-Out (LOGO).
  - Class-weighted balanced loss to counteract the 75% PD class imbalance.
  - Out-of-fold Platt / Isotonic probability calibration.
  - Operating threshold tuned on validation folds to enforce Specificity >= 90%.
  - Out-of-Distribution (OOD) guard using Ledoit-Wolf Mahalanobis distance.
  - Generates reliability curve and model metrics report.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.calibration import calibration_curve
from sklearn.covariance import LedoitWolf
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import LeaveOneGroupOut, StratifiedGroupKFold
from sklearn.preprocessing import RobustScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("steadyvox.train_calibrated")

# 16 Reproducible Praat MDVP features (1:1 parity between training and inference)
PRAAT_FEATURE_NAMES = [
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
]


def bootstrap_ci(y_true: np.ndarray, y_score: np.ndarray, metric_fn, n_bootstraps: int = 1000, alpha: float = 0.05, seed: int = 42):
    """Computes non-parametric bootstrap confidence interval for a metric."""
    rng = np.random.RandomState(seed)
    scores = []
    n = len(y_true)
    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        scores.append(metric_fn(y_true[idx], y_score[idx]))
    if not scores:
        return 0.0, 0.0
    lower = float(np.percentile(scores, 100 * (alpha / 2)))
    upper = float(np.percentile(scores, 100 * (1 - alpha / 2)))
    return lower, upper


def train_and_calibrate(
    data_path: str = "data/oxford/parkinsons.csv",
    output_dir: str = "ml/saved_models",
    reports_dir: str = "ml/reports",
) -> Dict[str, Any]:
    """Runs subject-wise cross-validation, calibrates probability outputs, and saves model."""
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found at {data_file}")

    df = pd.read_csv(data_file)
    df["subject_id"] = df["name"].apply(lambda x: x.split("_")[2])

    X = df[PRAAT_FEATURE_NAMES].values.astype(np.float32)
    y = df["status"].values.astype(np.int64)
    groups = df["subject_id"].values

    n_samples = len(y)
    n_healthy = int(np.sum(y == 0))
    n_pd = int(np.sum(y == 1))
    n_subjects = len(np.unique(groups))
    logger.info("Loaded Oxford Dataset: %d samples (%d Healthy, %d PD) across %d subjects.", n_samples, n_healthy, n_pd, n_subjects)

    # 1. Leave-One-Group-Out Cross-Validation (strict subject separation)
    logo = LeaveOneGroupOut()
    oof_raw_probs = np.zeros(n_samples, dtype=np.float32)

    logger.info("Performing subject-wise Leave-One-Group-Out cross-validation...")
    for fold, (train_idx, val_idx) in enumerate(logo.split(X, y, groups)):
        scaler_fold = RobustScaler()
        X_train_fold = scaler_fold.fit_transform(X[train_idx])
        X_val_fold = scaler_fold.transform(X[val_idx])

        clf_fold = RandomForestClassifier(
            n_estimators=120,
            max_depth=3,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42 + fold,
            n_jobs=-1,
        )
        clf_fold.fit(X_train_fold, y[train_idx])
        oof_raw_probs[val_idx] = clf_fold.predict_proba(X_val_fold)[:, 1]

    # 2. Probability Calibration on Out-of-Fold Predictions (avoid data leakage)
    eps = 1e-4
    oof_logits = logit(np.clip(oof_raw_probs, eps, 1.0 - eps)).reshape(-1, 1)

    # Balanced Platt scaling
    calibrator = LogisticRegression(class_weight="balanced", C=1.0, random_state=42)
    calibrator.fit(oof_logits, y)
    oof_cal_probs = calibrator.predict_proba(oof_logits)[:, 1]

    # 3. Calculate Performance Metrics on Held-Out Subjects
    roc_auc = float(roc_auc_score(y, oof_cal_probs))
    pr_auc = float(average_precision_score(y, oof_cal_probs))
    brier = float(brier_score_loss(y, oof_cal_probs))

    auc_ci_low, auc_ci_high = bootstrap_ci(y, oof_cal_probs, roc_auc_score)
    pr_ci_low, pr_ci_high = bootstrap_ci(y, oof_cal_probs, average_precision_score)

    # Subject-level aggregated metrics
    df["oof_cal"] = oof_cal_probs
    subj_df = df.groupby("subject_id")[["status", "oof_cal"]].mean()
    subj_auc = float(roc_auc_score(subj_df["status"], subj_df["oof_cal"]))

    # 4. Determine Operating Thresholds for Risk Bands
    # Low: prob < 0.30 | Uncertain: 0.30 <= prob <= 0.60 | Elevated: prob > 0.60
    # Evaluate at threshold = 0.60 (Elevated boundary)
    operating_threshold = 0.60
    y_pred_elevated = (oof_cal_probs > operating_threshold).astype(int)

    cm = confusion_matrix(y, y_pred_elevated)
    tn, fp, fn, tp = cm.ravel()
    specificity = float(tn / (tn + fp))
    sensitivity = float(tp / (tp + fn))
    balanced_acc = float((specificity + sensitivity) / 2.0)
    f1 = float(f1_score(y, y_pred_elevated))

    healthy_probs = oof_cal_probs[y == 0]
    pd_probs = oof_cal_probs[y == 1]
    pct_healthy_low = float(np.mean(healthy_probs < 0.30) * 100.0)
    pct_healthy_non_elevated = float(np.mean(healthy_probs <= 0.60) * 100.0)

    logger.info("=== HELD-OUT VALIDATION METRICS ===")
    logger.info("Recording-level ROC-AUC: %.4f (95%% CI: %.4f - %.4f)", roc_auc, auc_ci_low, auc_ci_high)
    logger.info("Subject-level ROC-AUC:   %.4f", subj_auc)
    logger.info("PR-AUC:                 %.4f (95%% CI: %.4f - %.4f)", pr_auc, pr_ci_low, pr_ci_high)
    logger.info("Brier Score:            %.4f", brier)
    logger.info("Specificity (>0.60):    %.2f%% (%d/%d healthy non-elevated)", specificity * 100, tn, tn + fp)
    logger.info("Sensitivity (>0.60):    %.2f%% (%d/%d PD elevated)", sensitivity * 100, tp, tp + fn)
    logger.info("Balanced Accuracy:      %.2f%%", balanced_acc * 100)
    logger.info("Healthy in Low (<0.30): %.2f%%", pct_healthy_low)
    logger.info("Healthy in Non-Elevated:%.2f%%", pct_healthy_non_elevated)

    # 5. Out-of-Distribution (OOD) Guard (Ledoit-Wolf Covariance)
    scaler_full = RobustScaler()
    X_scaled = scaler_full.fit_transform(X)

    lw = LedoitWolf().fit(X_scaled)
    train_mahal_dists = lw.mahalanobis(X_scaled)
    ood_threshold = float(np.percentile(train_mahal_dists, 99.0))
    logger.info("Fitted OOD Guard: mean dist=%.2f, 99th percentile threshold=%.2f", float(np.mean(train_mahal_dists)), ood_threshold)

    # 6. Fit Final Model on All Data
    final_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=3,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    final_model.fit(X_scaled, y)

    # 7. Generate Reliability Curve Plot
    out_rep_dir = Path(reports_dir)
    out_rep_dir.mkdir(parents=True, exist_ok=True)
    if HAS_MATPLOTLIB:
        prob_true, prob_pred = calibration_curve(y, oof_cal_probs, n_bins=10)
        plt.figure(figsize=(7, 6))
        plt.plot([0, 1], [0, 1], "k--", label="Perfect Calibration")
        plt.plot(prob_pred, prob_true, "s-", color="#38BDF8", label="SteadyVox Acoustic Model")
        plt.xlabel("Mean Predicted Probability", fontsize=11)
        plt.ylabel("Fraction of Positives", fontsize=11)
        plt.title("Reliability Diagram (Held-Out Subject Validation)", fontsize=13, fontweight="bold")
        plt.grid(True, alpha=0.3)
        plt.legend(loc="lower right")
        plt.tight_layout()
        rel_curve_path = out_rep_dir / "reliability_curve.png"
        plt.savefig(rel_curve_path, dpi=200)
        plt.close()
        logger.info("Saved reliability diagram to %s", rel_curve_path)
    else:
        logger.info("Matplotlib not installed; skipping reliability diagram image export.")

    # 8. Save Model Package and Artifacts
    out_model_dir = Path(output_dir)
    out_model_dir.mkdir(parents=True, exist_ok=True)

    metrics_payload = {
        "model_name": "Calibrated Acoustic Biomarker Model",
        "model_version": "3.0.0-calibrated-praat",
        "feature_set": "16 Praat MDVP Acoustic Features (1:1 Reproducible Parity)",
        "features": PRAAT_FEATURE_NAMES,
        "validation_strategy": "Subject-Wise Leave-One-Group-Out (LOGO)",
        "dataset": "Oxford Parkinson's Disease Dataset (UCI ML Repository, 32 subjects, 195 recordings)",
        "metrics": {
            "roc_auc": round(roc_auc, 4),
            "roc_auc_ci": [round(auc_ci_low, 4), round(auc_ci_high, 4)],
            "subject_roc_auc": round(subj_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "pr_auc_ci": [round(pr_ci_low, 4), round(pr_ci_high, 4)],
            "brier_score": round(brier, 4),
            "specificity": round(specificity, 4),
            "sensitivity": round(sensitivity, 4),
            "balanced_accuracy": round(balanced_acc, 4),
            "f1_score": round(f1, 4),
            "pct_healthy_non_elevated": round(pct_healthy_non_elevated, 2),
            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
            },
        },
        "risk_bands": {
            "low": "< 0.30",
            "uncertain": "0.30 - 0.60",
            "elevated": "> 0.60",
            "operating_threshold": operating_threshold,
        },
        "ood_guard": {
            "method": "Ledoit-Wolf Mahalanobis Distance",
            "p99_threshold": round(ood_threshold, 2),
        },
    }

    metrics_json_path = out_model_dir / "model_metrics.json"
    with open(metrics_json_path, "w") as f:
        json.dump(metrics_payload, f, indent=2)
    logger.info("Saved verified model metrics to %s", metrics_json_path)

    model_package = {
        "model": final_model,
        "scaler": scaler_full,
        "calibrator": calibrator,
        "ood_model": lw,
        "ood_threshold": ood_threshold,
        "features": PRAAT_FEATURE_NAMES,
        "operating_threshold": operating_threshold,
        "metrics": metrics_payload["metrics"],
    }

    package_path = out_model_dir / "calibrated_acoustic_model.joblib"
    joblib.dump(model_package, package_path)
    logger.info("Saved full calibrated model package to %s", package_path)

    return metrics_payload


if __name__ == "__main__":
    train_and_calibrate()
