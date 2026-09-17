"""SteadyVox Biophysical Phonation Synthesizer.

Generates realistic sustained vowel phonations (/a/) for healthy controls
and Parkinsonian dysarthria profiles (simulating vocal tremor, elevated jitter,
increased shimmer, and glottal aspiration noise).

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import os
from pathlib import Path
from typing import Tuple, List, Dict
import numpy as np
import scipy.signal as signal
import soundfile as sf
import pandas as pd


def generate_phonation_sample(
    duration: float = 3.0,
    sr: int = 16000,
    is_parkinsons: bool = False,
    base_f0: float = 130.0,
    speaker_jitter_offset: float = 0.0,
    speaker_shimmer_offset: float = 0.0,
    rng: np.random.Generator = None,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Synthesizes a single sustained vowel /a/ phonation with clinical acoustic parameters.
    
    Excitation: liljencrants-fant harmonic glottal source with frequency & cycle perturbation.
    Filter: parallel formant resonators for sustained vowel /a/.
    Pathology: vocal tremor (4.5-6.5 Hz FM/AM), elevated jitter, shimmer, and aspiration noise.
    """
    if rng is None:
        rng = np.random.default_rng()

    num_samples = int(duration * sr)
    time = np.arange(num_samples) / sr

    if is_parkinsons:
        # Parkinson's parameters
        # 1. Vocal tremor: 4.5-6.5 Hz frequency and amplitude modulation
        tremor_rate = rng.uniform(4.5, 6.5)
        tremor_depth_f0 = rng.uniform(2.0, 5.0)     # 2.0 to 5.0 Hz frequency modulation
        tremor_depth_amp = rng.uniform(0.15, 0.30)   # 15% to 30% amplitude modulation depth

        # 2. Cycle-to-cycle perturbation (Jitter & Shimmer)
        jitter_target = np.clip(rng.uniform(0.025, 0.050) + speaker_jitter_offset, 0.020, 0.060)
        shimmer_target = np.clip(rng.uniform(0.08, 0.16) + speaker_shimmer_offset, 0.06, 0.20)
        
        # 3. Glottal aspiration noise / reduced HNR (10 to 14 dB)
        hnr_target_db = rng.uniform(10.0, 14.0)
    else:
        # Healthy control parameters
        tremor_rate = 0.0
        tremor_depth_f0 = 0.0
        tremor_depth_amp = 0.0

        jitter_target = np.clip(rng.uniform(0.002, 0.005) + speaker_jitter_offset, 0.001, 0.006)
        shimmer_target = np.clip(rng.uniform(0.010, 0.020) + speaker_shimmer_offset, 0.008, 0.025)
        
        # High HNR (24 to 28 dB)
        hnr_target_db = rng.uniform(24.0, 28.0)

    # Instantaneous fundamental frequency F0(t)
    f0_tremor = tremor_depth_f0 * np.sin(2 * np.pi * tremor_rate * time)
    # Slow drift (natural vocal micro-fluctuation)
    f0_drift = np.cumsum(rng.normal(0, 0.01, size=num_samples))
    inst_f0 = np.clip(base_f0 + f0_tremor + f0_drift, 65.0, 320.0)

    # Phase accumulation
    phase = 2 * np.pi * np.cumsum(inst_f0) / sr

    # Low-pass filter for cycle-to-cycle perturbation
    nyq = sr / 2.0
    cutoff_hz = np.clip(np.mean(inst_f0) * 1.5, 50.0, nyq - 50.0)
    b_lp, a_lp = signal.butter(2, cutoff_hz / nyq, btype="low")

    # Jitter phase perturbation
    jitter_noise = rng.normal(0, jitter_target * 3.5, size=num_samples)
    smooth_jitter = signal.lfilter(b_lp, a_lp, jitter_noise)

    # Harmonic summation for glottal source
    glottal_source = np.zeros(num_samples)
    max_inst_f0 = max(float(np.max(inst_f0)), 50.0)
    num_harmonics = min(28, int(nyq / max_inst_f0))

    for h in range(1, num_harmonics + 1):
        harmonic_amp = 1.0 / (h ** 1.20)
        glottal_source += harmonic_amp * np.sin(h * phase + h * smooth_jitter)

    # Amplitude modulation (Vocal Tremor + Shimmer)
    tremor_amp_envelope = 1.0 + tremor_depth_amp * np.sin(2 * np.pi * tremor_rate * time + np.pi / 4)
    shimmer_noise = rng.normal(0, shimmer_target, size=num_samples)
    shimmer_envelope = 1.0 + signal.lfilter(b_lp, a_lp, shimmer_noise)
    glottal_source = glottal_source * tremor_amp_envelope * shimmer_envelope

    # Vocal tract resonance filtering: Formants for sustained /a/ vowel in PARALLEL
    # Formants: F1=730Hz (bw=60), F2=1090Hz (bw=90), F3=2440Hz (bw=100), F4=3400Hz (bw=120)
    formants = [
        (730.0, 60.0),
        (1090.0, 90.0),
        (2440.0, 100.0),
        (3400.0, 120.0),
    ]
    
    speech = np.zeros_like(glottal_source)
    for freq, bw in formants:
        q = freq / bw
        b, a = signal.iirpeak(freq, q, fs=sr)
        speech += signal.lfilter(b, a, glottal_source)

    # Additive glottal aspiration noise based on clinical HNR target
    speech_power = np.mean(speech ** 2) + 1e-12
    noise_power = speech_power / (10.0 ** (hnr_target_db / 10.0))
    raw_noise = rng.normal(0, np.sqrt(noise_power), size=num_samples)
    
    # Bandpass filter aspiration noise (300 Hz - 6000 Hz)
    b_noise, a_noise = signal.butter(2, [300.0 / nyq, min(6000.0 / nyq, 0.95)], btype="band")
    aspiration_noise = signal.lfilter(b_noise, a_noise, raw_noise)
    
    total_audio = speech + aspiration_noise

    # Smooth onset and offset fade (50ms)
    fade_len = int(0.05 * sr)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    total_audio[:fade_len] *= fade_in
    total_audio[-fade_len:] *= fade_out

    # Normalize peak to 0.90
    max_amp = np.max(np.abs(total_audio))
    if max_amp > 0:
        total_audio = (total_audio / max_amp * 0.90).astype(np.float32)

    metadata = {
        "is_parkinsons": float(is_parkinsons),
        "base_f0": round(float(base_f0), 2),
        "tremor_rate": round(float(tremor_rate), 2),
        "tremor_depth_f0": round(float(tremor_depth_f0), 2),
        "tremor_depth_amp": round(float(tremor_depth_amp), 2),
        "jitter_target": round(float(jitter_target), 4),
        "shimmer_target": round(float(shimmer_target), 4),
        "hnr_target_db": round(float(hnr_target_db), 2),
    }

    return total_audio, metadata


def generate_benchmark_dataset(
    output_dir: str = "ml/data/processed",
    num_speakers: int = 600,
    samples_per_speaker: int = 5,
    duration: float = 3.0,
    sr: int = 16000,
    seed: int = 42,
) -> pd.DataFrame:
    """Creates a balanced, speaker-independent dataset split into train/val/test.
    
    Generates 600 speakers (300 Healthy, 300 Parkinson's) with 5 takes each (3,000 total).
    Wider pitch (F0) distribution across male (85-155 Hz) and female (165-255 Hz) speakers.
    Strict 70/15/15 subject-independent split (zero speaker overlap between train/val/test).
    """
    rng = np.random.default_rng(seed)
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    records: List[Dict] = []

    # Assign speakers: 50% healthy, 50% parkinsons
    speakers = []
    half_speakers = num_speakers // 2
    for i in range(num_speakers):
        is_pd = (i % 2 == 1)
        label = "parkinsons" if is_pd else "healthy"
        gender = "M" if rng.random() > 0.5 else "F"
        
        # Male F0: 85 - 155 Hz; Female F0: 165 - 255 Hz
        if gender == "M":
            base_f0 = rng.uniform(85.0, 155.0)
        else:
            base_f0 = rng.uniform(165.0, 255.0)

        # Persistent speaker offsets
        spk_jitter_offset = rng.normal(0, 0.002)
        spk_shimmer_offset = rng.normal(0, 0.005)

        speaker_id = f"SPK_{label[:2].upper()}_{i+1:04d}"
        speakers.append((speaker_id, is_pd, label, gender, base_f0, spk_jitter_offset, spk_shimmer_offset))

    # Split speakers strictly: 70% train, 15% val, 15% test (zero speaker overlap)
    shuffled_idx = rng.permutation(len(speakers))
    n_train = int(0.70 * len(speakers))
    n_val = int(0.15 * len(speakers))

    for rank, idx in enumerate(shuffled_idx):
        speaker_id, is_pd, label, gender, base_f0, j_offset, s_offset = speakers[idx]
        if rank < n_train:
            split = "train"
        elif rank < n_train + n_val:
            split = "val"
        else:
            split = "test"

        split_dir = base_path / split / label
        split_dir.mkdir(parents=True, exist_ok=True)

        for s_idx in range(samples_per_speaker):
            # Slight F0 micro-variation across takes for same speaker (+/- 2%)
            sample_f0 = base_f0 * rng.uniform(0.98, 1.02)
            audio, meta = generate_phonation_sample(
                duration=duration,
                sr=sr,
                is_parkinsons=is_pd,
                base_f0=sample_f0,
                speaker_jitter_offset=j_offset,
                speaker_shimmer_offset=s_offset,
                rng=rng,
            )

            sample_id = f"{speaker_id}_take_{s_idx+1:02d}.wav"
            file_path = split_dir / sample_id
            sf.write(str(file_path), audio, sr)

            rec = {
                "file_path": str(file_path),
                "relative_path": f"{split}/{label}/{sample_id}",
                "speaker_id": speaker_id,
                "take": s_idx + 1,
                "label": label,
                "target": 1 if is_pd else 0,
                "gender": gender,
                "split": split,
                "sample_rate": sr,
                "duration": duration,
                **meta,
            }
            records.append(rec)

    df = pd.DataFrame(records)
    csv_path = base_path / "dataset_manifest.csv"
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} samples across {num_speakers} speakers in {output_dir}")
    print(df.groupby(["split", "label"]).size())
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic phonations for SteadyVox")
    parser.add_argument("--output_dir", type=str, default="ml/data/processed")
    parser.add_argument("--num_speakers", type=int, default=600)
    parser.add_argument("--samples_per_speaker", type=int, default=5)
    parser.add_argument("--duration", type=float, default=3.0)
    parser.add_argument("--sr", type=int, default=16000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_benchmark_dataset(
        output_dir=args.output_dir,
        num_speakers=args.num_speakers,
        samples_per_speaker=args.samples_per_speaker,
        duration=args.duration,
        sr=args.sr,
        seed=args.seed,
    )
