"""Custom exception classes for the application."""
from datetime import datetime
from typing import Any, Dict, List, Optional


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
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class AudioProcessingError(SpeechProcessingException):
    """Audio file processing errors."""

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        file_path: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize audio processing error.

        Args:
            message: Error message
            details: Additional error details
            file_path: Path to the problematic file
            suggestions: List of suggestions to fix the issue
        """
        super().__init__(message, code="AUDIO_PROCESSING_ERROR", details=details)
        self.file_path = file_path
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with audio-specific info."""
        error_dict = super().to_dict()
        if self.file_path:
            error_dict["file_path"] = self.file_path
        if self.suggestions:
            error_dict["suggestions"] = self.suggestions
        return error_dict


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

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        filename: Optional[str] = None,
        expected_formats: Optional[List[str]] = None,
        actual_format: Optional[str] = None,
        file_size_mb: Optional[float] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize file validation error.

        Args:
            message: Error message
            details: Additional error details
            filename: Name of the problematic file
            expected_formats: List of expected/supported formats
            actual_format: Detected actual format
            file_size_mb: File size in megabytes
            suggestions: List of suggestions to fix the issue
        """
        super().__init__(message, code="FILE_VALIDATION_ERROR", details=details)
        self.filename = filename
        self.expected_formats = expected_formats
        self.actual_format = actual_format
        self.file_size_mb = file_size_mb
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary with file-specific info."""
        error_dict = super().to_dict()
        if self.filename:
            error_dict["filename"] = self.filename
        if self.expected_formats:
            error_dict["expected_formats"] = self.expected_formats
        if self.actual_format:
            error_dict["actual_format"] = self.actual_format
        if self.file_size_mb is not None:
            error_dict["file_size_mb"] = round(self.file_size_mb, 2)
        if self.suggestions:
            error_dict["suggestions"] = self.suggestions
        return error_dict


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
