#!/usr/bin/env python3
"""Evaluation script – loads saved models, computes metrics on held‑out test sets,
and writes a markdown comparison table to results/comparison.md.

Research screening tool only — not a medical diagnosis.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "ml" / "saved_models"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


# ---------------------------------------------------------------------------
# Evaluate classification dataset
# ---------------------------------------------------------------------------

def evaluate_classification(dataset_name: str) -> list:
    """Evaluate RF + MLP on a classification dataset. Returns list of result rows."""
    section(f"Evaluating Classification: {dataset_name}")

    split_dir = DATA_DIR / dataset_name.lower() / "splits"
    test_path = split_dir / "test.npz"
    if not test_path.exists():
        print(f"  ✗ Test split not found: {test_path}")
        return []

    test_data = np.load(test_path)
    X_test, y_test = test_data["X"], test_data["y"]

    rows = []
    for model_label, filename in [("Random Forest", f"{dataset_name.lower()}_rf_best.pkl"),
                                   ("MLP Classifier", f"{dataset_name.lower()}_mlp_best.pkl")]:
        model_path = MODEL_DIR / filename
        if not model_path.exists():
            print(f"  ✗ Model not found: {model_path}")
            continue

        model = joblib.load(model_path)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)

        try:
            if y_prob.shape[1] == 2:
                auc = roc_auc_score(y_test, y_prob[:, 1])
            else:
                auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="weighted")
        except Exception:
            auc = float("nan")

        row = {
            "dataset": dataset_name,
            "task": "Classification",
            "model": model_label,
            "accuracy": round(acc, 4),
            "f1": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "roc_auc": round(auc, 4),
            "rmse": "—",
            "mae": "—",
            "r2": "—",
        }
        rows.append(row)
        print(f"  {model_label}: Acc={acc:.4f} F1={f1:.4f} AUC={auc:.4f}")

    return rows


# ---------------------------------------------------------------------------
# Evaluate regression dataset
# ---------------------------------------------------------------------------

def evaluate_regression(dataset_name: str = "telemonitoring") -> list:
    """Evaluate GBR + MLP Regressor on the Telemonitoring dataset."""
    section(f"Evaluating Regression: {dataset_name}")

    split_dir = DATA_DIR / dataset_name.lower() / "splits"
    test_path = split_dir / "test.npz"
    if not test_path.exists():
        print(f"  ✗ Test split not found: {test_path}")
        return []

    test_data = np.load(test_path)
    X_test, y_test = test_data["X"], test_data["y"]

    target_names_path = split_dir / "target_names.json"
    if target_names_path.exists():
        with open(target_names_path) as f:
            target_names = json.load(f)
    else:
        target_names = [f"target_{i}" for i in range(y_test.shape[1])]

    rows = []
    for t_idx, t_name in enumerate(target_names):
        y_te = y_test[:, t_idx]
        for model_label, filename in [
            ("Gradient Boosting", f"{dataset_name.lower()}_{t_name}_gb_best.pkl"),
            ("MLP Regressor", f"{dataset_name.lower()}_{t_name}_mlp_best.pkl"),
        ]:
            model_path = MODEL_DIR / filename
            if not model_path.exists():
                print(f"  ✗ Model not found: {model_path}")
                continue

            model = joblib.load(model_path)
            y_pred = model.predict(X_test)

            rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))
            mae = float(mean_absolute_error(y_te, y_pred))
            r2 = float(r2_score(y_te, y_pred))

            row = {
                "dataset": f"Telemonitoring ({t_name})",
                "task": "Regression",
                "model": model_label,
                "accuracy": "—",
                "f1": "—",
                "precision": "—",
                "recall": "—",
                "roc_auc": "—",
                "rmse": round(rmse, 4),
                "mae": round(mae, 4),
                "r2": round(r2, 4),
            }
            rows.append(row)
            print(f"  {t_name} / {model_label}: RMSE={rmse:.4f} MAE={mae:.4f} R²={r2:.4f}")

    return rows


# ---------------------------------------------------------------------------
# Generate markdown comparison table
# ---------------------------------------------------------------------------

def generate_markdown(rows: list) -> str:
    md = []
    md.append("# SteadyVox – Multi‑Dataset Model Comparison")
    md.append("")
    md.append("> **Disclaimer:** Research screening tool only — not a medical diagnosis.")
    md.append("")

    # ── Classification table ──────────────────────────────────────────
    clf_rows = [r for r in rows if r["task"] == "Classification"]
    if clf_rows:
        md.append("## Classification Results")
        md.append("")
        md.append("| Dataset | Model | Accuracy | F1 | Precision | Recall | ROC‑AUC |")
        md.append("|---------|-------|----------|-----|-----------|--------|---------|")
        for r in clf_rows:
            md.append(
                f"| {r['dataset']} | {r['model']} | {r['accuracy']} | {r['f1']} | "
                f"{r['precision']} | {r['recall']} | {r['roc_auc']} |"
            )
        md.append("")

    # ── Regression table ──────────────────────────────────────────────
    reg_rows = [r for r in rows if r["task"] == "Regression"]
    if reg_rows:
        md.append("## Regression Results")
        md.append("")
        md.append("| Dataset | Model | RMSE | MAE | R² |")
        md.append("|---------|-------|------|-----|----|")
        for r in reg_rows:
            md.append(
                f"| {r['dataset']} | {r['model']} | {r['rmse']} | {r['mae']} | {r['r2']} |"
            )
        md.append("")

    # ── Notes ─────────────────────────────────────────────────────────
    md.append("## Notes")
    md.append("")
    md.append("- **Oxford** (UCI ID 174): 195 instances, 23 features, binary classification (status: 0=healthy, 1=PD)")
    md.append("- **Istanbul** (UCI ID 470): 252 instances, multiple voice features, binary classification")
    md.append("- **Telemonitoring** (UCI ID 189): 5,875 instances, 16 voice features, regression targets: motor_UPDRS and total_UPDRS")
    md.append("- Datasets are kept **separate** (no merging) to preserve experimental integrity.")
    md.append("- All models use seed=42, test_size=0.2, StandardScaler on training data only.")
    md.append("- Classification uses stratified splitting; regression uses random splitting.")
    md.append("")
    md.append("## Citations")
    md.append("")
    md.append("1. Little, M.A., McSharry, P.E., Roberts, S.J., Costello, D.A.E., Moroz, I.M. (2007). \"Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection\". BioMedical Engineering OnLine, 6:23.")
    md.append("2. Sakar, C.O., et al. (2019). \"A Comparative Analysis of Speech Signal Processing Algorithms for Parkinson's Disease Classification and the Use of the Tunable Q-Factor Wavelet Transform\". Applied Soft Computing, 74, 255-263.")
    md.append("3. Tsanas, A., Little, M.A., McSharry, P.E., Ramig, L.O. (2010). \"Accurate Telemonitoring of Parkinson's Disease Progression by Noninvasive Speech Tests\". IEEE TBME, 57(4), 884-893.")
    md.append("")

    return "\n".join(md)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SteadyVox – Multi‑Dataset Evaluation")
    print("  Research screening tool only — not a medical diagnosis.")
    print("=" * 60)

    all_rows = []

    # Classification
    for ds in ["Oxford", "Istanbul"]:
        rows = evaluate_classification(ds)
        all_rows.extend(rows)

    # Regression
    reg_rows = evaluate_regression("Telemonitoring")
    all_rows.extend(reg_rows)

    if not all_rows:
        print("\n  ✗ No models found. Run ml/train.py first.")
        sys.exit(1)

    # Generate comparison markdown
    md = generate_markdown(all_rows)
    output_path = RESULTS_DIR / "comparison.md"
    with open(output_path, "w") as f:
        f.write(md)
    print(f"\n  Comparison table saved → {output_path}")

    # Also save as JSON
    json_path = RESULTS_DIR / "comparison.json"
    with open(json_path, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"  Raw results saved → {json_path}")

    print("\n" + "=" * 60)
    print("  Evaluation complete.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
