"""SteadyVox 2D CNN Spectrogram Baseline Model.

Analyzes 2D Log Mel-Spectrograms to detect acoustic dysarthria and spectral patterns.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Tuple, Dict, Any
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    """Convolution -> BatchNorm -> ReLU -> MaxPool -> Dropout block."""
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        padding: int = 1,
        dropout: float = 0.15,
    ):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.drop = nn.Dropout2d(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.drop(self.pool(self.relu(self.bn(self.conv(x)))))


class CNNBaseline(nn.Module):
    """2D Convolutional Baseline for Parkinson's Voice Screening."""

    def __init__(
        self,
        in_channels: int = 1,
        num_classes: int = 1,
        base_filters: int = 32,
        dropout_rate: float = 0.4,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes

        # Feature Extraction Backbone
        self.layer1 = ConvBlock(in_channels, base_filters, dropout=0.10)       # 32
        self.layer2 = ConvBlock(base_filters, base_filters * 2, dropout=0.15)  # 64
        self.layer3 = ConvBlock(base_filters * 2, base_filters * 4, dropout=0.20)  # 128
        self.layer4 = ConvBlock(base_filters * 4, base_filters * 8, dropout=0.25)  # 256

        # Global Pooling
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Classification Head
        self.fc1 = nn.Linear(base_filters * 8, 64)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc_out = nn.Linear(64, num_classes)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Returns flattened feature vector before classification layer."""
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.global_pool(x)
        return torch.flatten(x, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning raw logits (shape: [B, 1])."""
        feat = self.extract_features(x)
        out = self.fc1(feat)
        out = self.relu(out)
        out = self.dropout(out)
        logits = self.fc_out(out)
        return logits

    @torch.no_grad()
    def predict_proba(self, x: torch.Tensor) -> Tuple[float, float, str]:
        """Runs evaluation mode inference on a single batch or sample tensor.
        
        Returns:
            probability: float in [0.0, 1.0] (probability of Parkinson's indicators)
            confidence: float in [0.5, 1.0] (confidence in the top prediction)
            prediction_label: 'parkinsons' or 'healthy'
        """
        self.eval()
        logits = self.forward(x)
        prob = torch.sigmoid(logits).item()
        
        is_pd = prob >= 0.50
        label = "parkinsons" if is_pd else "healthy"
        confidence = prob if is_pd else (1.0 - prob)

        return float(prob), float(confidence), label
