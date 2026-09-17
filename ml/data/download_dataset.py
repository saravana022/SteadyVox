"""SteadyVox Dataset Ingestion and Downloader Utility.

Provides automated ingestion for public voice datasets:
1. Oxford Parkinson's Disease Detection Dataset (Little et al., 2007, UCI ML Repository)
   - 22 acoustic features from sustained phonations of 31 subjects (23 PD, 8 healthy).
2. Italian Parkinson's Voice and Speech Dataset (IEEE DataPort)
   - Graceful fallback with authentication documentation.
3. Local audio directory ingestion with subject-independent splitting.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import logging
import os
import re
import shutil
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("steadyvox.downloader")

UCI_PARKINSONS_URL = "https://archive.ics.uci.edu/static/public/174/parkinsons.zip"
IEEE_ITALIAN_DATASET_URL = "https://ieee-dataport.org/open-access/italian-parkinsons-voice-and-speech"

FEATURE_COLUMNS = [
    "MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)", "MDVP:Jitter(Abs)", "MDVP:RAP", "MDVP:PPQ", "Jitter:DDP",
    "MDVP:Shimmer", "MDVP:Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5", "MDVP:APQ", "Shimmer:DDA",
    "NHR", "HNR", "RPDE", "DFA", "spread1", "spread2", "D2", "PPE"
]


def attempt_italian_parkinsons_download() -> None:
    """Attempts to inspect Italian Parkinson's dataset availability and logs auth requirements."""
    logger.info("Checking Italian Parkinson's Voice & Speech Dataset availability...")
    logger.info("Source: IEEE DataPort (%s)", IEEE_ITALIAN_DATASET_URL)
    try:
        req = urllib.request.Request(
            IEEE_ITALIAN_DATASET_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            logger.info("Italian Parkinson's webpage accessible (HTTP %d).", status)
    except Exception as exc:
        logger.warning("Could not reach IEEE DataPort landing page: %s", exc)

    logger.info(
        "NOTE: The Italian Parkinson's Voice and Speech dataset on IEEE DataPort "
        "requires user account authentication / session cookies to download raw .wav files. "
        "Direct unauthenticated API download is restricted by IEEE DataPort. "
        "Gracefully falling back to the Oxford Parkinson's Disease Detection Dataset (UCI ML Repository)."
    )


def download_uci_parkinsons(
    output_dir: str = "ml/data/real",
    url: str = UCI_PARKINSONS_URL,
    random_state: int = 42
) -> Dict[str, pd.DataFrame]:
    """Downloads and prepares the Oxford Parkinson's Disease Detection Dataset (UCI ML Repository).

    Performs subject-independent stratified train/val/test splitting to prevent data leakage.
    Returns dictionary with 'train', 'val', 'test', and 'full' DataFrames.
    """
    dst = Path(output_dir)
    dst.mkdir(parents=True, exist_ok=True)

    zip_target = dst / "parkinsons.zip"
    data_target = dst / "parkinsons.data"

    # Check local tmp cache first, or download
    cached_tmp = Path("/tmp/parkinsons.zip")
    if not data_target.exists():
        if cached_tmp.exists():
            logger.info("Using cached download from %s", cached_tmp)
            shutil.copy2(cached_tmp, zip_target)
        else:
            logger.info("Downloading Oxford Parkinson's Dataset from %s...", url)
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp, open(zip_target, "wb") as out_f:
                shutil.copyfileobj(resp, out_f)
            logger.info("Downloaded %d bytes to %s", zip_target.stat().st_size, zip_target)

        logger.info("Extracting parkinsons.data from %s...", zip_target)
        with zipfile.ZipFile(zip_target, "r") as zf:
            for member in zf.namelist():
                if member.endswith("parkinsons.data"):
                    with zf.open(member) as src_f, open(data_target, "wb") as out_f:
                        shutil.copyfileobj(src_f, out_f)
                    break

    if not data_target.exists():
        raise FileNotFoundError(f"Failed to find parkinsons.data in {zip_target}")

    df = pd.read_csv(data_target)
    logger.info("Loaded Oxford Parkinson's dataset with %d rows and %d columns", len(df), len(df.columns))

    # Extract subject ID (e.g. phon_R01_S01_1 -> S01)
    df["subject_id"] = df["name"].str.extract(r"_(S\d+)_")[0]
    if df["subject_id"].isna().any():
        df["subject_id"] = df["name"].apply(lambda n: n.split("_")[2] if len(n.split("_")) >= 3 else n)

    num_subjects = df["subject_id"].nunique()
    num_pd = df[df["status"] == 1]["subject_id"].nunique()
    num_healthy = df[df["status"] == 0]["subject_id"].nunique()
    logger.info("Identified %d unique subjects: %d PD (status=1), %d Healthy (status=0)", num_subjects, num_pd, num_healthy)

    # Subject-independent stratified train/val/test split
    # Stage 1: 80% train+val, 20% test (subject-stratified)
    sgkf_outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_state)
    train_val_idx, test_idx = next(sgkf_outer.split(df, df["status"], groups=df["subject_id"]))
    train_val_df = df.iloc[train_val_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)

    # Stage 2: Split train+val into ~75% train, ~25% val (yielding ~60% train, ~20% val, ~20% test overall)
    sgkf_inner = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=random_state)
    train_sub_idx, val_sub_idx = next(sgkf_inner.split(train_val_df, train_val_df["status"], groups=train_val_df["subject_id"]))
    train_df = train_val_df.iloc[train_sub_idx].copy().reset_index(drop=True)
    val_df = train_val_df.iloc[val_sub_idx].copy().reset_index(drop=True)

    train_df["split"] = "train"
    val_df["split"] = "val"
    test_df["split"] = "test"

    # Verify zero subject overlap
    s_train = set(train_df["subject_id"])
    s_val = set(val_df["subject_id"])
    s_test = set(test_df["subject_id"])
    assert len(s_train.intersection(s_val)) == 0, "Subject leakage between train and val!"
    assert len(s_train.intersection(s_test)) == 0, "Subject leakage between train and test!"
    assert len(s_val.intersection(s_test)) == 0, "Subject leakage between val and test!"

    # Save split CSVs
    train_df.to_csv(dst / "train.csv", index=False)
    val_df.to_csv(dst / "val.csv", index=False)
    test_df.to_csv(dst / "test.csv", index=False)
    
    full_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    full_df.to_csv(dst / "full_dataset.csv", index=False)

    logger.info(
        "Splits saved successfully:\n"
        "  - Train: %d samples (%d subjects, %d PD / %d Healthy)\n"
        "  - Val:   %d samples (%d subjects, %d PD / %d Healthy)\n"
        "  - Test:  %d samples (%d subjects, %d PD / %d Healthy)",
        len(train_df), train_df["subject_id"].nunique(),
        train_df[train_df["status"] == 1]["subject_id"].nunique(),
        train_df[train_df["status"] == 0]["subject_id"].nunique(),
        len(val_df), val_df["subject_id"].nunique(),
        val_df[val_df["status"] == 1]["subject_id"].nunique(),
        val_df[val_df["status"] == 0]["subject_id"].nunique(),
        len(test_df), test_df["subject_id"].nunique(),
        test_df[test_df["status"] == 1]["subject_id"].nunique(),
        test_df[test_df["status"] == 0]["subject_id"].nunique(),
    )

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "full": full_df,
    }


def ingest_local_directory(
    source_dir: str,
    output_dir: str = "ml/data/processed",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Optional[pd.DataFrame]:
    """Ingests an existing folder containing subfolders of audio or speaker files."""
    src = Path(source_dir)
    dst = Path(output_dir)
    dst.mkdir(parents=True, exist_ok=True)

    records = []
    for class_name in ["healthy", "parkinsons"]:
        class_dir = src / class_name
        if not class_dir.exists():
            continue
        for audio_file in class_dir.glob("*.wav"):
            speaker_id = audio_file.stem.split("_")[0]
            records.append({
                "source_path": str(audio_file),
                "speaker_id": speaker_id,
                "label": class_name,
                "target": 1 if class_name == "parkinsons" else 0,
            })

    if not records:
        logger.warning("No audio files found in %s. Ensure structure has healthy/ and parkinsons/ subdirectories.", source_dir)
        return None

    df = pd.DataFrame(records)

    gss = GroupShuffleSplit(n_splits=1, train_size=train_ratio, random_state=seed)
    train_idx, temp_idx = next(gss.split(df, groups=df["speaker_id"]))
    train_df = df.iloc[train_idx].copy()
    train_df["split"] = "train"

    temp_df = df.iloc[temp_idx].copy()
    val_split_prop = val_ratio / (1.0 - train_ratio)
    gss_val = GroupShuffleSplit(n_splits=1, train_size=val_split_prop, random_state=seed)
    val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df["speaker_id"]))
    
    val_df = temp_df.iloc[val_idx].copy()
    val_df["split"] = "val"
    test_df = temp_df.iloc[test_idx].copy()
    test_df["split"] = "test"

    combined = pd.concat([train_df, val_df, test_df], ignore_index=True)

    for _, row in combined.iterrows():
        dest_folder = dst / row["split"] / row["label"]
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / Path(row["source_path"]).name
        shutil.copy2(row["source_path"], dest_path)
        row["file_path"] = str(dest_path)

    manifest_path = dst / "dataset_manifest.csv"
    combined.to_csv(manifest_path, index=False)
    logger.info("Ingested and organized %d files into %s", len(combined), output_dir)
    return combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest or download dataset for SteadyVox")
    parser.add_argument(
        "--dataset",
        type=str,
        default="uci",
        choices=["uci", "italian", "all", "local"],
        help="Dataset to fetch/prepare: 'uci' (Oxford Little et al.), 'italian' (check IEEE DataPort), 'all', or 'local'"
    )
    parser.add_argument("--source_dir", type=str, default=None, help="Path to raw audio folder for local ingestion")
    parser.add_argument("--output_dir", type=str, default="ml/data/real", help="Destination directory for processed real data")
    args = parser.parse_args()

    if args.dataset in ["italian", "all"]:
        attempt_italian_parkinsons_download()

    if args.dataset in ["uci", "all"]:
        download_uci_parkinsons(output_dir=args.output_dir)
    elif args.dataset == "local":
        if args.source_dir:
            ingest_local_directory(args.source_dir, args.output_dir)
        else:
            logger.error("--source_dir required for local ingestion.")
