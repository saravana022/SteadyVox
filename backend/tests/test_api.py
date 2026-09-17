"""Unit tests for SteadyVox FastAPI backend endpoints."""

import io
import numpy as np
import pytest
import soundfile as sf
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings


def generate_test_wav_bytes(duration=1.5, sr=16000) -> bytes:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 220Hz test sine tone with slight harmonics
    audio = 0.5 * np.sin(2 * np.pi * 220 * t) + 0.1 * np.sin(2 * np.pi * 440 * t)
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
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == settings.PROJECT_NAME
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_screen_upload_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        wav_bytes = generate_test_wav_bytes()
        files = {"file": ("test_phonation.wav", wav_bytes, "audio/wav")}
        data = {"patient_identifier": "TEST-PATIENT-001"}

        response = await client.post("/api/v1/screen/upload", files=files, data=data)
        assert response.status_code == 201
        res = response.json()

        assert "session_id" in res
        assert res["patient_identifier"] == "TEST-PATIENT-001"
        assert res["prediction"] in ["parkinsons", "healthy"]
        assert 0.0 <= res["probability"] <= 1.0
        assert 0.5 <= res["confidence"] <= 1.0
        assert "biomarkers" in res
        assert "hnr_mean_db" in res["biomarkers"]
        assert "jitter_local_percent" in res["biomarkers"]
        assert "shimmer_local_percent" in res["biomarkers"]
        assert "disclaimer" in res
        assert "not a medical diagnosis" in res["disclaimer"].lower()
        assert res["latency_ms"] > 0


@pytest.mark.asyncio
async def test_history_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/history?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert "disclaimer" in data
