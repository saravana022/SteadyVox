#!/usr/bin/env python3
"""Exploratory Data Analysis for the three Parkinson's disease datasets.

Reports:
  • Schema & dtypes for each dataset
  • Class balance (healthy vs PD) for classification sets
  • Target distribution for regression set
  • Missing value summary
  • Feature overlap across datasets (common vs dataset‑specific)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def report_schema(df: pd.DataFrame, name: str) -> None:
    section(f"Schema: {name}")
    print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\n  {'Column':<45} {'Dtype':<15} {'Non‑Null':<10} {'Null':<6}")
    print(f"  {'─'*45} {'─'*15} {'─'*10} {'─'*6}")
    for col in df.columns:
        nn = df[col].notna().sum()
        nl = df[col].isna().sum()
        print(f"  {col:<45} {str(df[col].dtype):<15} {nn:<10} {nl:<6}")


def report_class_balance(df: pd.DataFrame, label_col: str, name: str) -> None:
    section(f"Class Balance: {name} (label={label_col})")
    if label_col not in df.columns:
        print(f"  ⚠ Column '{label_col}' not found – skipping.")
        return
    counts = df[label_col].value_counts().sort_index()
    total = len(df)
    for val, cnt in counts.items():
        pct = cnt / total * 100
        print(f"  {val:>10}  →  {cnt:>5}  ({pct:.1f}%)")
    print(f"  {'Total':<10}     {total:>5}")


def report_missing(df: pd.DataFrame, name: str) -> None:
    section(f"Missing Values: {name}")
    missing = df.isnull().sum()
    has_missing = missing[missing > 0]
    if has_missing.empty:
        print("  No missing values ✓")
    else:
        for col, cnt in has_missing.items():
            print(f"  {col:<45} {cnt:>5} missing ({cnt/len(df)*100:.1f}%)")


def report_target_distribution(df: pd.DataFrame, target_cols: list, name: str) -> None:
    section(f"Target Distribution: {name}")
    for col in target_cols:
        if col in df.columns:
            print(f"\n  {col}:")
            print(f"    mean   = {df[col].mean():.3f}")
            print(f"    std    = {df[col].std():.3f}")
            print(f"    min    = {df[col].min():.3f}")
            print(f"    25%    = {df[col].quantile(0.25):.3f}")
            print(f"    median = {df[col].median():.3f}")
            print(f"    75%    = {df[col].quantile(0.75):.3f}")
            print(f"    max    = {df[col].max():.3f}")


# ---------------------------------------------------------------------------
# Feature name normaliser (lowercase, strip whitespace)
# ---------------------------------------------------------------------------

def normalise_feature_names(columns):
    """Return a set of lowercased, stripped column names."""
    return {c.strip().lower() for c in columns}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SteadyVox – Exploratory Data Analysis")
    print("=" * 60)

    # ── Load datasets ─────────────────────────────────────────────────
    oxford_path = DATA_DIR / "oxford" / "parkinsons.csv"
    istanbul_path = DATA_DIR / "istanbul" / "parkinsons_classification.csv"
    telemonitoring_path = DATA_DIR / "telemonitoring" / "parkinsons_telemonitoring.csv"

    datasets = {}
    for name, path in [("Oxford", oxford_path), ("Istanbul", istanbul_path),
                        ("Telemonitoring", telemonitoring_path)]:
        if path.exists():
            df = pd.read_csv(path)
            datasets[name] = df
            print(f"\n  ✓ Loaded {name}: {df.shape}")
        else:
            print(f"\n  ✗ {name} not found at {path}")

    if not datasets:
        print("\n  No datasets found. Run scripts/download_datasets.py first.")
        sys.exit(1)

    # ── Schema reports ────────────────────────────────────────────────
    for name, df in datasets.items():
        report_schema(df, name)

    # ── Class balance (classification sets) ───────────────────────────
    if "Oxford" in datasets:
        report_class_balance(datasets["Oxford"], "status", "Oxford")
    if "Istanbul" in datasets:
        # Try common label column names
        for label_col in ["class", "Class", "status", "target", "label"]:
            if label_col in datasets["Istanbul"].columns:
                report_class_balance(datasets["Istanbul"], label_col, "Istanbul")
                break
        else:
            print("\n  ⚠ Istanbul: could not identify label column.")
            print(f"    Columns: {list(datasets['Istanbul'].columns)}")

    # ── Regression target distribution ────────────────────────────────
    if "Telemonitoring" in datasets:
        report_target_distribution(
            datasets["Telemonitoring"],
            ["motor_UPDRS", "total_UPDRS"],
            "Telemonitoring",
        )

    # ── Missing values ────────────────────────────────────────────────
    for name, df in datasets.items():
        report_missing(df, name)

    # ── Feature overlap analysis ──────────────────────────────────────
    section("Feature Overlap Analysis")

    feature_sets = {}
    for name, df in datasets.items():
        feature_sets[name] = normalise_feature_names(df.columns)

    names = list(feature_sets.keys())
    if len(names) >= 2:
        # Pairwise overlap
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                shared = feature_sets[names[i]] & feature_sets[names[j]]
                print(f"\n  {names[i]} ∩ {names[j]}: {len(shared)} shared features")
                if shared:
                    for f in sorted(shared):
                        print(f"    • {f}")

    if len(names) >= 3:
        # Triple intersection
        common_all = feature_sets[names[0]]
        for n in names[1:]:
            common_all = common_all & feature_sets[n]
        print(f"\n  ───── Common across ALL three datasets: {len(common_all)} features ─────")
        if common_all:
            for f in sorted(common_all):
                print(f"    • {f}")
        else:
            print("    (none)")

    # Dataset-specific features
    section("Dataset‑Specific Features")
    for name in names:
        others = set()
        for other_name in names:
            if other_name != name:
                others |= feature_sets[other_name]
        unique = feature_sets[name] - others
        print(f"\n  {name}‑only ({len(unique)} features):")
        for f in sorted(unique):
            print(f"    • {f}")

    # ── Summary of key voice features across datasets ─────────────────
    section("Key Voice Feature Presence")
    key_features = [
        "jitter", "shimmer", "hnr", "nhr",
        "fo", "fhi", "flo", "pitch",
        "rpde", "dfa", "ppe", "spread1", "spread2", "d2",
    ]
    print(f"\n  {'Feature':<20}", end="")
    for name in names:
        print(f"  {name:<15}", end="")
    print()
    print(f"  {'─'*20}", end="")
    for _ in names:
        print(f"  {'─'*15}", end="")
    print()

    for feat in key_features:
        print(f"  {feat:<20}", end="")
        for name in names:
            found = any(feat in col for col in feature_sets[name])
            mark = "✓" if found else "✗"
            print(f"  {mark:<15}", end="")
        print()

    print("\n" + "=" * 60)
    print("  EDA complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
