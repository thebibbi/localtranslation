"""Pydantic models for transcription requests and responses."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ModelSize(str, Enum):
    """Whisper model size options."""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class JobStatus(str, Enum):
    """Job processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Word(BaseModel):
    """Individual word in transcription with timing."""

    word: str = Field(..., description="The word text")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class TranscriptionSegment(BaseModel):
    """A segment of transcribed audio."""

    id: int = Field(..., description="Segment ID")
    text: str = Field(..., description="Transcribed text")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    speaker: Optional[str] = Field(None, description="Speaker label (if diarization enabled)")
    words: Optional[List[Word]] = Field(None, description="Word-level timestamps")


class TranscriptionRequest(BaseModel):
    """Request parameters for transcription."""

    model_config = {"protected_namespaces": ()}  # Allow model_size field name

    language: Optional[str] = Field(None, description="Source language code (e.g., 'en', 'es')")
    model_size: ModelSize = Field(ModelSize.BASE, description="Whisper model size")
    enable_diarization: bool = Field(False, description="Enable speaker diarization")
    num_speakers: Optional[int] = Field(None, ge=1, description="Number of speakers (optional)")


class TranscriptionResult(BaseModel):
    """Complete transcription result."""

    text: str = Field(..., description="Full transcription text")
    segments: List[TranscriptionSegment] = Field(..., description="Transcription segments")
    language: str = Field(..., description="Detected or specified language")
    duration: float = Field(..., description="Audio duration in seconds")


class JobResponse(BaseModel):
    """Response for job status queries."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: int = Field(0, ge=0, le=100, description="Processing progress percentage")
    result: Optional[TranscriptionResult] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")


class JobCreateResponse(BaseModel):
    """Response when creating a new job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service health status")
    services: dict = Field(..., description="Individual service statuses")
    version: str = Field(..., description="API version")


class ModelsResponse(BaseModel):
    """Available models response."""

    model_config = {"protected_namespaces": ()}  # Allow current_model field name

    whisper_models: List[str] = Field(..., description="Available Whisper model sizes")
    current_model: str = Field(..., description="Currently loaded model")
    supported_languages: List[str] = Field(..., description="Supported language codes")
