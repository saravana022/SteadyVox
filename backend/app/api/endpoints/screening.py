"""SteadyVox Voice Screening API Endpoints.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import ScreeningSession
from backend.app.schemas.screening import ScreeningResponse, BiomarkersSchema
from backend.app.services.inference import inference_service
from backend.app.services.storage import storage_service

router = APIRouter()

ALLOWED_AUDIO_TYPES = [
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/flac", "audio/x-flac",
    "audio/ogg", "audio/webm",
    "application/octet-stream", # for raw audio recordings
]


@router.post(
    "/upload",
    response_model=ScreeningResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Screen audio recording for Parkinson's Disease vocal indicators",
    description="Uploads a sustained vowel phonation recording (/a/ or /o/), runs acoustic biomarker extraction and CNN+BiLSTM inference, persists results, and stores raw audio.",
)
async def screen_audio_upload(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, FLAC) containing sustained phonation"),
    patient_identifier: Optional[str] = Form(None, description="Optional anonymized patient or participant ID"),
    db: AsyncSession = Depends(get_db),
):
    # Validate filename extension or content type
    filename = file.filename or "recording.wav"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["wav", "mp3", "flac", "ogg", "webm", "m4a"] and file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Please upload a WAV, MP3, or FLAC audio file. (Notice: {settings.DISCLAIMER_TEXT})",
        )

    # Read audio bytes
    audio_bytes = await file.read()
    if len(audio_bytes) < 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is too short or empty. Please provide at least 1-3 seconds of audio.",
        )

    # 1. Run inference & feature extraction
    try:
        result = inference_service.run_screening(audio_bytes, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process audio: {str(e)}. Ensure the recording contains audible speech.",
        )

    # 2. Upload raw audio to S3 / MinIO storage
    s3_key = storage_service.upload_audio(audio_bytes, filename)
    audio_url = storage_service.get_presigned_url(s3_key)

    # 3. Persist session metadata into PostgreSQL
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    db_session = ScreeningSession(
        id=session_id,
        patient_identifier=patient_identifier or f"PATIENT-{session_id[:8].upper()}",
        audio_s3_key=s3_key,
        original_filename=filename,
        prediction=result["prediction"],
        probability=result["probability"],
        confidence=result["confidence"],
        model_architecture=result["model_architecture"],
        biomarkers=result["biomarkers"],
        disclaimer=settings.DISCLAIMER_TEXT,
        created_at=now,
    )

    try:
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
    except Exception as e:
        await db.rollback()
        print(f"Database save warning (proceeding): {e}")

    return ScreeningResponse(
        session_id=session_id,
        patient_identifier=db_session.patient_identifier,
        original_filename=filename,
        prediction=result["prediction"],
        probability=result["probability"],
        confidence=result["confidence"],
        model_architecture=result["model_architecture"],
        biomarkers=BiomarkersSchema(**result["biomarkers"]),
        audio_url=audio_url,
        latency_ms=result["latency_ms"],
        disclaimer=settings.DISCLAIMER_TEXT,
        created_at=now.isoformat(),
    )

@router.post(
    "/",
    response_model=ScreeningResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Screen audio recording (alias for /upload)",
    description="Accepts an audio file and runs the dual‑path inference, persisting the result. This endpoint mirrors the existing `/upload` path for compatibility.",
)
async def screen_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, FLAC) containing sustained phonation"),
    patient_identifier: Optional[str] = Form(None, description="Optional anonymized patient or participant ID"),
    db: AsyncSession = Depends(get_db),
):
    # Reuse the existing upload handler logic
    return await screen_audio_upload(file=file, patient_identifier=patient_identifier, db=db)
