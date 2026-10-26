"""SteadyVox Baseline Latency & Profiling Benchmark.
Measures cold start, warm p50/p95/p99, and per-stage execution times.
"""

import time
import os
import sys
from pathlib import Path
import numpy as np

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, "/home/saravana/SteadyVox")

from backend.app.services.inference import inference_service
from ml.preprocessing.audio_cleaning import preprocess_pipeline
from ml.preprocessing.feature_extraction import extract_biomarkers, extract_model_features
import torch

SAMPLE_WAV = "/home/saravana/SteadyVox/storage/audio/recordings/43bd02f7-f894-49d4-933a-60db8e914dfa.wav"

def run_benchmark():
    with open(SAMPLE_WAV, "rb") as f:
        audio_bytes = f.read()

    print("--- BENCHMARK BASELINE (B0) ---")
    
    # 1. Cold start inference call
    t0 = time.perf_counter()
    res_cold = inference_service.run_screening(audio_bytes, "cold_test.wav")
    cold_ms = (time.perf_counter() - t0) * 1000.0
    print(f"Cold Start Latency: {cold_ms:.2f} ms")

    # 2. Warm iterations (10 runs)
    latencies = []
    stage_times = {"decode_clean": [], "biomarkers": [], "tab_mlp": [], "audio_spec_infer": []}

    for i in range(10):
        t_start = time.perf_counter()
        
        # Sub-stage breakdown
        t_stage0 = time.perf_counter()
        waveform, sr = preprocess_pipeline(audio_bytes, inference_service.audio_config)
        t_stage1 = time.perf_counter()
        
        biomarkers = extract_biomarkers(waveform, sr=sr)
        t_stage2 = time.perf_counter()
        
        tab_vector, _ = inference_service._construct_oxford_feature_vector(biomarkers)
        if inference_service.tabular_scaler is not None:
            tab_scaled = inference_service.tabular_scaler.transform(tab_vector.reshape(1, -1))
        else:
            tab_scaled = tab_vector.reshape(1, -1)
        tab_tensor = torch.from_numpy(tab_scaled).float().to(inference_service.device)
        with torch.no_grad():
            _ = inference_service.tabular_model.predict_proba(tab_tensor)
        t_stage3 = time.perf_counter()
        
        spec_tensor = extract_model_features(waveform, sr=sr, n_mels=128).to(inference_service.device)
        with torch.no_grad():
            _ = inference_service.audio_model.predict_proba(spec_tensor)
        t_stage4 = time.perf_counter()
        
        total_run_ms = (t_stage4 - t_start) * 1000.0
        latencies.append(total_run_ms)
        stage_times["decode_clean"].append((t_stage1 - t_stage0) * 1000.0)
        stage_times["biomarkers"].append((t_stage2 - t_stage1) * 1000.0)
        stage_times["tab_mlp"].append((t_stage3 - t_stage2) * 1000.0)
        stage_times["audio_spec_infer"].append((t_stage4 - t_stage3) * 1000.0)

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"Warm Latency (10 runs):")
    print(f"  p50: {p50:.2f} ms")
    print(f"  p95: {p95:.2f} ms")
    print(f"  p99: {p99:.2f} ms")
    print("Stage breakdown (avg ms):")
    for stage, times in stage_times.items():
        print(f"  {stage}: {np.mean(times):.2f} ms")

if __name__ == "__main__":
    run_benchmark()
