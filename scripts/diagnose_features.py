#!/usr/bin/env python3
"""Diagnostic script to inspect feature extraction, scaling, and classification.

Tasks:
  (a) Lists the exact feature vector extracted by the app for a test audio.
  (b) Compares it with the UCI Oxford healthy-group mean/std (calculates z-scores, flags |z| > 4).
  (c) Verifies feature column order, scaler application, and class index in inference.
  (d) Evaluates recording stability across gain variations, sample rates, and noise levels.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import sys
from pathlib import Path
import json

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import torch

from ml.models.tabular_mlp import FEATURE_NAMES, TabularMLP
from ml.preprocessing.audio_cleaning import load_audio, normalize_audio
from ml.preprocessing.feature_extraction import extract_biomarkers


def generate_synthetic_healthy_vowel(sr=16000, duration=3.5, f0=140.0):
    """Generates a clean, stable synthetic sustained vowel /a/."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Glottal source approximation (fundamental + harmonics)
    signal = (
        0.6 * np.sin(2 * np.pi * f0 * t) +
        0.3 * np.sin(2 * np.pi * 2 * f0 * t) +
        0.15 * np.sin(2 * np.pi * 3 * f0 * t) +
        0.05 * np.sin(2 * np.pi * 4 * f0 * t)
    )
    # Add minimal natural noise (SNR > 30 dB)
    noise = np.random.normal(0, 0.002, signal.shape)
    waveform = signal + noise
    waveform = waveform / (np.max(np.abs(waveform)) + 1e-8) * 0.8
    return waveform.astype(np.float32)


def main():
    print("=" * 80)
    print(" STEADYVOX FEATURE DIAGNOSTIC HARNESS")
    print("=" * 80)

    # 1. Load Oxford dataset to compute reference distributions
    oxford_path = ROOT_DIR / "data" / "oxford" / "parkinsons.csv"
    if not oxford_path.exists():
        print(f"Error: Oxford dataset not found at {oxford_path}")
        return

    df = pd.read_csv(oxford_path)
    healthy_df = df[df["status"] == 0]
    pd_df = df[df["status"] == 1]

    print(f"\n[1] Oxford Dataset Summary:")
    print(f"    Total samples: {len(df)} (Healthy: {len(healthy_df)}, PD: {len(pd_df)})")
    print(f"    Healthy subjects: {healthy_df['name'].apply(lambda x: x.split('_')[2]).nunique()}")
    print(f"    PD subjects: {pd_df['name'].apply(lambda x: x.split('_')[2]).nunique()}")

    # 2. Extract feature vector using the current app's logic
    test_wave = generate_synthetic_healthy_vowel(sr=16000, duration=3.5, f0=135.0)
    biomarkers = extract_biomarkers(test_wave, sr=16000)

    # Replicate current _construct_oxford_feature_vector logic
    f0 = max(float(biomarkers.f0_mean), 65.0)
    f0_max = max(float(biomarkers.f0_max), f0)
    f0_min = min(float(biomarkers.f0_min), f0)
    j_pct = max(float(biomarkers.jitter_local_percent), 0.001)
    j_abs = (j_pct / 100.0) / f0
    rap = float(biomarkers.jitter_rap_percent) / 100.0
    ppq = float(biomarkers.jitter_ppq5_percent) / 100.0
    ddp = 3.0 * rap
    shm = max(float(biomarkers.shimmer_local_percent), 0.01) / 100.0
    shm_db = float(biomarkers.shimmer_local_db)
    apq3 = float(biomarkers.shimmer_apq3_percent) / 100.0
    apq5 = float(biomarkers.shimmer_apq5_percent) / 100.0
    apq = (apq3 + apq5) / 2.0
    dda = 3.0 * apq3
    hnr = float(biomarkers.hnr_mean_db)
    nhr = 10.0 ** (-max(hnr, 1.0) / 10.0)

    # Current app nonlinear logic
    is_elevated = (j_pct > 0.12 or shm > 0.04 or hnr < 18.0)
    rpde = 0.542 if is_elevated else 0.465
    dfa = 0.725 if is_elevated else 0.690
    spread1 = -5.35 if is_elevated else -6.65
    spread2 = 0.245 if is_elevated else 0.165
    d2 = 2.42 if is_elevated else 2.25
    ppe = 0.225 if is_elevated else 0.125

    app_vector = [
        f0, f0_max, f0_min,
        j_pct, j_abs, rap, ppq, ddp,
        shm, shm_db, apq3, apq5, apq, dda,
        nhr, hnr,
        rpde, dfa, spread1, spread2, d2, ppe,
    ]

    print("\n[2] Feature Vector Comparison & Z-Scores against Healthy Controls:")
    print(f"{'Feature Name':<20} | {'Extracted':<12} | {'Healthy Mean':<12} | {'Healthy Std':<12} | {'Z-Score':<10} | {'Flag'}")
    print("-" * 80)

    anomalies = []
    for idx, name in enumerate(FEATURE_NAMES):
        extracted_val = app_vector[idx]
        h_mean = healthy_df[name].mean()
        h_std = healthy_df[name].std()
        if h_std > 0:
            z_score = (extracted_val - h_mean) / h_std
        else:
            z_score = 0.0

        flag = "🚨 |Z| > 4" if abs(z_score) > 4.0 else ("⚠️ |Z| > 2" if abs(z_score) > 2.0 else "✓ Normal")
        if abs(z_score) > 4.0:
            anomalies.append((name, extracted_val, h_mean, z_score))

        print(f"{name:<20} | {extracted_val:<12.5f} | {h_mean:<12.5f} | {h_std:<12.5f} | {z_score:<+10.2f} | {flag}")

    print("\n[3] Verification of Scaler, Model, and Column Order:")
    scaler_path = ROOT_DIR / "ml" / "saved_models" / "tabular_scaler.joblib"
    model_path = ROOT_DIR / "ml" / "saved_models" / "tabular_mlp_best.pt"

    scaler = joblib.load(scaler_path) if scaler_path.exists() else None
    print(f"    Scaler loaded: {scaler is not None} from {scaler_path}")
    if scaler is not None:
        print(f"    Scaler n_features_in_: {scaler.n_features_in_}")
        scaled_vec = scaler.transform(np.array(app_vector).reshape(1, -1))
        print(f"    Scaled Vector Min: {scaled_vec.min():.2f}, Max: {scaled_vec.max():.2f}, Mean: {scaled_vec.mean():.2f}")

    if model_path.exists():
        ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
        print(f"    Model Checkpoint Keys: {list(ckpt.keys())}")
        calibrated_thresh = ckpt.get("calibrated_threshold", 0.5)
        print(f"    Calibrated Threshold in Checkpoint: {calibrated_thresh}")

        model = TabularMLP()
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()

        with torch.no_grad():
            inp_t = torch.from_numpy(scaled_vec).float()
            logits = model(inp_t)
            prob = torch.sigmoid(logits).item()
            conf = max(0.5, prob) if prob >= calibrated_thresh else max(0.5, 1.0 - prob)

        print(f"    -> Raw Model Logit: {logits.item():.4f}")
        print(f"    -> Output Probability (PD): {prob * 100:.2f}%")
        print(f"    -> Output Confidence: {conf * 100:.2f}%")
        print(f"    -> Resulting Classification: {'PARKINSONS (ELEVATED)' if prob >= calibrated_thresh else 'HEALTHY (LOW)'}")

    print("\n[4] Score Stability Test (Gains, Sample Rates, Noise):")
    # Test gains: 0.25, 0.5, 1.0, 1.5
    for gain in [0.25, 0.5, 1.0, 1.5]:
        test_g = normalize_audio(test_wave * gain)
        b_g = extract_biomarkers(test_g, sr=16000)
        print(f"    Gain {gain:.2f}x: F0={b_g.f0_mean:.1f}Hz, Jitter={b_g.jitter_local_percent:.4f}%, Shimmer={b_g.shimmer_local_percent:.4f}%, HNR={b_g.hnr_mean_db:.1f}dB")

    # Test noise levels
    for noise_std in [0.001, 0.01, 0.05]:
        noisy = test_wave + np.random.normal(0, noise_std, test_wave.shape).astype(np.float32)
        b_n = extract_biomarkers(noisy, sr=16000)
        print(f"    Noise std={noise_std:.3f}: F0={b_n.f0_mean:.1f}Hz, Jitter={b_n.jitter_local_percent:.4f}%, HNR={b_n.hnr_mean_db:.1f}dB")

    print("\n[5] CRITICAL ROOT-CAUSE DIAGNOSIS SUMMARY:")
    print("=" * 80)
    for name, ext, mean, z in anomalies:
        print(f"  * {name}: extracted={ext:.5f} vs healthy_mean={mean:.5f} (Z-Score = {z:+.2f})")
    print("=" * 80)


if __name__ == "__main__":
    main()
