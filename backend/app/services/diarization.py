"""Speaker diarization service using pyannote.audio."""
import os
import sys
import warnings
from contextlib import contextmanager
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.errors import DiarizationError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Suppress warnings from pyannote and torchaudio
warnings.filterwarnings("ignore", message=".*MPEG_LAYER_III subtype.*")
warnings.filterwarnings("ignore", message=".*torchaudio._backend.set_audio_backend.*")
warnings.filterwarnings("ignore", category=SyntaxWarning)


@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output (C-level warnings)."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


class SpeakerSegment:
    """A segment of audio attributed to a speaker."""
    
    def __init__(self, speaker: str, start: float, end: float):
        self.speaker = speaker
        self.start = start
        self.end = end


class DiarizationService:
    """Service for speaker diarization using pyannote.audio."""

    def __init__(self) -> None:
        """Initialize diarization service."""
        self.pipeline: Optional["Pipeline"] = None
        self.auth_token = settings.PYANNOTE_AUTH_TOKEN if hasattr(settings, 'PYANNOTE_AUTH_TOKEN') else None
        
        
    def is_available(self) -> bool:
        """Check if diarization is available."""
        try:
            with suppress_stderr():
                from pyannote.audio import Pipeline
            return bool(self.auth_token)
        except ImportError:
            return False

    def load_pipeline(self) -> None:
        """Load the pyannote diarization pipeline.
        
        Raises:
            DiarizationError: If pipeline fails to load
        """
        try:
            with suppress_stderr():
                from pyannote.audio import Pipeline
        except ImportError:
            raise DiarizationError(
                "pyannote.audio is not installed",
                details="Install with: uv pip install 'speech-processing-backend[diarization]'",
            )

        if not self.auth_token:
            raise DiarizationError(
                "Pyannote authentication token not configured",
                details="Set PYANNOTE_AUTH_TOKEN in your .env file. "
                        "Get a token from https://huggingface.co/pyannote/speaker-diarization-3.1",
            )

        try:
            logger.info("Loading pyannote diarization pipeline...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.auth_token,
            )
            logger.info("Diarization pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load diarization pipeline: {str(e)}")
            raise DiarizationError(
                "Failed to load diarization pipeline",
                details=str(e),
            )

    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> List[SpeakerSegment]:
        """Perform speaker diarization on an audio file.
        
        Args:
            audio_path: Path to the audio file
            num_speakers: Optional number of speakers (auto-detect if None)
            
        Returns:
            List of SpeakerSegment objects
            
        Raises:
            DiarizationError: If diarization fails
        """
        if self.pipeline is None:
            self.load_pipeline()

        try:
            logger.info(f"Starting diarization of {audio_path} (num_speakers={num_speakers})")
            
            # Run diarization with stderr suppressed to avoid C-level warnings
            with suppress_stderr():
                if num_speakers:
                    diarization = self.pipeline(audio_path, num_speakers=num_speakers)
                else:
                    diarization = self.pipeline(audio_path)

            # Convert to our format
            segments: List[SpeakerSegment] = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append(SpeakerSegment(
                    speaker=speaker,
                    start=turn.start,
                    end=turn.end,
                ))

            logger.info(f"Diarization completed: {len(segments)} speaker segments found")
            return segments

        except Exception as e:
            logger.error(f"Diarization failed: {str(e)}")
            raise DiarizationError(
                "Failed to perform speaker diarization",
                details=str(e),
            )

    def assign_speakers_to_segments(
        self,
        transcription_segments: List[dict],
        speaker_segments: List[SpeakerSegment],
    ) -> List[dict]:
        """Assign speaker labels to transcription segments.
        
        Uses overlap-based assignment: each transcription segment is assigned
        to the speaker with the most overlap.
        
        Args:
            transcription_segments: List of transcription segment dicts with 'start' and 'end'
            speaker_segments: List of SpeakerSegment objects from diarization
            
        Returns:
            Updated transcription segments with 'speaker' field
        """
        for trans_seg in transcription_segments:
            trans_start = trans_seg["start"]
            trans_end = trans_seg["end"]
            
            # Find speaker with maximum overlap
            best_speaker = None
            best_overlap = 0.0
            
            for spk_seg in speaker_segments:
                # Calculate overlap
                overlap_start = max(trans_start, spk_seg.start)
                overlap_end = min(trans_end, spk_seg.end)
                overlap = max(0.0, overlap_end - overlap_start)
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = spk_seg.speaker
            
            trans_seg["speaker"] = best_speaker
        
        return transcription_segments


# Global service instance
_diarization_service: Optional[DiarizationService] = None


def get_diarization_service() -> DiarizationService:
    """Get or create the global diarization service instance.
    
    Returns:
        DiarizationService instance
    """
    global _diarization_service
    if _diarization_service is None:
        _diarization_service = DiarizationService()
    return _diarization_service


def is_diarization_available() -> bool:
    """Check if diarization is available.
    
    Returns:
        True if pyannote.audio is installed and configured
    """
    service = get_diarization_service()
    return service.is_available()
