"""Unit tests for SteadyVox CNN baseline architecture."""

import torch
import pytest
from ml.models.cnn_baseline import CNNBaseline


def test_cnn_baseline_forward():
    model = CNNBaseline()
    # Dummy mel-spectrogram batch: (B=4, C=1, n_mels=128, time_steps=94)
    dummy_input = torch.randn(4, 1, 128, 94)
    logits = model(dummy_input)
    assert logits.shape == (4, 1)


def test_cnn_baseline_predict_proba():
    model = CNNBaseline()
    dummy_sample = torch.randn(1, 1, 128, 94)
    prob, conf, label = model.predict_proba(dummy_sample)

    assert 0.0 <= prob <= 1.0
    assert 0.5 <= conf <= 1.0
    assert label in ["parkinsons", "healthy"]


def test_cnn_feature_extraction():
    model = CNNBaseline()
    dummy_sample = torch.randn(2, 1, 128, 94)
    features = model.extract_features(dummy_sample)
    assert features.shape == (2, 256)


def test_cnn_bilstm_forward():
    from ml.models.cnn_bilstm import CNNBiLSTM
    model = CNNBiLSTM()
    dummy_input = torch.randn(4, 1, 128, 94)
    logits = model(dummy_input)
    assert logits.shape == (4, 1)


def test_cnn_bilstm_predict_proba():
    from ml.models.cnn_bilstm import CNNBiLSTM
    model = CNNBiLSTM()
    dummy_sample = torch.randn(1, 1, 128, 94)
    prob, conf, label = model.predict_proba(dummy_sample)

    assert 0.0 <= prob <= 1.0
    assert 0.5 <= conf <= 1.0
    assert label in ["parkinsons", "healthy"]


def test_cnn_bilstm_attention():
    from ml.models.cnn_bilstm import CNNBiLSTM
    model = CNNBiLSTM()
    dummy_sample = torch.randn(2, 1, 128, 94)
    context, attn_weights = model.extract_features(dummy_sample)

    assert context.shape == (2, 128)
    assert attn_weights.shape == (2, 23, 1)
    # Check that attention weights sum to 1.0 across time dimension
    weight_sums = torch.sum(attn_weights, dim=1)
    assert torch.allclose(weight_sums, torch.ones_like(weight_sums), atol=1e-5)

