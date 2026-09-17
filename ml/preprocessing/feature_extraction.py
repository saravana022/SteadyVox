"""SteadyVox Acoustic Feature Extraction Module.

Extracts both:
1. Deep Learning Representations: Log Mel-Spectrograms and MFCCs (for CNN/BiLSTM).
2. Clinical Voice Pathology Biomarkers: Pitch (F0), Jitter, Shimmer, HNR using Praat/Parselmouth.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Tuple
import numpy as np
import librosa
import torch

try:
    import parselmouth
    from parselmouth.praat import call as praat_call
    PARSELMOUTH_AVAILABLE = True
except ImportError:
    PARSELMOUTH_AVAILABLE = False


@dataclass
class AcousticBiomarkers:
    """Clinical voice pathology metrics."""
    # Pitch / Fundamental frequency (Hz)
    f0_mean: float
    f0_std: float
    f0_min: float
    f0_max: float
    
    # Jitter (Frequency perturbation)
    jitter_local_percent: float  # Normal threshold ~ < 1.04%
    jitter_rap_percent: float    # Normal threshold ~ < 0.68%
    jitter_ppq5_percent: float   # Normal threshold ~ < 0.84%
    
    # Shimmer (Amplitude perturbation)
    shimmer_local_percent: float # Normal threshold ~ < 3.81%
    shimmer_local_db: float      # Normal threshold ~ < 0.35 dB
    shimmer_apq3_percent: float  # Normal threshold ~ < 1.95%
    shimmer_apq5_percent: float  # Normal threshold ~ < 2.50%
    
    # Glottal Efficiency & Noise
    hnr_mean_db: float           # Normal threshold ~ > 20 dB (PD often < 15 dB)

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


def extract_mel_spectrogram(
    waveform: np.ndarray,
    sr: int = 16000,
    n_mels: int = 128,
    n_fft: int = 1024,
    hop_length: int = 512,
    f_min: float = 50.0,
    f_max: float = 8000.0,
) -> np.ndarray:
    """Extracts Log Mel-Spectrogram in dB.
    
    Output shape: (n_mels, time_steps)
    """
    mel_spec = librosa.feature.melspectrogram(
        y=waveform,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels,
        fmin=f_min,
        fmax=f_max,
        power=2.0,
    )
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    # Normalize between 0 and 1 or standard scaler
    log_mel_spec = (log_mel_spec - log_mel_spec.min()) / (log_mel_spec.max() - log_mel_spec.min() + 1e-8)
    return log_mel_spec.astype(np.float32)


def extract_mfcc(
    waveform: np.ndarray,
    sr: int = 16000,
    n_mfcc: int = 40,
    n_fft: int = 1024,
    hop_length: int = 512,
    include_deltas: bool = True,
) -> np.ndarray:
    """Extracts MFCC features with optional first and second-order derivatives.
    
    Output shape: (n_mfcc * (3 if include_deltas else 1), time_steps)
    """
    mfcc = librosa.feature.mfcc(
        y=waveform,
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    if not include_deltas:
        return mfcc.astype(np.float32)

    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    features = np.vstack([mfcc, delta, delta2])
    return features.astype(np.float32)


def extract_biomarkers(
    waveform: np.ndarray,
    sr: int = 16000,
    pitch_floor: float = 75.0,
    pitch_ceiling: float = 600.0,
) -> AcousticBiomarkers:
    """Extracts clinical vocal biomarkers (F0, Jitter, Shimmer, HNR).
    
    Utilizes Praat/Parselmouth for standard clinical acoustic measurement.
    """
    if PARSELMOUTH_AVAILABLE and len(waveform) > sr * 0.1:
        try:
            sound = parselmouth.Sound(waveform, sampling_frequency=sr)
            
            # Pitch analysis
            pitch = sound.to_pitch(pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
            f0_values = pitch.selected_array['frequency']
            f0_values = f0_values[f0_values > 0]  # Unvoiced frames filtered out
            
            if len(f0_values) > 0:
                f0_mean = float(np.mean(f0_values))
                f0_std = float(np.std(f0_values))
                f0_min = float(np.min(f0_values))
                f0_max = float(np.max(f0_values))
            else:
                f0_mean, f0_std, f0_min, f0_max = 0.0, 0.0, 0.0, 0.0

            # PointProcess for Jitter & Shimmer
            point_process = praat_call(
                sound, "To PointProcess (periodic, cc)", pitch_floor, pitch_ceiling
            )

            # Jitter calculations
            jitter_local = praat_call(
                point_process, "Get jitter (local)", 0.0, 0.0, 0.0001, 0.02, 1.3
            ) * 100.0
            jitter_rap = praat_call(
                point_process, "Get jitter (rap)", 0.0, 0.0, 0.0001, 0.02, 1.3
            ) * 100.0
            jitter_ppq5 = praat_call(
                point_process, "Get jitter (ppq5)", 0.0, 0.0, 0.0001, 0.02, 1.3
            ) * 100.0

            # Shimmer calculations
            shimmer_local = praat_call(
                [sound, point_process], "Get shimmer (local)", 0.0, 0.0, 0.0001, 0.02, 1.3, 1.6
            ) * 100.0
            shimmer_local_db = praat_call(
                [sound, point_process], "Get shimmer (local_dB)", 0.0, 0.0, 0.0001, 0.02, 1.3, 1.6
            )
            shimmer_apq3 = praat_call(
                [sound, point_process], "Get shimmer (apq3)", 0.0, 0.0, 0.0001, 0.02, 1.3, 1.6
            ) * 100.0
            shimmer_apq5 = praat_call(
                [sound, point_process], "Get shimmer (apq5)", 0.0, 0.0, 0.0001, 0.02, 1.3, 1.6
            ) * 100.0

            # Harmonics-to-Noise Ratio (HNR)
            harmonicity = sound.to_harmonicity(pitch_floor=pitch_floor)
            hnr_values = harmonicity.values
            hnr_valid = hnr_values[hnr_values > -200]
            hnr_mean = float(np.mean(hnr_valid)) if len(hnr_valid) > 0 else 0.0

            # Clean NaNs or Infinities
            return AcousticBiomarkers(
                f0_mean=f0_mean if np.isfinite(f0_mean) else 0.0,
                f0_std=f0_std if np.isfinite(f0_std) else 0.0,
                f0_min=f0_min if np.isfinite(f0_min) else 0.0,
                f0_max=f0_max if np.isfinite(f0_max) else 0.0,
                jitter_local_percent=jitter_local if np.isfinite(jitter_local) else 0.0,
                jitter_rap_percent=jitter_rap if np.isfinite(jitter_rap) else 0.0,
                jitter_ppq5_percent=jitter_ppq5 if np.isfinite(jitter_ppq5) else 0.0,
                shimmer_local_percent=shimmer_local if np.isfinite(shimmer_local) else 0.0,
                shimmer_local_db=shimmer_local_db if np.isfinite(shimmer_local_db) else 0.0,
                shimmer_apq3_percent=shimmer_apq3 if np.isfinite(shimmer_apq3) else 0.0,
                shimmer_apq5_percent=shimmer_apq5 if np.isfinite(shimmer_apq5) else 0.0,
                hnr_mean_db=hnr_mean if np.isfinite(hnr_mean) else 0.0,
            )
        except Exception:
            pass

    # Fallback approximation using Librosa if Parselmouth is unavailable
    return _librosa_fallback_biomarkers(waveform, sr, pitch_floor, pitch_ceiling)


def _librosa_fallback_biomarkers(
    waveform: np.ndarray,
    sr: int,
    pitch_floor: float,
    pitch_ceiling: float,
) -> AcousticBiomarkers:
    """Fallback estimator for acoustic metrics when Praat is unavailable."""
    f0, voiced_flag, _ = librosa.pyin(
        waveform,
        fmin=pitch_floor,
        fmax=pitch_ceiling,
        sr=sr,
        frame_length=2048,
    )
    voiced_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    
    if len(voiced_f0) > 1:
        f0_mean = float(np.mean(voiced_f0))
        f0_std = float(np.std(voiced_f0))
        f0_min = float(np.min(voiced_f0))
        f0_max = float(np.max(voiced_f0))
        
        # Approximate jitter from period differences
        periods = 1.0 / voiced_f0
        diffs = np.abs(np.diff(periods))
        jitter_local = float(np.mean(diffs) / np.mean(periods) * 100.0) if len(diffs) > 0 else 0.0
    else:
        f0_mean, f0_std, f0_min, f0_max, jitter_local = 0.0, 0.0, 0.0, 0.0, 0.0

    # Approximate shimmer from frame amplitudes
    rms = librosa.feature.rms(y=waveform)[0]
    rms = rms[rms > 1e-4]
    if len(rms) > 1:
        amp_diffs = np.abs(np.diff(rms))
        shimmer_local = float(np.mean(amp_diffs) / np.mean(rms) * 100.0)
        shimmer_db = float(20 * np.log10(1 + (shimmer_local / 100.0)))
    else:
        shimmer_local, shimmer_db = 0.0, 0.0

    # Approximate HNR via harmonic and percussive separation
    harmonic, percussive = librosa.effects.hpss(waveform)
    harm_energy = np.sum(harmonic ** 2) + 1e-8
    noise_energy = np.sum(percussive ** 2) + 1e-8
    hnr_mean = float(10 * np.log10(harm_energy / noise_energy))

    return AcousticBiomarkers(
        f0_mean=f0_mean,
        f0_std=f0_std,
        f0_min=f0_min,
        f0_max=f0_max,
        jitter_local_percent=jitter_local,
        jitter_rap_percent=jitter_local * 0.6,
        jitter_ppq5_percent=jitter_local * 0.8,
        shimmer_local_percent=shimmer_local,
        shimmer_local_db=shimmer_db,
        shimmer_apq3_percent=shimmer_local * 0.5,
        shimmer_apq5_percent=shimmer_local * 0.7,
        hnr_mean_db=hnr_mean,
    )


def extract_model_features(
    waveform: np.ndarray,
    sr: int = 16000,
    n_mels: int = 128,
) -> torch.Tensor:
    """Convenience function returning a PyTorch tensor suitable for model inference.
    
    Output shape: (1, 1, n_mels, time_steps)
    """
    mel_spec = extract_mel_spectrogram(waveform, sr=sr, n_mels=n_mels)
    tensor = torch.from_numpy(mel_spec).unsqueeze(0).unsqueeze(0)  # (1, 1, n_mels, T)
    return tensor
