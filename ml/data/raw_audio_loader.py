#!/usr/bin/env python3
"""Dataset Loader and Cross-Dataset Evaluator for Raw Audio Datasets.

Supports loading raw acoustic phonations (e.g. Italian Parkinson's Voice and Speech,
PC-GITA, MDVR-KCL, mPower, or local audio directories), extracting the standard 16
Praat MDVP acoustic features using SteadyVox's extraction pipeline, and performing
cross-dataset evaluation.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import joblib
import numpy as np
import pandas as pd
import soundfile as sf
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.preprocessing.audio_cleaning import load_audio, normalize_audio
from ml.preprocessing.feature_extraction import extract_biomarkers

PRAAT_FEATURE_NAMES = [
    "MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)", "MDVP:Jitter(Abs)", "MDVP:RAP", "MDVP:PPQ", "Jitter:DDP",
    "MDVP:Shimmer", "MDVP:Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5", "MDVP:APQ", "Shimmer:DDA",
    "NHR", "HNR"
]


class RawAudioDatasetLoader:
    """Loads raw phonation audio datasets and extracts standardized features."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract_features_from_audio(self, waveform: np.ndarray, sr: int) -> np.ndarray:
        """Extracts the 16 Praat MDVP acoustic features from an audio array."""
        b = extract_biomarkers(waveform, sr=sr)
        f0 = max(float(b.f0_mean), 65.0)
        f0_max = max(float(b.f0_max), f0)
        f0_min = min(float(b.f0_min), f0) if b.f0_min > 0 else f0
        j_pct = max(float(b.jitter_local_percent), 0.001) / 100.0
        j_abs = j_pct / f0
        rap = float(b.jitter_rap_percent) / 100.0
        ppq = float(b.jitter_ppq5_percent) / 100.0
        ddp = 3.0 * rap
        shm = max(float(b.shimmer_local_percent), 0.01) / 100.0
        shm_db = float(b.shimmer_local_db)
        apq3 = float(b.shimmer_apq3_percent) / 100.0
        apq5 = float(b.shimmer_apq5_percent) / 100.0
        apq = (apq3 + apq5) / 2.0
        dda = 3.0 * apq3
        hnr = float(b.hnr_mean_db)
        nhr = 10.0 ** (-max(hnr, 1.0) / 10.0)

        return np.array([
            f0, f0_max, f0_min,
            j_pct, j_abs, rap, ppq, ddp,
            shm, shm_db, apq3, apq5, apq, dda,
            nhr, hnr
        ], dtype=np.float32)

    def load_dataset_from_directory(
        self,
        base_dir: Path,
        healthy_subdir: str = "healthy",
        pd_subdir: str = "parkinsons",
        max_samples_per_class: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Loads audio files from class subdirectories and extracts features."""
        base_path = Path(base_dir)
        h_dir = base_path / healthy_subdir
        pd_dir = base_path / pd_subdir

        X_list, y_list, filenames = [], [], []

        for p in (sorted(list(h_dir.glob("*.wav")))[:max_samples_per_class] if h_dir.exists() else []):
            try:
                wave, sr = sf.read(str(p))
                if wave.ndim > 1:
                    wave = np.mean(wave, axis=1)
                feats = self.extract_features_from_audio(wave.astype(np.float32), sr=sr)
                X_list.append(feats)
                y_list.append(0)
                filenames.append(p.name)
            except Exception as e:
                print(f"Skipping {p.name}: {e}")

        for p in (sorted(list(pd_dir.glob("*.wav")))[:max_samples_per_class] if pd_dir.exists() else []):
            try:
                wave, sr = sf.read(str(p))
                if wave.ndim > 1:
                    wave = np.mean(wave, axis=1)
                feats = self.extract_features_from_audio(wave.astype(np.float32), sr=sr)
                X_list.append(feats)
                y_list.append(1)
                filenames.append(p.name)
            except Exception as e:
                print(f"Skipping {p.name}: {e}")

        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int64), filenames


def evaluate_cross_dataset(model_pkg_path: str = "ml/saved_models/calibrated_acoustic_model.joblib", test_audio_dir: str = "ml/data/processed/test"):
    """Evaluates the trained Oxford model on an external raw audio dataset."""
    pkg = joblib.load(model_pkg_path)
    model = pkg["model"]
    scaler = pkg["scaler"]
    calibrator = pkg["calibrator"]

    loader = RawAudioDatasetLoader()
    X_test, y_test, filenames = loader.load_dataset_from_directory(Path(test_audio_dir), max_samples_per_class=100)

    if len(X_test) == 0:
        print("No test files found for cross-dataset evaluation.")
        return

    from scipy.special import logit
    X_sc = scaler.transform(X_test)
    raw_probs = model.predict_proba(X_sc)[:, 1]
    logits = logit(np.clip(raw_probs, 1e-4, 1.0 - 1e-4)).reshape(-1, 1)
    cal_probs = calibrator.predict_proba(logits)[:, 1]

    auc = roc_auc_score(y_test, cal_probs)
    pr_auc = average_precision_score(y_test, cal_probs)

    pred_elevated = (cal_probs > 0.60).astype(int)
    cm = confusion_matrix(y_test, pred_elevated)
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp)
    sens = tp / (tp + fn)

    print("=" * 80)
    print(f" CROSS-DATASET EVALUATION ({len(X_test)} samples)")
    print("=" * 80)
    print(f"ROC-AUC: {auc:.4f} | PR-AUC: {pr_auc:.4f}")
    print(f"Specificity (>0.60): {spec*100:.1f}% ({tn}/{tn+fp})")
    print(f"Sensitivity (>0.60): {sens*100:.1f}% ({tp}/{tp+fn})")
    print(f"Balanced Accuracy: {((spec+sens)/2)*100:.1f}%")
    print(f"Confusion Matrix:\n{cm}")
    print("=" * 80)


if __name__ == "__main__":
    evaluate_cross_dataset()
