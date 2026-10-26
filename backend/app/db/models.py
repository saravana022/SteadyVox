"""SteadyVox Database Models.

Stores patient records (encrypted at rest), screening sessions, acoustic biomarkers,
and prediction audits.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.session import Base
from backend.app.core.config import settings
from backend.app.core.security import encrypt_field, decrypt_field


class Patient(Base):
    """Patient entity with sensitive personal identifying information (PII) encrypted at rest."""
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    encrypted_name = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(30), nullable=False)
    consent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to screening sessions
    screenings = relationship("ScreeningSession", back_populates="patient", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        """Decrypts and returns the patient name."""
        return decrypt_field(self.encrypted_name) or "Anonymous"

    @name.setter
    def name(self, val: str):
        """Encrypts and stores the patient name."""
        self.encrypted_name = encrypt_field(val)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "consent_at": self.consent_at.isoformat() if self.consent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True)
    patient_identifier = Column(String(100), nullable=True, index=True)
    audio_sha256 = Column(String(64), nullable=True, index=True)
    audio_s3_key = Column(String(255), nullable=True)
    original_filename = Column(String(255), nullable=False)
    
    # Model predictions & 3-tier risk level
    risk_level = Column(String(20), nullable=False, default="uncertain")  # "low", "uncertain", "elevated", "ood"
    prediction = Column(String(50), nullable=False)                      # "parkinsons" or "healthy"
    probability = Column(Float, nullable=False)                          # Risk probability [0.0, 1.0]
    confidence = Column(Float, nullable=False)                           # Uncertainty / Confidence margin
    confidence_interval = Column(JSON, nullable=True)                    # e.g. [0.18, 0.26]
    model_version = Column(String(50), default=settings.PRIMARY_MODEL_VERSION)
    model_architecture = Column(String(50), default="calibrated_praat_rf")
    explanation = Column(Text, nullable=True)                            # Clinically generated feature explanation
    
    # Quality gate inspection report
    quality_report = Column(JSON, nullable=True)
    
    # Acoustic biomarkers (F0, Jitter, Shimmer, HNR)
    biomarkers = Column(JSON, nullable=False)
    
    # Consent and retention
    consent_given = Column(Boolean, default=True, nullable=False)
    
    # Latency tracking
    latency_ms = Column(Float, nullable=True)
    stage_latencies = Column(JSON, nullable=True)
    
    # Mandatory Research Disclaimer
    disclaimer = Column(Text, default=settings.DISCLAIMER_TEXT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to Patient
    patient = relationship("Patient", back_populates="screenings")

    def to_dict(self):
        p_name = self.patient.name if self.patient else (self.patient_identifier or "Anonymous")
        p_age = self.patient.age if self.patient else None
        p_gender = self.patient.gender if self.patient else None
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_identifier": p_name,
            "patient_name": p_name,
            "patient_age": p_age,
            "patient_gender": p_gender,
            "audio_sha256": self.audio_sha256,
            "audio_s3_key": self.audio_s3_key,
            "original_filename": self.original_filename,
            "risk_level": self.risk_level,
            "prediction": self.prediction,
            "probability": self.probability,
            "confidence": self.confidence,
            "confidence_interval": self.confidence_interval,
            "explanation": self.explanation,
            "model_version": self.model_version,
            "model_architecture": self.model_architecture,
            "quality_report": self.quality_report,
            "biomarkers": self.biomarkers,
            "consent_given": self.consent_given,
            "latency_ms": self.latency_ms,
            "stage_latencies": self.stage_latencies,
            "disclaimer": self.disclaimer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
