from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core Environment
    PROJECT_NAME: str = "SteadyVox"
    VERSION: str = "2.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "steadyvox-dev-secret-key-replace-in-production"

    # Mandatory Research Disclaimer
    DISCLAIMER_TEXT: str = "Research screening tool only — not a medical diagnosis. Consult a qualified neurologist."

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "steadyvox_db"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/steadyvox_db"

    # Object Storage (S3 / MinIO)
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "steadyvox-audio"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Inference & Model Versions
    PRIMARY_MODEL_NAME: str = "Tabular MLP (Clinical Ground Truth)"
    PRIMARY_MODEL_VERSION: str = "2.1.0-oxford"
    PRIMARY_MODEL_PROVENANCE: str = "Oxford Parkinson's Disease Dataset (UCI ML Repository, 195 recordings, Little et al.)"
    SECONDARY_MODEL_NAME: str = "CNN + BiLSTM (Acoustic Spectrogram)"
    SECONDARY_MODEL_VERSION: str = "1.0.0-synthetic-benchmark"
    SECONDARY_MODEL_PROVENANCE: str = "Sustained /a/ biophysical simulation benchmark (600 speakers, synthetic ablation)"
    
    MODEL_PATH: str = "ml/saved_models/tabular_mlp_best.pt"
    AUDIO_MODEL_PATH: str = "ml/saved_models/cnn_bilstm_best.pt"
    SAMPLE_RATE: int = 16000
    AUDIO_DURATION_SECONDS: float = 3.0

    # Risk Calibration Thresholds
    RISK_LOW_THRESHOLD: float = 0.40
    RISK_ELEVATED_THRESHOLD: float = 0.70

    # Quality Gate Rules
    MIN_AUDIO_DURATION_SECONDS: float = 1.0
    MAX_AUDIO_DURATION_SECONDS: float = 12.0
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MIN_SNR_DB: float = 9.0
    MAX_CLIPPING_RATIO: float = 0.03
    MAX_SILENCE_RATIO: float = 0.75

    # Monitoring & Observability
    PROMETHEUS_METRICS_ENABLED: bool = True


settings = Settings()
