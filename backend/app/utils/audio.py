"""Audio processing utilities."""
import os
from pathlib import Path
from typing import List, Tuple

import soundfile as sf
from pydub import AudioSegment

from app.core.errors import AudioProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioProcessor:
    """Utility class for audio file processing."""

    SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}
    TARGET_SAMPLE_RATE = 16000  # Whisper requirement

    @staticmethod
    def validate_audio_file(file_path: str) -> Tuple[bool, str]:
        """Validate audio file format and readability.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (is_valid, message)
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            return False, "File does not exist"

        # Check file extension
        if path.suffix.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {path.suffix}"

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 500:  # 500MB limit
            return False, f"File too large: {file_size_mb:.1f}MB (max 500MB)"

        # Try to read the file
        try:
            if path.suffix.lower() == ".wav":
                with sf.SoundFile(file_path) as audio:
                    _ = audio.samplerate
            else:
                # Use pydub for other formats
                audio = AudioSegment.from_file(file_path)
                _ = audio.frame_rate
            return True, "Valid audio file"
        except Exception as e:
            return False, f"Cannot read audio file: {str(e)}"

    @staticmethod
    async def convert_to_wav(input_path: str, output_dir: str) -> str:
        """Convert audio file to WAV format.

        Args:
            input_path: Path to input audio file
            output_dir: Directory for output file

        Returns:
            Path to converted WAV file

        Raises:
            AudioProcessingError: If conversion fails
        """
        try:
            input_path_obj = Path(input_path)
            output_path = Path(output_dir) / f"{input_path_obj.stem}.wav"

            logger.info(f"Converting {input_path} to WAV format")

            # If already WAV, just return the path
            if input_path_obj.suffix.lower() == ".wav":
                return input_path

            # Convert using pydub
            audio = AudioSegment.from_file(input_path)
            audio.export(
                str(output_path),
                format="wav",
                parameters=["-ar", str(AudioProcessor.TARGET_SAMPLE_RATE)],
            )

            logger.info(f"Converted to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise AudioProcessingError(
                "Failed to convert audio to WAV format",
                details=str(e),
            )

    @staticmethod
    async def resample_audio(input_path: str, output_path: str, target_sr: int = 16000) -> str:
        """Resample audio to target sample rate.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            target_sr: Target sample rate in Hz

        Returns:
            Path to resampled audio file

        Raises:
            AudioProcessingError: If resampling fails
        """
        try:
            logger.info(f"Resampling {input_path} to {target_sr}Hz")

            # Read audio
            audio = AudioSegment.from_file(input_path)

            # Resample
            audio = audio.set_frame_rate(target_sr)

            # Export
            audio.export(output_path, format="wav")

            logger.info(f"Resampled to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Audio resampling failed: {str(e)}")
            raise AudioProcessingError(
                "Failed to resample audio",
                details=str(e),
            )

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Get audio file duration in seconds.

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds

        Raises:
            AudioProcessingError: If duration cannot be determined
        """
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            logger.error(f"Failed to get audio duration: {str(e)}")
            raise AudioProcessingError(
                "Failed to get audio duration",
                details=str(e),
            )

    @staticmethod
    def chunk_audio(
        file_path: str,
        output_dir: str,
        chunk_duration_ms: int = 30000,
    ) -> List[str]:
        """Split audio into smaller chunks.

        Args:
            file_path: Path to audio file
            output_dir: Directory for output chunks
            chunk_duration_ms: Chunk duration in milliseconds

        Returns:
            List of paths to audio chunks

        Raises:
            AudioProcessingError: If chunking fails
        """
        try:
            logger.info(f"Chunking audio file: {file_path}")

            audio = AudioSegment.from_file(file_path)
            chunks = []

            # Calculate number of chunks
            total_duration = len(audio)
            num_chunks = (total_duration + chunk_duration_ms - 1) // chunk_duration_ms

            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            file_stem = Path(file_path).stem

            for i in range(num_chunks):
                start = i * chunk_duration_ms
                end = min((i + 1) * chunk_duration_ms, total_duration)

                chunk = audio[start:end]
                chunk_path = output_dir_path / f"{file_stem}_chunk_{i:03d}.wav"

                chunk.export(str(chunk_path), format="wav")
                chunks.append(str(chunk_path))

            logger.info(f"Created {len(chunks)} audio chunks")
            return chunks

        except Exception as e:
            logger.error(f"Audio chunking failed: {str(e)}")
            raise AudioProcessingError(
                "Failed to chunk audio file",
                details=str(e),
            )

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Delete a file safely.

        Args:
            file_path: Path to file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")
