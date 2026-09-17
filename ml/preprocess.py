#!/usr/bin/env python3
"""Preprocessing pipeline for the three Parkinson's disease datasets.

Tasks:
  1. Standardise column names across datasets.
  2. Keep datasets separate (no merging) – each gets its own train/test split.
  3. Classification datasets (Oxford, Istanbul): stratified train/test split.
  4. Regression dataset (Telemonitoring): random train/test split.
  5. Fit StandardScaler per dataset on training split only; save as .joblib.
  6. Persist splits as .npz files under data/<dataset>/splits/.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "ml" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
TEST_SIZE = 0.2

# ---------------------------------------------------------------------------
# Column name standardisation maps
# ---------------------------------------------------------------------------

OXFORD_RENAME = {
    "MDVP:Fo(Hz)": "fo_hz",
    "MDVP:Fhi(Hz)": "fhi_hz",
    "MDVP:Flo(Hz)": "flo_hz",
    "MDVP:Jitter(%)": "jitter_pct",
    "MDVP:Jitter(Abs)": "jitter_abs",
    "MDVP:RAP": "jitter_rap",
    "MDVP:PPQ": "jitter_ppq",
    "Jitter:DDP": "jitter_ddp",
    "MDVP:Shimmer": "shimmer",
    "MDVP:Shimmer(dB)": "shimmer_db",
    "Shimmer:APQ3": "shimmer_apq3",
    "Shimmer:APQ5": "shimmer_apq5",
    "MDVP:APQ": "shimmer_apq",
    "Shimmer:DDA": "shimmer_dda",
    "NHR": "nhr",
    "HNR": "hnr",
    "RPDE": "rpde",
    "DFA": "dfa",
    "spread1": "spread1",
    "spread2": "spread2",
    "D2": "d2",
    "PPE": "ppe",
    "status": "status",
    "name": "name",
}

# Telemonitoring has similar but slightly different columns
TELEMONITORING_RENAME = {
    "subject#": "subject_id",
    "age": "age",
    "sex": "sex",
    "test_time": "test_time",
    "motor_UPDRS": "motor_updrs",
    "total_UPDRS": "total_updrs",
    "Jitter(%)": "jitter_pct",
    "Jitter(Abs)": "jitter_abs",
    "Jitter:RAP": "jitter_rap",
    "Jitter:PPQ5": "jitter_ppq5",
    "Jitter:DDP": "jitter_ddp",
    "Shimmer": "shimmer",
    "Shimmer(dB)": "shimmer_db",
    "Shimmer:APQ3": "shimmer_apq3",
    "Shimmer:APQ5": "shimmer_apq5",
    "Shimmer:APQ11": "shimmer_apq11",
    "Shimmer:DDA": "shimmer_dda",
    "NHR": "nhr",
    "HNR": "hnr",
    "RPDE": "rpde",
    "DFA": "dfa",
    "PPE": "ppe",
}


def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ---------------------------------------------------------------------------
# Oxford preprocessing
# ---------------------------------------------------------------------------

def preprocess_oxford():
    section("Preprocessing Oxford Dataset")
    path = DATA_DIR / "oxford" / "parkinsons.csv"
    if not path.exists():
        print(f"  ✗ Not found: {path}")
        return None
    df = pd.read_csv(path)

    # Rename columns
    df = df.rename(columns=OXFORD_RENAME)

    # Drop the name column (patient identifier, not a feature)
    if "name" in df.columns:
        df = df.drop(columns=["name"])

    # Separate features and label
    label_col = "status"
    feature_cols = [c for c in df.columns if c != label_col]
    X = df[feature_cols].values.astype(np.float32)
    y = df[label_col].values.astype(np.int64)

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)

    # Save
    split_dir = DATA_DIR / "oxford" / "splits"
    split_dir.mkdir(exist_ok=True)
    np.savez(split_dir / "train.npz", X=X_train, y=y_train)
    np.savez(split_dir / "test.npz", X=X_test, y=y_test)
    joblib.dump(scaler, MODEL_DIR / "oxford_scaler.joblib")

    # Save feature names
    with open(split_dir / "feature_names.json", "w") as f:
        json.dump(feature_cols, f, indent=2)

    print(f"  Features: {len(feature_cols)}")
    print(f"  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
    print(f"  Label distribution (train): {dict(zip(*np.unique(y_train, return_counts=True)))}")
    print(f"  Label distribution (test):  {dict(zip(*np.unique(y_test, return_counts=True)))}")
    print(f"  Scaler saved → {MODEL_DIR / 'oxford_scaler.joblib'}")
    return feature_cols


# ---------------------------------------------------------------------------
# Istanbul preprocessing
# ---------------------------------------------------------------------------

def preprocess_istanbul():
    section("Preprocessing Istanbul Dataset")
    path = DATA_DIR / "istanbul" / "parkinsons_classification.csv"
    if not path.exists():
        print(f"  ✗ Not found: {path}")
        return None

    df = pd.read_csv(path)
    if len(df) == 0:
        print("  ⚠ Dataset is empty (placeholder). Skipping.")
        return None

    # Lowercase columns for easier handling
    df.columns = [c.strip().lower() for c in df.columns]

    # Identify label column
    label_col = None
    for candidate in ["class", "status", "target", "label"]:
        if candidate in df.columns:
            label_col = candidate
            break
    if label_col is None:
        print(f"  ⚠ Cannot identify label column. Columns: {list(df.columns)}")
        return None

    # Drop ID column if present
    for id_col in ["id", "subject_id", "subject#"]:
        if id_col in df.columns:
            df = df.drop(columns=[id_col])

    feature_cols = [c for c in df.columns if c != label_col]

    # Ensure all feature columns are numeric
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()

    X = df[feature_cols].values.astype(np.float32)
    y = df[label_col].values.astype(np.int64)

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)

    # Save
    split_dir = DATA_DIR / "istanbul" / "splits"
    split_dir.mkdir(exist_ok=True)
    np.savez(split_dir / "train.npz", X=X_train, y=y_train)
    np.savez(split_dir / "test.npz", X=X_test, y=y_test)
    joblib.dump(scaler, MODEL_DIR / "istanbul_scaler.joblib")

    with open(split_dir / "feature_names.json", "w") as f:
        json.dump(feature_cols, f, indent=2)

    print(f"  Features: {len(feature_cols)}")
    print(f"  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
    print(f"  Label distribution (train): {dict(zip(*np.unique(y_train, return_counts=True)))}")
    print(f"  Label distribution (test):  {dict(zip(*np.unique(y_test, return_counts=True)))}")
    print(f"  Scaler saved → {MODEL_DIR / 'istanbul_scaler.joblib'}")
    return feature_cols


# ---------------------------------------------------------------------------
# Telemonitoring preprocessing
# ---------------------------------------------------------------------------

def preprocess_telemonitoring():
    section("Preprocessing Telemonitoring Dataset")
    path = DATA_DIR / "telemonitoring" / "parkinsons_telemonitoring.csv"
    if not path.exists():
        print(f"  ✗ Not found: {path}")
        return None

    df = pd.read_csv(path)

    # Rename columns
    rename_map = {}
    for orig, new in TELEMONITORING_RENAME.items():
        if orig in df.columns:
            rename_map[orig] = new
    # Also handle lowercase originals
    for orig, new in TELEMONITORING_RENAME.items():
        if orig.lower() in [c.lower() for c in df.columns]:
            matching = [c for c in df.columns if c.lower() == orig.lower()]
            if matching:
                rename_map[matching[0]] = new
    df = df.rename(columns=rename_map)

    # Target columns for regression
    target_cols = []
    for t in ["motor_updrs", "total_updrs"]:
        if t in df.columns:
            target_cols.append(t)
    if not target_cols:
        print(f"  ⚠ Cannot find target columns. Columns: {list(df.columns)}")
        return None

    # Drop non-feature columns
    drop_cols = ["subject_id", "age", "sex", "test_time"] + target_cols
    feature_cols = [c for c in df.columns if c not in drop_cols]

    # Ensure numeric
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=feature_cols + target_cols)

    X = df[feature_cols].values.astype(np.float32)
    y = df[target_cols].values.astype(np.float32)  # multi‑output regression

    # Random split (regression – no stratification)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED
    )

    # Scale features only (not targets)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)

    # Save
    split_dir = DATA_DIR / "telemonitoring" / "splits"
    split_dir.mkdir(exist_ok=True)
    np.savez(split_dir / "train.npz", X=X_train, y=y_train)
    np.savez(split_dir / "test.npz", X=X_test, y=y_test)
    joblib.dump(scaler, MODEL_DIR / "telemonitoring_scaler.joblib")

    with open(split_dir / "feature_names.json", "w") as f:
        json.dump(feature_cols, f, indent=2)
    with open(split_dir / "target_names.json", "w") as f:
        json.dump(target_cols, f, indent=2)

    print(f"  Features: {len(feature_cols)}")
    print(f"  Targets: {target_cols}")
    print(f"  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
    print(f"  Target stats (train): mean={y_train.mean(axis=0)}, std={y_train.std(axis=0)}")
    print(f"  Scaler saved → {MODEL_DIR / 'telemonitoring_scaler.joblib'}")
    return feature_cols


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SteadyVox – Data Preprocessing Pipeline")
    print("=" * 60)

    oxford_feats = preprocess_oxford()
    istanbul_feats = preprocess_istanbul()
    telemonitoring_feats = preprocess_telemonitoring()

    # Summary
    section("Preprocessing Summary")
    datasets_processed = 0
    for name, feats in [("Oxford", oxford_feats), ("Istanbul", istanbul_feats),
                         ("Telemonitoring", telemonitoring_feats)]:
        if feats is not None:
            print(f"  ✓ {name}: {len(feats)} features")
            datasets_processed += 1
        else:
            print(f"  ✗ {name}: skipped")

    print(f"\n  {datasets_processed}/3 datasets preprocessed successfully.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
