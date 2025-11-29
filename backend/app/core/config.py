"""Application configuration management."""
import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # ML Models
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    PYANNOTE_AUTH_TOKEN: str = ""  # HuggingFace token for pyannote.audio

    # Storage
    UPLOAD_DIR: str = "./storage/uploads"
    PROCESSED_DIR: str = "./storage/processed"
    CACHE_DIR: str = "./storage/cache"
    MAX_UPLOAD_SIZE: int = 500  # MB

    # Database
    DATABASE_URL: str = "sqlite:///./storage/jobs.db"

    # Job Queue (optional)
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = '["tauri://localhost", "http://localhost:1420"]'

    # Features
    ENABLE_TRANSLATION: bool = False
    ENABLE_DIARIZATION: bool = False
    MAX_CONCURRENT_JOBS: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            return ["*"]

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.UPLOAD_DIR, self.PROCESSED_DIR, self.CACHE_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
