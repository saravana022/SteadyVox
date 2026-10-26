"""SteadyVox Screening History, Audio Retrieval, and Deletion Endpoints.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse, StreamingResponse
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import ScreeningSession
from backend.app.schemas.screening import ScreeningHistoryList, ScreeningHistoryItem
from backend.app.services.storage import storage_service

from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get(
    "",
    response_model=ScreeningHistoryList,
    summary="Retrieve paginated screening history",
)
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Count total
        count_stmt = select(func.count(ScreeningSession.id))
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Query items with eager-loaded patient
        items_stmt = (
            select(ScreeningSession)
            .options(selectinload(ScreeningSession.patient))
            .order_by(desc(ScreeningSession.created_at))
            .offset(offset)
            .limit(limit)
        )
        items_res = await db.execute(items_stmt)
        sessions = items_res.scalars().all()

        items = [
            ScreeningHistoryItem(
                id=s.id,
                patient_id=s.patient_id,
                patient_identifier=s.patient.name if s.patient else (s.patient_identifier or "Anonymous"),
                patient_name=s.patient.name if s.patient else (s.patient_identifier or "Anonymous"),
                patient_age=s.patient.age if s.patient else None,
                patient_gender=s.patient.gender if s.patient else None,
                original_filename=s.original_filename,
                audio_sha256=s.audio_sha256,
                risk_level=s.risk_level or "uncertain",
                prediction=s.prediction,
                probability=s.probability,
                confidence=s.confidence,
                confidence_interval=s.confidence_interval,
                explanation=s.explanation,
                model_version=s.model_version or settings.PRIMARY_MODEL_VERSION,
                model_architecture=s.model_architecture,
                quality_report=s.quality_report,
                biomarkers=s.biomarkers,
                disclaimer=s.disclaimer or settings.DISCLAIMER_TEXT,
                created_at=s.created_at.isoformat() if s.created_at else "",
            )
            for s in sessions
        ]
        return ScreeningHistoryList(total=total, items=items, disclaimer=settings.DISCLAIMER_TEXT)
    except Exception as e:
        print(f"History listing fallback: {e}")
        return ScreeningHistoryList(total=0, items=[], disclaimer=settings.DISCLAIMER_TEXT)


@router.get(
    "/{session_id}",
    response_model=ScreeningHistoryItem,
    summary="Retrieve single screening session details",
)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ScreeningSession)
        .options(selectinload(ScreeningSession.patient))
        .where(ScreeningSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening session '{session_id}' not found. (Notice: {settings.DISCLAIMER_TEXT})",
        )

    p_name = session.patient.name if session.patient else (session.patient_identifier or "Anonymous")
    return ScreeningHistoryItem(
        id=session.id,
        patient_id=session.patient_id,
        patient_identifier=p_name,
        patient_name=p_name,
        patient_age=session.patient.age if session.patient else None,
        patient_gender=session.patient.gender if session.patient else None,
        original_filename=session.original_filename,
        audio_sha256=session.audio_sha256,
        risk_level=session.risk_level or "uncertain",
        prediction=session.prediction,
        probability=session.probability,
        confidence=session.confidence,
        confidence_interval=session.confidence_interval,
        explanation=session.explanation,
        model_version=session.model_version or settings.PRIMARY_MODEL_VERSION,
        model_architecture=session.model_architecture,
        quality_report=session.quality_report,
        biomarkers=session.biomarkers,
        disclaimer=session.disclaimer or settings.DISCLAIMER_TEXT,
        created_at=session.created_at.isoformat() if session.created_at else "",
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a screening session record (Privacy right to erasure)",
)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScreeningSession).where(ScreeningSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    del_stmt = delete(ScreeningSession).where(ScreeningSession.id == session_id)
    await db.execute(del_stmt)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{session_id}/audio",
    summary="Retrieve audio playback for a session",
)
async def get_session_audio(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScreeningSession).where(ScreeningSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session or not session.audio_s3_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found or user opted out of retention")

    if storage_service.is_s3_available():
        presigned_url = storage_service.get_presigned_url(session.audio_s3_key)
        return RedirectResponse(url=presigned_url)

    audio_bytes = storage_service.get_audio_bytes(session.audio_s3_key)
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio content unavailable")

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={"Content-Disposition": f"inline; filename={session.original_filename}"},
    )


@router.get("/audio-file", summary="Direct audio stream fallback")
async def stream_audio_file(key: str = Query(...)):
    audio_bytes = storage_service.get_audio_bytes(key)
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=recording.wav"},
    )
