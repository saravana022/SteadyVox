"""Unit tests for SteadyVox FastAPI backend endpoints with quality gate, calibrated model & patient intake."""

import io
import numpy as np
import pytest
import soundfile as sf
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings


def generate_test_wav_bytes(duration=2.5, sr=16000) -> bytes:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Phonation tone with harmonic richness
    audio = (
        0.4 * np.sin(2 * np.pi * 220 * t) +
        0.15 * np.sin(2 * np.pi * 440 * t) +
        0.05 * np.sin(2 * np.pi * 660 * t)
    )
    buf = io.BytesIO()
    sf.write(buf, audio.astype(np.float32), sr, format="WAV")
    buf.seek(0)
    return buf.read()


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == settings.PROJECT_NAME
        assert "disclaimer" in data
        assert "not a medical diagnosis" in data["disclaimer"].lower()


@pytest.mark.asyncio
async def test_ready_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["checks"]["primary_model_loaded"] is True


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == settings.PROJECT_NAME
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_patient_intake_and_encryption():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create Patient
        patient_data = {
            "name": "Jane Doe",
            "age": 62,
            "gender": "Female",
            "consent": True,
        }
        res = await client.post("/api/v1/patients", json=patient_data)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["name"] == "Jane Doe"
        assert data["age"] == 62
        assert data["gender"] == "Female"
        patient_id = data["id"]

        # Retrieve Patient
        get_res = await client.get(f"/api/v1/patients/{patient_id}")
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_screen_primary_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register a patient first
        patient_res = await client.post("/api/v1/patients", json={
            "name": "John Smith",
            "age": 55,
            "gender": "Male",
            "consent": True,
        })
        patient_id = patient_res.json()["id"]

        wav_bytes = generate_test_wav_bytes(duration=2.5)
        files = {"file": ("test_phonation.wav", wav_bytes, "audio/wav")}
        data = {"patient_id": patient_id, "consent_given": "true"}

        response = await client.post("/api/v1/screen", files=files, data=data)
        assert response.status_code == 201
        res = response.json()

        assert "session_id" in res
        assert "request_id" in res
        assert "audio_sha256" in res
        assert res["patient_id"] == patient_id
        assert res["patient_name"] == "John Smith"
        assert res["patient_age"] == 55
        assert res["patient_gender"] == "Male"
        assert res["risk_level"] in ["low", "uncertain", "elevated", "ood"]
        assert res["prediction"] in ["parkinsons", "healthy", "inconclusive"]
        assert 0.0 <= res["probability"] <= 1.0
        assert res["confidence"] >= 0.0
        assert res["quality_report"]["is_acceptable"] is True
        assert "primary_model" in res
        assert "Calibrated" in res["primary_model"]["name"]
        assert "biomarkers" in res
        assert "hnr_mean_db" in res["biomarkers"]
        assert "jitter_local_percent" in res["biomarkers"]
        assert "shimmer_local_percent" in res["biomarkers"]
        assert "explanation" in res
        assert res["explanation"] is not None
        assert "disclaimer" in res
        assert "not a medical diagnosis" in res["disclaimer"].lower()
        assert res["latency_ms"] > 0
        assert "stage_latencies" in res


@pytest.mark.asyncio
async def test_quality_gate_rejection_too_short():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate 0.3s audio (below 1.0s minimum requirement)
        wav_bytes = generate_test_wav_bytes(duration=0.3)
        files = {"file": ("short.wav", wav_bytes, "audio/wav")}
        response = await client.post("/api/v1/screen", files=files)
        
        assert response.status_code == 422
        problem = response.json()
        assert "quality_report" in problem
        assert problem["quality_report"]["is_acceptable"] is False
        assert len(problem["quality_report"]["rejection_reasons"]) > 0


@pytest.mark.asyncio
async def test_history_and_deletion_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a screening
        wav_bytes = generate_test_wav_bytes(duration=2.0)
        files = {"file": ("test_lifecycle.wav", wav_bytes, "audio/wav")}
        data = {"patient_identifier": "LIFECYCLE-PATIENT"}
        create_res = await client.post("/api/v1/screen", files=files, data=data)
        assert create_res.status_code == 201
        session_id = create_res.json()["session_id"]

        # Fetch history
        hist_res = await client.get("/api/v1/history?limit=10&offset=0")
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data["total"] >= 1
        ids = [item["id"] for item in hist_data["items"]]
        assert session_id in ids

        # Delete session
        del_res = await client.delete(f"/api/v1/history/{session_id}")
        assert del_res.status_code == 204

        # Verify not found
        get_res = await client.get(f"/api/v1/history/{session_id}")
        assert get_res.status_code == 404
