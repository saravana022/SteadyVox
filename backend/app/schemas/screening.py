"""SteadyVox Pydantic API Schemas with Patient Intake, RFC 7807 problem details, and model provenance.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator
from backend.app.services.quality_gate import QualityReport


# --- Patient Intake Schemas ---

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Patient full name, initials, or pseudonym")
    age: int = Field(..., ge=18, le=110, description="Patient age (must be between 18 and 110)")
    gender: str = Field(..., description="Gender: Male, Female, Other, or Prefer not to say")
    consent: bool = Field(..., description="Explicit consent agreement")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid = ["male", "female", "other", "prefer not to say"]
        if v.strip().lower() not in valid:
            raise ValueError(f"Gender must be one of {valid}")
        return v.strip().title()

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Informed consent is mandatory before voice intake.")
        return v


class PatientResponse(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    consent_at: str
    created_at: str


# --- Screening & Biomarkers Schemas ---

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
    rpde: Optional[float] = Field(None, description="Recurrence Period Density Entropy")
    dfa: Optional[float] = Field(None, description="Detrended Fluctuation Analysis")
    ppe: Optional[float] = Field(None, description="Pitch Period Entropy")


class ModelProvenanceSchema(BaseModel):
    name: str = Field(..., description="Name of the machine learning model")
    version: str = Field(..., description="Semantic version or checkpoint tag")
    architecture: str = Field(..., description="Model neural or tabular architecture")
    provenance: str = Field(..., description="Exact dataset and training provenance citation")
    dataset_type: str = Field(..., description="Real Clinical Dataset vs Synthetic Benchmark")
    validation_metric: str = Field(..., description="Validated test score (ROC-AUC / F1)")
    probability: float = Field(..., description="Model calibrated posterior risk probability [0.0 - 1.0]")
    confidence: float = Field(..., description="Model decision confidence margin")
    risk_level: str = Field(..., description="Three-tier categorization: low, uncertain, or elevated")


class ScreeningResponse(BaseModel):
    request_id: str = Field(..., description="Unique request tracing ID")
    session_id: str = Field(..., description="Screening record session UUID")
    patient_id: Optional[str] = Field(None, description="Patient UUID")
    patient_identifier: Optional[str] = Field(None, description="Patient display identifier / name")
    patient_name: Optional[str] = Field(None, description="Patient display name")
    patient_age: Optional[int] = Field(None, description="Patient age")
    patient_gender: Optional[str] = Field(None, description="Patient gender")
    original_filename: str = Field(..., description="Uploaded audio file name")
    audio_sha256: str = Field(..., description="SHA-256 integrity hash of raw audio payload")
    
    # Three-tier Clinical Risk Output
    risk_level: str = Field(..., description="Categorical risk stratification: 'low', 'uncertain', 'elevated', or 'ood'")
    prediction: str = Field(..., description="Binary classification label: 'healthy' or 'parkinsons'")
    probability: float = Field(..., description="Primary risk probability score [0.0 - 1.0]")
    confidence: float = Field(..., description="Model uncertainty margin (e.g. ±0.04)")
    confidence_interval: Optional[List[float]] = Field(None, description="95% probability confidence interval [low, high]")
    explanation: Optional[str] = Field(None, description="Dynamic clinically grounded feature explanation")
    
    # Input Quality & Safety Guards
    quality_report: QualityReport = Field(..., description="Acoustic quality gate validation results")
    ood_status: Optional[str] = Field("in_distribution", description="'in_distribution' or 'out_of_distribution'")
    path_disagreement: bool = Field(False, description="True if primary and secondary paths diverge significantly")
    
    # Model Provenance
    primary_model: ModelProvenanceSchema = Field(..., description="Primary real-data calibrated model")
    secondary_model: Optional[ModelProvenanceSchema] = Field(None, description="Dev-only ablation benchmark")
    
    # Extracted Biomarkers
    biomarkers: BiomarkersSchema = Field(..., description="Extracted clinical acoustic perturbations")
    audio_url: Optional[str] = Field(None, description="Presigned URL or direct audio retrieval path")
    
    # Latency Telemetry
    latency_ms: float = Field(..., description="Total processing latency in milliseconds")
    stage_latencies: Dict[str, float] = Field(default_factory=dict, description="Execution breakdown per stage in ms")
    
    # Regulatory
    disclaimer: str = Field(
        default="Research screening tool only — not a medical diagnosis. Consult a qualified neurologist.",
        description="Mandatory non-diagnostic legal warning",
    )
    created_at: str


class ProblemDetail(BaseModel):
    """RFC 7807 standard Problem Details for HTTP APIs."""
    type: str = Field(..., description="URI reference identifying the problem type")
    title: str = Field(..., description="Short, human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(None, description="URI reference identifying specific occurrence")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    quality_report: Optional[QualityReport] = Field(None, description="Quality report if rejection occurred")


class ScreeningHistoryItem(BaseModel):
    id: str
    patient_id: Optional[str] = None
    patient_identifier: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    original_filename: str
    audio_sha256: Optional[str] = None
    risk_level: str = "uncertain"
    prediction: str
    probability: float
    confidence: float
    confidence_interval: Optional[List[float]] = None
    explanation: Optional[str] = None
    model_version: str = "3.0.0-calibrated-praat"
    model_architecture: str = "calibrated_praat_rf"
    quality_report: Optional[Dict[str, Any]] = None
    biomarkers: Dict[str, float]
    disclaimer: str
    created_at: str


class ScreeningHistoryList(BaseModel):
    total: int
    items: List[ScreeningHistoryItem]
    disclaimer: str
