"""Transcription service using faster-whisper."""
import asyncio
from typing import List, Optional

from faster_whisper import WhisperModel

from app.core.config import settings
from app.core.errors import ModelLoadError, TranscriptionError
from app.core.logging import get_logger
from app.models.transcription import (
    ModelSize,
    TranscriptionResult,
    TranscriptionSegment,
    Word,
)

logger = get_logger(__name__)


class TranscriptionService:
    """Service for transcribing audio using Whisper."""

    def __init__(self, model_size: Optional[str] = None) -> None:
        """Initialize transcription service with Whisper model.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        self.compute_type = settings.WHISPER_COMPUTE_TYPE
        self.model: Optional[WhisperModel] = None

        logger.info(
            f"Initializing TranscriptionService with model={self.model_size}, "
            f"device={self.device}, compute_type={self.compute_type}"
        )

    def load_model(self) -> None:
        """Load the Whisper model into memory.

        Raises:
            ModelLoadError: If model fails to load
        """
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info(f"Successfully loaded Whisper model: {self.model_size}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise ModelLoadError(
                f"Failed to load Whisper model {self.model_size}",
                details=str(e),
            )

    async def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Source language code (auto-detect if None)

        Returns:
            TranscriptionResult with text and segments

        Raises:
            TranscriptionError: If transcription fails
        """
        if self.model is None:
            self.load_model()

        try:
            logger.info(f"Starting transcription of {audio_path} (language={language})")

            # Run transcription in thread pool to avoid blocking
            segments, info = await asyncio.to_thread(
                self._transcribe_sync,
                audio_path,
                language,
            )

            # Convert segments to our model format
            transcription_segments: List[TranscriptionSegment] = []
            full_text_parts: List[str] = []

            for idx, segment in enumerate(segments):
                # Extract words if available
                words: Optional[List[Word]] = None
                if hasattr(segment, "words") and segment.words:
                    words = [
                        Word(
                            word=word.word,
                            start=word.start,
                            end=word.end,
                            confidence=word.probability,
                        )
                        for word in segment.words
                    ]

                transcription_segments.append(
                    TranscriptionSegment(
                        id=idx,
                        text=segment.text.strip(),
                        start=segment.start,
                        end=segment.end,
                        confidence=segment.avg_logprob if hasattr(segment, "avg_logprob") else 0.0,
                        words=words,
                    )
                )
                full_text_parts.append(segment.text.strip())

            full_text = " ".join(full_text_parts)
            detected_language = info.language if hasattr(info, "language") else language or "en"
            duration = info.duration if hasattr(info, "duration") else 0.0

            logger.info(
                f"Transcription completed: {len(transcription_segments)} segments, "
                f"language={detected_language}, duration={duration:.2f}s"
            )

            return TranscriptionResult(
                text=full_text,
                segments=transcription_segments,
                language=detected_language,
                duration=duration,
            )

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise TranscriptionError(
                "Failed to transcribe audio file",
                details=str(e),
            )

    def _transcribe_sync(
        self,
        audio_path: str,
        language: Optional[str],
    ) -> tuple:
        """Synchronous transcription call.

        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detect

        Returns:
            Tuple of (segments, info) from faster-whisper
        """
        if self.model is None:
            raise TranscriptionError("Model not loaded")

        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,  # Voice activity detection to remove silence
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        # Convert generator to list to capture all segments
        segments_list = list(segments)

        return segments_list, info

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO language codes
        """
        # Whisper supports 100+ languages
        # This is a subset of the most common ones
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja",
            "ko", "ar", "hi", "tr", "pl", "uk", "ro", "sv", "cs", "da",
            "fi", "no", "sk", "bg", "hr", "sl", "et", "lv", "lt", "el",
            "he", "id", "ms", "th", "vi", "fa", "af", "sq", "am", "hy",
        ]

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available model sizes.

        Returns:
            List of model size names
        """
        return [model.value for model in ModelSize]


# Global service instance (lazy loaded)
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get or create the global transcription service instance.

    Returns:
        TranscriptionService instance
    """
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
