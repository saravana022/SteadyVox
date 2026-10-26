"""SteadyVox Patient Intake and Privacy API Endpoints.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.db.session import get_db
from backend.app.db.models import Patient
from backend.app.schemas.screening import PatientCreate, PatientResponse, ProblemDetail

router = APIRouter()


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Patient Intake Record",
    description="Registers participant intake details with field-level encryption for sensitive identifying data.",
)
async def create_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    patient = Patient(
        id=patient_id,
        age=payload.age,
        gender=payload.gender,
        consent_at=now,
        created_at=now,
    )
    # Uses encrypted setter
    patient.name = payload.name

    try:
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist patient intake record: {str(e)}",
        )

    return PatientResponse(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        consent_at=patient.consent_at.isoformat() if patient.consent_at else now.isoformat(),
        created_at=patient.created_at.isoformat() if patient.created_at else now.isoformat(),
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get Patient Record",
    description="Retrieves decrypted patient record by UUID.",
)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None)))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    return PatientResponse(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        consent_at=patient.consent_at.isoformat() if patient.consent_at else "",
        created_at=patient.created_at.isoformat() if patient.created_at else "",
    )
