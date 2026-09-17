"""SteadyVox Database Models.

Stores screening session metadata, acoustic biomarkers, and prediction history.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func

from backend.app.db.session import Base
from backend.app.core.config import settings


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    patient_identifier = Column(String(100), nullable=True, index=True)
    audio_s3_key = Column(String(255), nullable=True)
    original_filename = Column(String(255), nullable=False)
    
    # Model predictions
    prediction = Column(String(50), nullable=False)  # "parkinsons" or "healthy"
    probability = Column(Float, nullable=False)      # Risk probability [0.0, 1.0]
    confidence = Column(Float, nullable=False)       # Prediction confidence [0.5, 1.0]
    model_architecture = Column(String(50), default="cnn_bilstm")
    
    # Acoustic biomarkers (F0, Jitter, Shimmer, HNR)
    biomarkers = Column(JSON, nullable=False)
    
    # Mandatory Research Disclaimer
    disclaimer = Column(Text, default=settings.DISCLAIMER_TEXT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_identifier": self.patient_identifier,
            "audio_s3_key": self.audio_s3_key,
            "original_filename": self.original_filename,
            "prediction": self.prediction,
            "probability": self.probability,
            "confidence": self.confidence,
            "model_architecture": self.model_architecture,
            "biomarkers": self.biomarkers,
            "disclaimer": self.disclaimer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
