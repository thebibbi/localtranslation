"""FastAPI application entry point."""
import warnings
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Suppress audio library warnings BEFORE any imports
warnings.filterwarnings("ignore", message=".*MPEG_LAYER_III subtype.*")
warnings.filterwarnings("ignore", message=".*torchaudio._backend.set_audio_backend.*")
warnings.filterwarnings("ignore", category=SyntaxWarning)  # pyannote regex warnings

# Suppress C-level warnings from libmpg123
os.environ["PYTHONWARNINGS"] = "ignore"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import transcription
from app.core.config import settings
from app.core.errors import SpeechProcessingException
from app.core.logging import get_logger, setup_logging
from app.services.job_manager import get_job_manager

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager.

    Args:
        app: FastAPI application instance

    Yields:
        Control back to the application
    """
    # Startup
    logger.info("Starting Speech Processing API")
    settings.ensure_directories()
    logger.info("Application directories initialized")

    yield

    # Shutdown
    logger.info("Shutting down Speech Processing API")
    job_manager = get_job_manager()
    await job_manager.shutdown()


# Create FastAPI application
app = FastAPI(
    title="Speech Processing API",
    description="STT, Diarization, and Translation services",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(SpeechProcessingException)
async def speech_processing_exception_handler(
    request: Request,
    exc: SpeechProcessingException,
) -> JSONResponse:
    """Handle custom speech processing exceptions.

    Args:
        request: The request that caused the exception
        exc: The exception instance

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=400,
        content={"error": exc.to_dict()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: The request that caused the exception
        exc: The exception instance

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None,
            }
        },
    )


# Include routers
app.include_router(
    transcription.router,
    prefix=settings.API_V1_PREFIX,
    tags=["transcription"],
)


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "services": {
            "transcription": "ready",
            "diarization": "disabled" if not settings.ENABLE_DIARIZATION else "ready",
            "translation": "disabled" if not settings.ENABLE_TRANSLATION else "ready",
        },
        "version": "0.1.0",
    }


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint.

    Returns:
        Welcome message and API information
    """
    return {
        "message": "Speech Processing API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
