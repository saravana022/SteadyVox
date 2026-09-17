"""SteadyVox Tabular MLP Neural Network for Acoustic Biomarker Classification.

Trained on the Oxford Parkinson's Disease Detection Dataset (Little et al., 2007).
Classifies 22 clinical voice features: fundamental frequency perturbation,
amplitude perturbation, noise-to-harmonics ratios, and nonlinear dynamical complexity.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Tuple, List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


FEATURE_NAMES: List[str] = [
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
    "RPDE",
    "DFA",
    "spread1",
    "spread2",
    "D2",
    "PPE",
]


class TabularMLP(nn.Module):
    """Deep Multi-Layer Perceptron for 22 Acoustic Biomarker Features.
    
    Employs LayerNorm and LeakyReLU activations for robust sample-level normalization
    and high generalization on clinical tabular biomarkers.
    """

    def __init__(
        self,
        in_features: int = 22,
        hidden_dim1: int = 64,
        hidden_dim2: int = 32,
        dropout_rate: float = 0.20,
        calibrated_threshold: float = 0.50,
    ):
        super().__init__()
        self.in_features = in_features
        self.hidden_dim1 = hidden_dim1
        self.hidden_dim2 = hidden_dim2
        self.feature_names = FEATURE_NAMES
        self.calibrated_threshold = calibrated_threshold

        # Hidden Layer 1
        self.fc1 = nn.Linear(in_features, hidden_dim1)
        self.ln1 = nn.LayerNorm(hidden_dim1)
        self.act1 = nn.LeakyReLU(negative_slope=0.1)
        self.drop1 = nn.Dropout(dropout_rate)

        # Hidden Layer 2
        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.ln2 = nn.LayerNorm(hidden_dim2)
        self.act2 = nn.LeakyReLU(negative_slope=0.1)
        self.drop2 = nn.Dropout(dropout_rate)

        # Output projection
        self.fc_out = nn.Linear(hidden_dim2, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning scalar logit per sample (shape: [B, 1])."""
        if x.dim() == 1:
            x = x.unsqueeze(0)
        
        x = self.drop1(self.act1(self.ln1(self.fc1(x))))
        x = self.drop2(self.act2(self.ln2(self.fc2(x))))
        logits = self.fc_out(x)
        return logits

    @torch.no_grad()
    def predict_proba(
        self,
        x: torch.Tensor,
        threshold: Optional[float] = None
    ) -> Tuple[float, float, str]:
        """Runs evaluation mode inference on a feature vector.
        
        Args:
            x: Tensor of shape (22,) or (1, 22) pre-scaled features.
            threshold: Optional classification threshold; defaults to calibrated_threshold.
            
        Returns:
            probability: float in [0.0, 1.0] (probability of Parkinson's indicators)
            confidence: float in [0.5, 1.0] (confidence in top prediction)
            prediction_label: 'parkinsons' or 'healthy'
        """
        self.eval()
        if x.dim() == 1:
            x = x.unsqueeze(0)
        logits = self.forward(x)
        prob = torch.sigmoid(logits).squeeze().item()

        effective_thresh = threshold if threshold is not None else self.calibrated_threshold
        is_pd = prob >= effective_thresh
        label = "parkinsons" if is_pd else "healthy"
        
        if is_pd:
            confidence = max(0.5, prob)
        else:
            confidence = max(0.5, 1.0 - prob)

        return float(prob), float(confidence), label
