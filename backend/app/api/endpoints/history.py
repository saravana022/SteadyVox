"""SteadyVox Screening History and Audio Retrieval Endpoints.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse, StreamingResponse
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import ScreeningSession
from backend.app.schemas.screening import ScreeningHistoryList, ScreeningHistoryItem
from backend.app.services.storage import storage_service

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

        # Query items
        items_stmt = (
            select(ScreeningSession)
            .order_by(desc(ScreeningSession.created_at))
            .offset(offset)
            .limit(limit)
        )
        items_res = await db.execute(items_stmt)
        sessions = items_res.scalars().all()

        items = [
            ScreeningHistoryItem(
                id=s.id,
                patient_identifier=s.patient_identifier,
                original_filename=s.original_filename,
                prediction=s.prediction,
                probability=s.probability,
                confidence=s.confidence,
                model_architecture=s.model_architecture,
                biomarkers=s.biomarkers,
                disclaimer=s.disclaimer or settings.DISCLAIMER_TEXT,
                created_at=s.created_at.isoformat() if s.created_at else "",
            )
            for s in sessions
        ]
        return ScreeningHistoryList(total=total, items=items, disclaimer=settings.DISCLAIMER_TEXT)
    except Exception as e:
        # If database table is empty or error, return empty list gracefully
        return ScreeningHistoryList(total=0, items=[], disclaimer=settings.DISCLAIMER_TEXT)


@router.get(
    "/{session_id}",
    response_model=ScreeningHistoryItem,
    summary="Retrieve single screening session details",
)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScreeningSession).where(ScreeningSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening session '{session_id}' not found. (Notice: {settings.DISCLAIMER_TEXT})",
        )

    return ScreeningHistoryItem(
        id=session.id,
        patient_identifier=session.patient_identifier,
        original_filename=session.original_filename,
        prediction=session.prediction,
        probability=session.probability,
        confidence=session.confidence,
        model_architecture=session.model_architecture,
        biomarkers=session.biomarkers,
        disclaimer=session.disclaimer or settings.DISCLAIMER_TEXT,
        created_at=session.created_at.isoformat() if session.created_at else "",
    )


@router.get(
    "/{session_id}/audio",
    summary="Retrieve audio playback for a session",
)
async def get_session_audio(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScreeningSession).where(ScreeningSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session or not session.audio_s3_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

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
