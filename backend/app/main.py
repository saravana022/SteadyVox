from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.core.config import settings
from backend.app.db.session import init_db
from backend.app.api.endpoints.screening import router as screening_router
from backend.app.api.endpoints.history import router as history_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    try:
        await init_db()
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Database init warning (running in detached mode): {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Research screening API for vocal biomarkers associated with Parkinson's Disease. "
        f"IMPORTANT NOTICE: {settings.DISCLAIMER_TEXT}"
    ),
    openapi_tags=[
        {"name": "health", "description": "Service health checks and readiness"},
        {"name": "screening", "description": "Voice upload and Parkinson's screening analysis"},
        {"name": "history", "description": "Patient screening history and stored metadata"},
    ],
    lifespan=lifespan,
)

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


@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Service health check endpoint returning system status and research disclaimer."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "disclaimer": settings.DISCLAIMER_TEXT,
    }


@app.get("/", tags=["health"])
async def root():
    """Root entrypoint returning API metadata."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "disclaimer": settings.DISCLAIMER_TEXT,
    }
