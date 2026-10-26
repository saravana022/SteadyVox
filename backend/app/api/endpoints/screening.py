"""SteadyVox Voice Screening API Endpoints.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    Request,
    BackgroundTasks,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import ScreeningSession, Patient
from backend.app.schemas.screening import (
    ScreeningResponse,
    BiomarkersSchema,
    ModelProvenanceSchema,
    ProblemDetail,
)
from backend.app.services.inference import inference_service
from backend.app.services.storage import storage_service

router = APIRouter()

ALLOWED_AUDIO_TYPES = [
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/flac", "audio/x-flac",
    "audio/ogg", "audio/webm",
    "audio/mp4", "audio/m4a", "audio/x-m4a",
    "application/octet-stream",
]


def _background_upload_audio(audio_bytes: bytes, filename: str, s3_key: str):
    """Background task to store audio to persistent storage."""
    try:
        storage_service.upload_audio(audio_bytes, filename)
    except Exception as e:
        print(f"Background audio storage warning: {e}")


@router.post(
    "",
    response_model=ScreeningResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Primary Voice Screening Endpoint",
    description="Uploads sustained vowel phonation (/a/ or /o/), validates acoustic signal quality, executes clinical dual-path inference, and records session.",
    responses={
        422: {"model": ProblemDetail, "description": "Unusable audio signal (clipping, silence, or high noise)"},
        400: {"model": ProblemDetail, "description": "Invalid format or empty file"},
    },
)
async def screen_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file (WAV, MP3, FLAC, WebM, M4A)"),
    patient_id: Optional[str] = Form(None, description="Optional registered patient UUID"),
    patient_identifier: Optional[str] = Form(None, description="Optional de-identified participant ID"),
    consent_given: bool = Form(True, description="Explicit consent to retain audio for research screening history"),
    explain: bool = Form(False, description="Include detailed feature attribution breakdown"),
    db: AsyncSession = Depends(get_db),
):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    filename = file.filename or "recording.wav"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    # 1. Format validation
    if ext not in ["wav", "mp3", "flac", "ogg", "webm", "m4a", "mp4"] and file.content_type not in ALLOWED_AUDIO_TYPES:
        problem = ProblemDetail(
            type="https://steadyvox.org/errors/unsupported-media-type",
            title="Unsupported Audio Format",
            status=status.HTTP_400_BAD_REQUEST,
            detail=f"Format '{ext or file.content_type}' is not supported. Please provide a WAV, MP3, FLAC, or WebM recording.",
            instance=str(request.url),
            request_id=request_id,
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem.model_dump())

    audio_bytes = await file.read()
    if len(audio_bytes) < 512:
        problem = ProblemDetail(
            type="https://steadyvox.org/errors/payload-too-small",
            title="Empty Audio Payload",
            status=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded audio file is empty or corrupted.",
            instance=str(request.url),
            request_id=request_id,
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem.model_dump())

    if len(audio_bytes) > settings.MAX_FILE_SIZE_BYTES:
        problem = ProblemDetail(
            type="https://steadyvox.org/errors/payload-too-large",
            title="Audio File Too Large",
            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file size exceeds limit of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
            instance=str(request.url),
            request_id=request_id,
        )
        return JSONResponse(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, content=problem.model_dump())

    # Look up patient details if patient_id is provided
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None

    if patient_id:
        try:
            p_res = await db.execute(select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None)))
            pat = p_res.scalar_one_or_none()
            if pat:
                patient_name = pat.name
                patient_age = pat.age
                patient_gender = pat.gender
        except Exception as e:
            print(f"Patient lookup notice: {e}")

    # 2. Run Quality Gate & Calibrated Inference
    try:
        result = inference_service.run_screening(
            audio_bytes,
            filename=filename,
            patient_gender=patient_gender,
            patient_age=patient_age,
        )
    except Exception as e:
        problem = ProblemDetail(
            type="https://steadyvox.org/errors/dsp-processing-failure",
            title="Acoustic Signal Processing Failure",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Acoustic feature extraction encountered an unrecoverable error: {str(e)}",
            instance=str(request.url),
            request_id=request_id,
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=problem.model_dump())

    # 3. Check if audio was rejected by Quality Gate
    if result.get("quality_rejected"):
        q_report = result["quality_report"]
        reasons = "; ".join(q_report.rejection_reasons)
        problem = ProblemDetail(
            type="https://steadyvox.org/errors/audio-quality-degraded",
            title="Acoustic Recording Quality Unusable",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The recorded audio cannot be reliably analyzed: {reasons}",
            instance=str(request.url),
            request_id=request_id,
            quality_report=q_report,
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=problem.model_dump())

    # 4. Storage Handling (with user consent check)
    session_id = str(uuid.uuid4())
    s3_key: Optional[str] = None
    audio_url: Optional[str] = None

    if consent_given:
        ext_dot = f".{ext}" if ext else ".wav"
        s3_key = f"recordings/{session_id}{ext_dot}"
        background_tasks.add_task(_background_upload_audio, audio_bytes, filename, s3_key)
        audio_url = storage_service.get_presigned_url(s3_key)

    # 5. Persist Session Metadata to Database
    now = datetime.now(timezone.utc)
    display_identifier = patient_name or patient_identifier or f"PATIENT-{session_id[:8].upper()}"

    db_session = ScreeningSession(
        id=session_id,
        patient_id=patient_id,
        patient_identifier=display_identifier,
        audio_sha256=result["audio_sha256"],
        audio_s3_key=s3_key if consent_given else None,
        original_filename=filename,
        risk_level=result["risk_level"],
        prediction=result["prediction"],
        probability=result["probability"],
        confidence=result["confidence"],
        confidence_interval=result.get("confidence_interval"),
        explanation=result.get("explanation"),
        model_version=result["primary_model"]["version"],
        model_architecture=result.get("model_architecture", "calibrated_praat_rf"),
        quality_report=result["quality_report"].model_dump(),
        biomarkers=result["biomarkers"],
        consent_given=consent_given,
        latency_ms=result["latency_ms"],
        stage_latencies=result["stage_latencies"],
        disclaimer=settings.DISCLAIMER_TEXT,
        created_at=now,
    )

    try:
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
    except Exception as e:
        await db.rollback()
        print(f"Database session save notice: {e}")

    return ScreeningResponse(
        request_id=request_id,
        session_id=session_id,
        patient_id=patient_id,
        patient_identifier=display_identifier,
        patient_name=patient_name or display_identifier,
        patient_age=patient_age,
        patient_gender=patient_gender,
        original_filename=filename,
        audio_sha256=result["audio_sha256"],
        risk_level=result["risk_level"],
        prediction=result["prediction"],
        probability=result["probability"],
        confidence=result["confidence"],
        confidence_interval=result.get("confidence_interval"),
        explanation=result.get("explanation"),
        quality_report=result["quality_report"],
        ood_status=result.get("ood_status", "in_distribution"),
        path_disagreement=result.get("path_disagreement", False),
        primary_model=ModelProvenanceSchema(**result["primary_model"]),
        secondary_model=ModelProvenanceSchema(**result["secondary_model"]) if result.get("secondary_model") else None,
        biomarkers=BiomarkersSchema(**result["biomarkers"]),
        audio_url=audio_url,
        latency_ms=result["latency_ms"],
        stage_latencies=result["stage_latencies"],
        disclaimer=settings.DISCLAIMER_TEXT,
        created_at=now.isoformat(),
    )


@router.post(
    "/upload",
    response_model=ScreeningResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Screen audio recording (Deprecated - Use POST /api/v1/screen)",
    description="Deprecated compatibility alias for POST /api/v1/screen.",
    deprecated=True,
)
async def screen_audio_upload_deprecated(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    patient_identifier: Optional[str] = Form(None),
    consent_given: bool = Form(True),
    explain: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    return await screen_audio(
        request=request,
        background_tasks=background_tasks,
        file=file,
        patient_id=patient_id,
        patient_identifier=patient_identifier,
        consent_given=consent_given,
        explain=explain,
        db=db,
    )
