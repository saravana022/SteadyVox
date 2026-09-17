"""SteadyVox Pydantic API Schemas.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class BiomarkersSchema(BaseModel):
    f0_mean: float = Field(..., description="Mean Fundamental Frequency in Hz")
    f0_std: float = Field(..., description="F0 Standard Deviation")
    f0_min: float = Field(..., description="Minimum F0 in Hz")
    f0_max: float = Field(..., description="Maximum F0 in Hz")
    jitter_local_percent: float = Field(..., description="Cycle-to-cycle frequency variation (%)")
    jitter_rap_percent: float = Field(..., description="Relative Average Perturbation (%)")
    jitter_ppq5_percent: float = Field(..., description="Five-point Period Perturbation Quotient (%)")
    shimmer_local_percent: float = Field(..., description="Cycle-to-cycle amplitude variation (%)")
    shimmer_local_db: float = Field(..., description="Shimmer in Decibels (dB)")
    shimmer_apq3_percent: float = Field(..., description="Three-point Amplitude Perturbation Quotient (%)")
    shimmer_apq5_percent: float = Field(..., description="Five-point Amplitude Perturbation Quotient (%)")
    hnr_mean_db: float = Field(..., description="Mean Harmonics-to-Noise Ratio in dB")


class ScreeningResponse(BaseModel):
    session_id: str
    patient_identifier: Optional[str] = None
    original_filename: str
    prediction: str = Field(..., description="'parkinsons' or 'healthy'")
    probability: float = Field(..., description="Risk probability score [0.0 - 1.0]")
    confidence: float = Field(..., description="Prediction confidence score [0.5 - 1.0]")
    model_architecture: str
    biomarkers: BiomarkersSchema
    audio_url: Optional[str] = None
    latency_ms: float
    disclaimer: str = Field(
        default="Research screening tool only — not a medical diagnosis.",
        description="Mandatory non-diagnostic legal warning",
    )
    created_at: str


class ScreeningHistoryItem(BaseModel):
    id: str
    patient_identifier: Optional[str] = None
    original_filename: str
    prediction: str
    probability: float
    confidence: float
    model_architecture: str
    biomarkers: Dict[str, float]
    disclaimer: str
    created_at: str


class ScreeningHistoryList(BaseModel):
    total: int
    items: List[ScreeningHistoryItem]
    disclaimer: str = "Research screening tool only — not a medical diagnosis."
