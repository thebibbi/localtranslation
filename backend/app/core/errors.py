"""Custom exception classes for the application."""
from typing import Any, Dict, Optional


class SpeechProcessingException(Exception):
    """Base exception for all custom errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[str] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            code: Error code for client identification
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses.

        Returns:
            Dictionary representation of the error
        """
        error_dict: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class AudioProcessingError(SpeechProcessingException):
    """Audio file processing errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize audio processing error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="AUDIO_PROCESSING_ERROR", details=details)


class ModelLoadError(SpeechProcessingException):
    """Model loading errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize model load error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="MODEL_LOAD_ERROR", details=details)


class TranscriptionError(SpeechProcessingException):
    """Transcription errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize transcription error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="TRANSCRIPTION_ERROR", details=details)


class DiarizationError(SpeechProcessingException):
    """Diarization errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize diarization error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="DIARIZATION_ERROR", details=details)


class TranslationError(SpeechProcessingException):
    """Translation errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize translation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="TRANSLATION_ERROR", details=details)


class FileValidationError(SpeechProcessingException):
    """File validation errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize file validation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, code="FILE_VALIDATION_ERROR", details=details)


class JobNotFoundError(SpeechProcessingException):
    """Job not found errors."""

    def __init__(self, job_id: str) -> None:
        """Initialize job not found error.

        Args:
            job_id: ID of the job that was not found
        """
        super().__init__(
            message=f"Job {job_id} not found",
            code="JOB_NOT_FOUND",
            details=f"No job exists with ID: {job_id}",
        )
