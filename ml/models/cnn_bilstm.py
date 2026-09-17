"""SteadyVox CNN + BiLSTM Deep Learning Model for Voice Screening.

Combines 2D Convolutional Neural Networks for spectral feature extraction
with Bidirectional LSTM layers and Temporal Self-Attention to capture vocal
tremor, cycle-to-cycle frequency perturbations, and phonatory instability.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNReLU(nn.Module):
    """Convolution -> BatchNorm -> ReLU -> MaxPool -> Dropout block."""
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        pool_size: Tuple[int, int] = (2, 2),
        dropout: float = 0.10,
    ):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(kernel_size=pool_size)
        self.drop = nn.Dropout2d(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.drop(self.pool(self.relu(self.bn(self.conv(x)))))


class TemporalAttention(nn.Module):
    """Self-attention pooling mechanism over temporal sequence."""
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (Batch, Time, Hidden)
        Returns:
            context: (Batch, Hidden)
            weights: (Batch, Time, 1)
        """
        scores = self.attn(x)  # (B, T, 1)
        weights = F.softmax(scores, dim=1)  # (B, T, 1)
        context = torch.sum(x * weights, dim=1)  # (B, Hidden)
        return context, weights


class CNNBiLSTM(nn.Module):
    """CNN + BiLSTM with Temporal Attention for Parkinson's Voice Screening."""

    def __init__(
        self,
        in_channels: int = 1,
        num_classes: int = 1,
        lstm_hidden: int = 64,
        lstm_layers: int = 1,
        dropout_rate: float = 0.3,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.lstm_hidden = lstm_hidden

        # 1. Spectral CNN Backbone
        # Input: (B, 1, 128 mels, ~94 time frames)
        self.block1 = ConvBNReLU(in_channels, 32, pool_size=(2, 2), dropout=0.10) # -> (B, 32, 64, 47)
        self.block2 = ConvBNReLU(32, 64, pool_size=(2, 2), dropout=0.15)          # -> (B, 64, 32, 23)
        self.block3 = ConvBNReLU(64, 64, pool_size=(2, 1), dropout=0.15)          # -> (B, 64, 16, 23)

        # Spectral projection: 64 channels * 16 mels = 1024 -> 128
        self.proj = nn.Sequential(
            nn.Linear(64 * 16, 128),
            nn.LayerNorm(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.20),
        )

        # 2. Bidirectional LSTM
        # Input: (B, T=23, 128) -> Output: (B, T=23, lstm_hidden * 2 = 128)
        self.bilstm = nn.LSTM(
            input_size=128,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            batch_first=True,
            bidirectional=True,
        )

        # 3. Temporal Attention
        self.attention = TemporalAttention(hidden_dim=lstm_hidden * 2)

        # 4. Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 32),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(32, num_classes),
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d) or isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)

    def extract_features(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extracts temporal representation.
        Returns:
            context: (Batch, lstm_hidden * 2)
            attn_weights: (Batch, Time, 1)
        """
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)  # (B, 64, 16, T)

        B, C, M, T = x.shape
        x = x.permute(0, 3, 1, 2).contiguous().view(B, T, C * M)
        x = self.proj(x)  # (B, T, 128)

        lstm_out, _ = self.bilstm(x)  # (B, T, 2 * lstm_hidden)
        context, attn_weights = self.attention(lstm_out)
        return context, attn_weights

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        context, _ = self.extract_features(x)
        logits = self.classifier(context)
        return logits

    @torch.no_grad()
    def predict_proba(self, x: torch.Tensor) -> Tuple[float, float, str]:
        self.eval()
        logits = self.forward(x)
        prob = torch.sigmoid(logits).item()
        
        is_pd = prob >= 0.50
        label = "parkinsons" if is_pd else "healthy"
        confidence = prob if is_pd else (1.0 - prob)

        return float(prob), float(confidence), label
