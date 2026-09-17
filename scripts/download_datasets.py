#!/usr/bin/env python3
"""Download three Parkinson's disease datasets from UCI ML Repository.

Datasets:
1. Oxford Parkinson's Disease Detection (ID 174)
2. Parkinson's Disease Classification – Istanbul (ID 470)
3. Parkinson's Telemonitoring (ID 189)

Uses `ucimlrepo` package first; falls back to direct CSV URLs on failure.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

OXFORD_DIR = DATA_DIR / "oxford"
ISTANBUL_DIR = DATA_DIR / "istanbul"
TELEMONITORING_DIR = DATA_DIR / "telemonitoring"

for d in [OXFORD_DIR, ISTANBUL_DIR, TELEMONITORING_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Fallback URLs (raw CSV links hosted on UCI / GitHub mirrors)
# ---------------------------------------------------------------------------
FALLBACK_URLS = {
    "oxford": "https://archive.ics.uci.edu/ml/machine-learning-databases/parkinsons/parkinsons.data",
    "telemonitoring": "https://archive.ics.uci.edu/ml/machine-learning-databases/parkinsons/telemonitoring/parkinsons_updrs.data",
}


def _save_and_report(df: pd.DataFrame, path: Path, label: str) -> None:
    df.to_csv(path, index=False)
    print(f"  ✓ {label}: {df.shape[0]} rows × {df.shape[1]} columns → {path}")


# ── Oxford (ID 174) ────────────────────────────────────────────────────────
def download_oxford():
    print("\n[1/3] Oxford Parkinson's Disease Detection Dataset")
    dest = OXFORD_DIR / "parkinsons.csv"

    # Check if we already have it in the project
    existing = PROJECT_ROOT / "ml" / "data" / "real" / "parkinsons.data"
    if existing.exists():
        print(f"  → Found local copy at {existing}")
        df = pd.read_csv(existing)
        _save_and_report(df, dest, "Oxford")
        return df

    # Try ucimlrepo first
    try:
        from ucimlrepo import fetch_ucirepo  # type: ignore
        dataset = fetch_ucirepo(id=174)
        features = dataset.data.features
        targets = dataset.data.targets
        df = pd.concat([features, targets], axis=1)
        _save_and_report(df, dest, "Oxford (ucimlrepo)")
        return df
    except Exception as e:
        print(f"  ⚠ ucimlrepo failed ({e}), trying direct URL …")

    # Fallback
    try:
        df = pd.read_csv(FALLBACK_URLS["oxford"])
        _save_and_report(df, dest, "Oxford (URL)")
        return df
    except Exception as e2:
        print(f"  ✗ Direct URL also failed: {e2}")
        sys.exit(1)


# ── Istanbul / Cerrahpaşa (ID 470) ────────────────────────────────────────
def download_istanbul():
    print("\n[2/3] Parkinson's Disease Classification Dataset (Istanbul)")
    dest = ISTANBUL_DIR / "parkinsons_classification.csv"

    # Try ucimlrepo first
    try:
        from ucimlrepo import fetch_ucirepo  # type: ignore
        dataset = fetch_ucirepo(id=470)
        features = dataset.data.features
        targets = dataset.data.targets
        df = pd.concat([features, targets], axis=1)
        _save_and_report(df, dest, "Istanbul (ucimlrepo)")
        return df
    except Exception as e:
        print(f"  ⚠ ucimlrepo failed ({e}), trying direct URL …")

    # Fallback — multiple baseline vocal features + UPDRS features
    # This dataset is hosted as a zip; try alternative CSV URL
    fallback_url = (
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00470/"
        "Parkinson_Multiple_Sound_Recording.rar"
    )
    try:
        # If rar, download and extract
        import requests
        import io
        import zipfile

        # Try CSV export first
        csv_url = (
            "https://archive.ics.uci.edu/static/public/470/"
            "parkinsons+disease+classification.zip"
        )
        r = requests.get(csv_url, timeout=60)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        csv_names = [n for n in z.namelist() if n.endswith(".csv") or n.endswith(".data") or n.endswith(".txt")]
        print(f"  → Archive contents: {z.namelist()}")
        if csv_names:
            with z.open(csv_names[0]) as f:
                df = pd.read_csv(f)
            _save_and_report(df, dest, "Istanbul (zip)")
            return df
        else:
            # Try all text-like files
            for name in z.namelist():
                try:
                    with z.open(name) as f:
                        df = pd.read_csv(f)
                    if len(df) > 10:
                        _save_and_report(df, dest, f"Istanbul ({name})")
                        return df
                except Exception:
                    continue
            print("  ✗ Could not parse any file in the archive.")
    except Exception as e2:
        print(f"  ✗ Fallback also failed: {e2}")

    # Final fallback: generate a placeholder CSV with the known schema
    print("  ⚠ Creating placeholder – you may need to manually download this dataset.")
    cols = [
        "id", "gender", "PPE", "DFA", "RPDE", "numPulses", "numPeriodsPulses",
        "meanPeriodPulses", "stdDevPeriodPulses", "locPctJitter", "locAbsJitter",
        "rapJitter", "ppq5Jitter", "ddpJitter", "locShimmer", "locDbShimmer",
        "apq3Shimmer", "apq5Shimmer", "apq11Shimmer", "ddaShimmer",
        "meanAutoCorrHarmonicity", "meanNoiseToHarmHarmonicity",
        "meanHarmToNoiseHarmonicity", "minIntensity", "maxIntensity",
        "meanIntensity", "minPitch", "maxPitch", "meanPitch",
        "stdDevPitch", "localJitter", "localAbsoluteJitter",
        "rapJitter2", "ppq5Jitter2", "class"
    ]
    df = pd.DataFrame(columns=cols)
    _save_and_report(df, dest, "Istanbul (placeholder)")
    return df


# ── Telemonitoring (ID 189) ───────────────────────────────────────────────
def download_telemonitoring():
    print("\n[3/3] Parkinson's Telemonitoring Dataset")
    dest = TELEMONITORING_DIR / "parkinsons_telemonitoring.csv"

    # Try ucimlrepo first
    try:
        from ucimlrepo import fetch_ucirepo  # type: ignore
        dataset = fetch_ucirepo(id=189)
        features = dataset.data.features
        targets = dataset.data.targets
        df = pd.concat([features, targets], axis=1)
        _save_and_report(df, dest, "Telemonitoring (ucimlrepo)")
        return df
    except Exception as e:
        print(f"  ⚠ ucimlrepo failed ({e}), trying direct URL …")

    # Fallback
    try:
        df = pd.read_csv(FALLBACK_URLS["telemonitoring"])
        _save_and_report(df, dest, "Telemonitoring (URL)")
        return df
    except Exception as e2:
        print(f"  ✗ Direct URL also failed: {e2}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("SteadyVox – Multi‑Dataset Downloader")
    print("=" * 60)

    df_oxford = download_oxford()
    df_istanbul = download_istanbul()
    df_telemonitoring = download_telemonitoring()

    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"  Oxford:         {df_oxford.shape[0]:>6} rows × {df_oxford.shape[1]:>3} cols")
    print(f"  Istanbul:       {df_istanbul.shape[0]:>6} rows × {df_istanbul.shape[1]:>3} cols")
    print(f"  Telemonitoring: {df_telemonitoring.shape[0]:>6} rows × {df_telemonitoring.shape[1]:>3} cols")
    print("=" * 60)
    print("All datasets saved under data/\n")


if __name__ == "__main__":
    main()
