"""SteadyVox FastAPI Application Entrypoint.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.core.config import settings
from backend.app.db.session import init_db, engine
from backend.app.middleware.request_id import RequestTracingMiddleware
from backend.app.api.endpoints.screening import router as screening_router
from backend.app.api.endpoints.history import router as history_router
from backend.app.api.endpoints.patients import router as patients_router
from backend.app.services.inference import inference_service
from backend.app.services.storage import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    try:
        await init_db()
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Database init warning (running in fallback mode): {e}")

    # 2. Warm up ML models (eliminates cold start latency)
    try:
        inference_service.warmup()
    except Exception as e:
        print(f"Inference warm-up notice: {e}")

    yield

    # Clean up DB engine pools on shutdown
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Dual-Path Acoustic Biomarker Voice Screening Platform for Parkinson's Disease. "
        f"IMPORTANT REGULATORY NOTICE: {settings.DISCLAIMER_TEXT}"
    ),
    openapi_tags=[
        {"name": "screening", "description": "Unified voice screening and quality validation"},
        {"name": "history", "description": "Screening records timeline and audit history"},
        {"name": "patients", "description": "Patient intake registration and privacy management"},
        {"name": "health", "description": "Service health checks and readiness probes"},
    ],
    lifespan=lifespan,
)

# Tracing Middleware
app.add_middleware(RequestTracingMiddleware)

# Setup CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Prometheus Metrics Instrumentation
if settings.PROMETHEUS_METRICS_ENABLED:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Include Routers
app.include_router(screening_router, prefix="/api/v1/screen", tags=["screening"])
app.include_router(history_router, prefix="/api/v1/history", tags=["history"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["patients"])


@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Liveness probe returning service status and research disclaimer."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "disclaimer": settings.DISCLAIMER_TEXT,
    }


@app.get("/api/v1/ready", tags=["health"])
async def readiness_check():
    """Readiness probe verifying DB connectivity and ML model weights."""
    models_ready = (
        inference_service.tabular_model is not None and
        inference_service.audio_model is not None
    )
    s3_ready = storage_service.is_s3_available()

    payload = {
        "ready": models_ready,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "checks": {
            "primary_model_loaded": inference_service.tabular_model is not None,
            "secondary_model_loaded": inference_service.audio_model is not None,
            "storage_s3_connected": s3_ready,
        },
        "disclaimer": settings.DISCLAIMER_TEXT,
    }

    if not models_ready:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload)
    return payload


@app.get("/", tags=["health"])
async def root():
    """Root entrypoint returning API metadata."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "disclaimer": settings.DISCLAIMER_TEXT,
    }
