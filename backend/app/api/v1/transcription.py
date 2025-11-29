"""Transcription API endpoints."""
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import settings
from app.core.errors import FileValidationError
from app.core.logging import get_logger
from app.models.transcription import (
    HealthResponse,
    JobCreateResponse,
    JobResponse,
    JobStatus,
    ModelSize,
    ModelsResponse,
    TranscriptionRequest,
)
from app.services.job_manager import get_job_manager
from app.services.transcription import get_transcription_service
from app.utils.audio import AudioProcessor
from app.utils.file_handler import FileHandler

logger = get_logger(__name__)

router = APIRouter()


@router.post("/transcribe/file", response_model=JobCreateResponse)
async def transcribe_file(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(None, description="Source language code"),
    model_size: str = Form("base", description="Whisper model size"),
    enable_diarization: bool = Form(False, description="Enable speaker diarization"),
    num_speakers: Optional[int] = Form(None, description="Number of speakers"),
) -> JobCreateResponse:
    """Upload and transcribe an audio file.

    Args:
        file: Audio file upload
        language: Optional language code
        model_size: Whisper model size
        enable_diarization: Enable speaker diarization
        num_speakers: Number of speakers for diarization

    Returns:
        Job creation response with job ID

    Raises:
        FileValidationError: If file validation fails
    """
    # Log detailed file info for debugging
    logger.info(f"Received transcription request for file: {file.filename}")
    logger.info(f"File content_type: {file.content_type}, size: {file.size}")
    
    # Read file content to check if it's actually there
    file_content = await file.read()
    content_length = len(file_content) if file_content else 0
    logger.info(f"Actual content length read: {content_length} bytes")
    
    # Reset file position for later use
    await file.seek(0)
    
    if content_length == 0:
        raise FileValidationError(
            message="Empty file received",
            details="The uploaded file contains no data. This may be a browser or network issue.",
            filename=file.filename,
            suggestions=[
                "Try refreshing the page and uploading again",
                "Check if the file is accessible on your system",
                "Try a different browser",
            ],
        )

    # Validate file size before saving
    if file.size and not FileHandler.validate_file_size(file.size):
        file_size_mb = file.size / (1024 * 1024)
        raise FileValidationError(
            message="File too large",
            details=f"File size is {file_size_mb:.1f}MB, maximum allowed is {settings.MAX_UPLOAD_SIZE}MB",
            filename=file.filename,
            file_size_mb=file_size_mb,
            suggestions=[
                "Compress the audio file before uploading",
                "Split the audio into smaller segments",
                "Use a lower quality encoding",
            ],
        )

    # Validate file extension before saving
    if file.filename:
        from pathlib import Path
        ext = Path(file.filename).suffix.lower()
        if ext not in AudioProcessor.SUPPORTED_FORMATS:
            raise FileValidationError(
                message=f"Unsupported file format: {ext}",
                details=f"The file extension {ext} is not supported",
                filename=file.filename,
                expected_formats=AudioProcessor.SUPPORTED_FORMATS_LIST,
                suggestions=[
                    f"Convert to a supported format: {', '.join(AudioProcessor.SUPPORTED_FORMATS_LIST)}",
                    "Use ffmpeg to convert: ffmpeg -i input_file output.wav",
                ],
            )

    # Generate unique filename and save
    unique_filename = FileHandler.generate_unique_filename(file.filename or "audio.wav")
    file_path = await FileHandler.save_upload_file(
        file.file,
        unique_filename,
        settings.UPLOAD_DIR,
    )

    # Validate audio file with detailed error reporting
    try:
        AudioProcessor.validate_audio_file_detailed(file_path)
    except FileValidationError:
        # Cleanup file and re-raise
        AudioProcessor.cleanup_file(file_path)
        raise

    # Create transcription request
    try:
        transcription_request = TranscriptionRequest(
            language=language,
            model_size=ModelSize(model_size),
            enable_diarization=enable_diarization,
            num_speakers=num_speakers,
        )
    except ValueError as e:
        AudioProcessor.cleanup_file(file_path)
        raise FileValidationError(f"Invalid parameters: {str(e)}")

    # Create job
    job_manager = get_job_manager()
    job_id = job_manager.create_job(
        job_type="transcription",
        file_path=file_path,
        parameters=transcription_request.model_dump(),
    )

    # Submit job for processing
    job_manager.submit_transcription_job(
        job_id=job_id,
        file_path=file_path,
        request=transcription_request,
    )

    logger.info(f"Created transcription job {job_id}")

    return JobCreateResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Transcription job created and queued for processing",
    )


@router.get("/transcribe/job/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    """Get transcription job status and result.

    Args:
        job_id: Job ID to query

    Returns:
        Job status and result if completed

    Raises:
        JobNotFoundError: If job doesn't exist
    """
    logger.debug(f"Fetching status for job {job_id}")
    job_manager = get_job_manager()
    return job_manager.get_job(job_id)


@router.get("/models", response_model=ModelsResponse)
async def get_models() -> ModelsResponse:
    """Get information about available models.

    Returns:
        Available models and supported languages
    """
    service = get_transcription_service()

    return ModelsResponse(
        whisper_models=service.get_available_models(),
        current_model=service.model_size,
        supported_languages=service.get_supported_languages(),
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check for transcription service.

    Returns:
        Service health status
    """
    return HealthResponse(
        status="healthy",
        services={
            "transcription": "ready",
            "diarization": "disabled" if not settings.ENABLE_DIARIZATION else "ready",
            "translation": "disabled" if not settings.ENABLE_TRANSLATION else "ready",
        },
        version="0.1.0",
    )
