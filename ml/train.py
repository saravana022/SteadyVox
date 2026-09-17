#!/usr/bin/env python3
"""Training pipeline for the three Parkinson's disease datasets.

Classification (Oxford, Istanbul):
  • Random Forest (sklearn)
  • MLP Classifier (sklearn)

Regression (Telemonitoring):
  • Gradient Boosting Regressor (sklearn)
  • MLP Regressor (sklearn)

Logs accuracy/F1 for classification, RMSE/MAE for regression.
Saves best models to ml/saved_models/ with clear filenames per dataset.
"""

import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    roc_auc_score,
    r2_score,
)
from sklearn.neural_network import MLPClassifier, MLPRegressor

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "ml" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42


def section(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


# ---------------------------------------------------------------------------
# Classification training
# ---------------------------------------------------------------------------

def train_classification(dataset_name: str) -> dict:
    """Train RF + MLP on a classification dataset. Returns metrics dict."""
    section(f"Training Classification: {dataset_name}")

    split_dir = DATA_DIR / dataset_name.lower() / "splits"
    train_path = split_dir / "train.npz"
    test_path = split_dir / "test.npz"

    if not train_path.exists() or not test_path.exists():
        print(f"  ✗ Splits not found at {split_dir}. Run ml/preprocess.py first.")
        return {}

    train_data = np.load(train_path)
    test_data = np.load(test_path)
    X_train, y_train = train_data["X"], train_data["y"]
    X_test, y_test = test_data["X"], test_data["y"]

    print(f"  Train: {X_train.shape} | Test: {X_test.shape}")

    results = {}

    # ── Random Forest ─────────────────────────────────────────────────
    print("\n  [1/2] Random Forest …")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=SEED,
        n_jobs=-1,
        class_weight="balanced",
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_prob_rf = rf.predict_proba(X_test)

    acc_rf = accuracy_score(y_test, y_pred_rf)
    f1_rf = f1_score(y_test, y_pred_rf, average="weighted")
    prec_rf = precision_score(y_test, y_pred_rf, average="weighted", zero_division=0)
    rec_rf = recall_score(y_test, y_pred_rf, average="weighted", zero_division=0)

    # ROC-AUC (handle binary vs multiclass)
    try:
        if y_prob_rf.shape[1] == 2:
            auc_rf = roc_auc_score(y_test, y_prob_rf[:, 1])
        else:
            auc_rf = roc_auc_score(y_test, y_prob_rf, multi_class="ovr", average="weighted")
    except Exception:
        auc_rf = float("nan")

    rf_metrics = {
        "accuracy": round(acc_rf, 4),
        "f1": round(f1_rf, 4),
        "precision": round(prec_rf, 4),
        "recall": round(rec_rf, 4),
        "roc_auc": round(auc_rf, 4),
    }
    results["random_forest"] = rf_metrics
    print(f"    Accuracy: {acc_rf:.4f} | F1: {f1_rf:.4f} | ROC‑AUC: {auc_rf:.4f}")

    # Save RF model
    rf_path = MODEL_DIR / f"{dataset_name.lower()}_rf_best.pkl"
    joblib.dump(rf, rf_path)
    print(f"    Saved → {rf_path}")

    # ── MLP Classifier ────────────────────────────────────────────────
    print("\n  [2/2] MLP Classifier …")
    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        solver="adam",
        alpha=1e-3,
        batch_size=32,
        learning_rate="adaptive",
        learning_rate_init=1e-3,
        max_iter=500,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=20,
        random_state=SEED,
    )
    mlp.fit(X_train, y_train)
    y_pred_mlp = mlp.predict(X_test)
    y_prob_mlp = mlp.predict_proba(X_test)

    acc_mlp = accuracy_score(y_test, y_pred_mlp)
    f1_mlp = f1_score(y_test, y_pred_mlp, average="weighted")
    prec_mlp = precision_score(y_test, y_pred_mlp, average="weighted", zero_division=0)
    rec_mlp = recall_score(y_test, y_pred_mlp, average="weighted", zero_division=0)

    try:
        if y_prob_mlp.shape[1] == 2:
            auc_mlp = roc_auc_score(y_test, y_prob_mlp[:, 1])
        else:
            auc_mlp = roc_auc_score(y_test, y_prob_mlp, multi_class="ovr", average="weighted")
    except Exception:
        auc_mlp = float("nan")

    mlp_metrics = {
        "accuracy": round(acc_mlp, 4),
        "f1": round(f1_mlp, 4),
        "precision": round(prec_mlp, 4),
        "recall": round(rec_mlp, 4),
        "roc_auc": round(auc_mlp, 4),
    }
    results["mlp"] = mlp_metrics
    print(f"    Accuracy: {acc_mlp:.4f} | F1: {f1_mlp:.4f} | ROC‑AUC: {auc_mlp:.4f}")

    # Save MLP model
    mlp_path = MODEL_DIR / f"{dataset_name.lower()}_mlp_best.pkl"
    joblib.dump(mlp, mlp_path)
    print(f"    Saved → {mlp_path}")

    # ── Best model selection ──────────────────────────────────────────
    best = "random_forest" if f1_rf >= f1_mlp else "mlp"
    print(f"\n  ★ Best model for {dataset_name}: {best} (F1={results[best]['f1']:.4f})")

    return results


# ---------------------------------------------------------------------------
# Regression training
# ---------------------------------------------------------------------------

def train_regression(dataset_name: str = "telemonitoring") -> dict:
    """Train GBR + MLP Regressor on the Telemonitoring dataset."""
    section(f"Training Regression: {dataset_name}")

    split_dir = DATA_DIR / dataset_name.lower() / "splits"
    train_path = split_dir / "train.npz"
    test_path = split_dir / "test.npz"

    if not train_path.exists() or not test_path.exists():
        print(f"  ✗ Splits not found at {split_dir}. Run ml/preprocess.py first.")
        return {}

    train_data = np.load(train_path)
    test_data = np.load(test_path)
    X_train, y_train = train_data["X"], train_data["y"]
    X_test, y_test = test_data["X"], test_data["y"]

    # Load target names
    target_names_path = split_dir / "target_names.json"
    if target_names_path.exists():
        with open(target_names_path) as f:
            target_names = json.load(f)
    else:
        target_names = [f"target_{i}" for i in range(y_train.shape[1])]

    print(f"  Train: {X_train.shape} | Test: {X_test.shape}")
    print(f"  Targets: {target_names}")

    results = {}

    # Train separate models per target
    for t_idx, t_name in enumerate(target_names):
        print(f"\n  ── Target: {t_name} ──")
        y_tr = y_train[:, t_idx]
        y_te = y_test[:, t_idx]

        # ── Gradient Boosting ─────────────────────────────────────────
        print("    [1/2] Gradient Boosting Regressor …")
        gbr = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=SEED,
        )
        gbr.fit(X_train, y_tr)
        y_pred_gb = gbr.predict(X_test)

        rmse_gb = float(np.sqrt(mean_squared_error(y_te, y_pred_gb)))
        mae_gb = float(mean_absolute_error(y_te, y_pred_gb))
        r2_gb = float(r2_score(y_te, y_pred_gb))

        gb_metrics = {"rmse": round(rmse_gb, 4), "mae": round(mae_gb, 4), "r2": round(r2_gb, 4)}
        results[f"{t_name}_gradient_boosting"] = gb_metrics
        print(f"      RMSE: {rmse_gb:.4f} | MAE: {mae_gb:.4f} | R²: {r2_gb:.4f}")

        gb_path = MODEL_DIR / f"{dataset_name.lower()}_{t_name}_gb_best.pkl"
        joblib.dump(gbr, gb_path)
        print(f"      Saved → {gb_path}")

        # ── MLP Regressor ─────────────────────────────────────────────
        print("    [2/2] MLP Regressor …")
        mlp_reg = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            activation="relu",
            solver="adam",
            alpha=1e-3,
            batch_size=64,
            learning_rate="adaptive",
            learning_rate_init=1e-3,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=SEED,
        )
        mlp_reg.fit(X_train, y_tr)
        y_pred_mlp = mlp_reg.predict(X_test)

        rmse_mlp = float(np.sqrt(mean_squared_error(y_te, y_pred_mlp)))
        mae_mlp = float(mean_absolute_error(y_te, y_pred_mlp))
        r2_mlp = float(r2_score(y_te, y_pred_mlp))

        mlp_metrics = {"rmse": round(rmse_mlp, 4), "mae": round(mae_mlp, 4), "r2": round(r2_mlp, 4)}
        results[f"{t_name}_mlp_regressor"] = mlp_metrics
        print(f"      RMSE: {rmse_mlp:.4f} | MAE: {mae_mlp:.4f} | R²: {r2_mlp:.4f}")

        mlp_path = MODEL_DIR / f"{dataset_name.lower()}_{t_name}_mlp_best.pkl"
        joblib.dump(mlp_reg, mlp_path)
        print(f"      Saved → {mlp_path}")

        # Best model for this target
        best = "gradient_boosting" if rmse_gb <= rmse_mlp else "mlp_regressor"
        best_rmse = min(rmse_gb, rmse_mlp)
        print(f"    ★ Best for {t_name}: {best} (RMSE={best_rmse:.4f})")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SteadyVox – Multi‑Dataset Training Pipeline")
    print("  Research screening tool only — not a medical diagnosis.")
    print("=" * 60)

    all_results = {}

    # Classification datasets
    for ds in ["Oxford", "Istanbul"]:
        metrics = train_classification(ds)
        if metrics:
            all_results[ds] = metrics

    # Regression dataset
    reg_metrics = train_regression("Telemonitoring")
    if reg_metrics:
        all_results["Telemonitoring"] = reg_metrics

    # Save all results
    results_path = MODEL_DIR / "training_results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  All results saved → {results_path}")

    # Print summary
    section("Training Summary")
    for ds, models in all_results.items():
        print(f"\n  {ds}:")
        for model_name, metrics in models.items():
            metrics_str = " | ".join(f"{k}={v}" for k, v in metrics.items())
            print(f"    {model_name}: {metrics_str}")

    print("\n" + "=" * 60)
    print("  Training complete.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
