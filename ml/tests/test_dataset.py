"""Unit tests for SteadyVox synthetic data generation and dataset loader."""

import tempfile
import pytest
import torch
from ml.data.synthetic_generator import generate_benchmark_dataset, generate_phonation_sample
from ml.data.dataset import create_dataloaders, ParkinsonVoiceDataset


def test_generate_phonation_sample():
    audio_hc, meta_hc = generate_phonation_sample(duration=1.0, sr=16000, is_parkinsons=False)
    assert len(audio_hc) == 16000
    assert meta_hc["is_parkinsons"] == 0.0

    audio_pd, meta_pd = generate_phonation_sample(duration=1.0, sr=16000, is_parkinsons=True)
    assert len(audio_pd) == 16000
    assert meta_pd["is_parkinsons"] == 1.0


def test_dataset_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate mini benchmark dataset
        df = generate_benchmark_dataset(
            output_dir=tmpdir,
            num_speakers=8,
            samples_per_speaker=2,
            duration=1.0,
            sr=16000,
        )
        assert len(df) == 16

        train_loader, val_loader, test_loader, pos_weight = create_dataloaders(
            data_dir=tmpdir,
            batch_size=2,
        )
        assert len(train_loader) > 0
        assert len(val_loader) > 0
        assert len(test_loader) > 0

        # Fetch one batch
        batch_x, batch_y, paths = next(iter(train_loader))
        assert batch_x.ndim == 4
        assert batch_x.shape[0] == 2
        assert batch_x.shape[1] == 1  # 1 channel
        assert batch_x.shape[2] == 128 # 128 mels
        assert batch_y.shape == (2, 1)
