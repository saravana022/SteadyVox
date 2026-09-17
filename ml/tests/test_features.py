"""Unit tests for SteadyVox audio preprocessing and feature extraction."""

import numpy as np
import pytest
from ml.preprocessing.audio_cleaning import (
    AudioConfig,
    trim_silence,
    normalize_audio,
    pad_or_truncate,
    preprocess_pipeline,
)
from ml.preprocessing.feature_extraction import (
    extract_mel_spectrogram,
    extract_mfcc,
    extract_biomarkers,
    extract_model_features,
    AcousticBiomarkers,
)


@pytest.fixture
def synthetic_tone():
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 220 Hz sine tone with slight harmonics
    wave = 0.5 * np.sin(2 * np.pi * 220 * t) + 0.2 * np.sin(2 * np.pi * 440 * t)
    return wave.astype(np.float32), sr


def test_pad_or_truncate(synthetic_tone):
    wave, sr = synthetic_tone
    target_len = 48000  # 3 seconds at 16kHz
    padded = pad_or_truncate(wave, target_len)
    assert len(padded) == target_len

    truncated = pad_or_truncate(padded, 16000)
    assert len(truncated) == 16000


def test_normalize_audio(synthetic_tone):
    wave, sr = synthetic_tone
    normalized = normalize_audio(wave * 0.1, peak_norm=True, rms_norm=True, target_rms=0.1)
    assert np.max(np.abs(normalized)) <= 1.0
    rms = np.sqrt(np.mean(normalized ** 2))
    assert pytest.approx(rms, rel=0.1) == 0.1


def test_extract_mel_spectrogram(synthetic_tone):
    wave, sr = synthetic_tone
    n_mels = 128
    mel_spec = extract_mel_spectrogram(wave, sr=sr, n_mels=n_mels)
    assert mel_spec.ndim == 2
    assert mel_spec.shape[0] == n_mels
    assert mel_spec.min() >= 0.0
    assert mel_spec.max() <= 1.0


def test_extract_mfcc(synthetic_tone):
    wave, sr = synthetic_tone
    n_mfcc = 40
    mfcc_with_deltas = extract_mfcc(wave, sr=sr, n_mfcc=n_mfcc, include_deltas=True)
    assert mfcc_with_deltas.shape[0] == n_mfcc * 3


def test_extract_biomarkers(synthetic_tone):
    wave, sr = synthetic_tone
    biomarkers = extract_biomarkers(wave, sr=sr)
    assert isinstance(biomarkers, AcousticBiomarkers)
    # The tone fundamental frequency should be around 220 Hz
    assert 180 <= biomarkers.f0_mean <= 260
    assert biomarkers.jitter_local_percent >= 0.0
    assert biomarkers.shimmer_local_percent >= 0.0
    b_dict = biomarkers.to_dict()
    assert "hnr_mean_db" in b_dict


def test_extract_model_features(synthetic_tone):
    wave, sr = synthetic_tone
    tensor = extract_model_features(wave, sr=sr, n_mels=128)
    assert tensor.shape[0] == 1  # batch
    assert tensor.shape[1] == 1  # channel
    assert tensor.shape[2] == 128 # mels
