"""Audio processing utilities."""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import soundfile as sf
from pydub import AudioSegment

from app.core.errors import AudioProcessingError, FileValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioValidator:
    """Validates audio files and provides detailed diagnostics."""

    # Magic bytes for common audio formats
    MAGIC_BYTES: Dict[str, List[bytes]] = {
        "mp3": [b"\xff\xfb", b"\xff\xfa", b"\xff\xf3", b"\xff\xf2", b"ID3"],
        "wav": [b"RIFF"],
        "flac": [b"fLaC"],
        "ogg": [b"OggS"],
        "m4a": [b"\x00\x00\x00\x18ftypM4A", b"\x00\x00\x00\x20ftyp", b"ftyp"],
        "aac": [b"\xff\xf1", b"\xff\xf9"],
    }

    @staticmethod
    def detect_file_type(file_path: str) -> Optional[str]:
        """Detect actual file type from magic bytes.

        Args:
            file_path: Path to file

        Returns:
            Detected file type or None if unknown
        """
        try:
            with open(file_path, "rb") as f:
                header = f.read(32)

            for format_name, signatures in AudioValidator.MAGIC_BYTES.items():
                for sig in signatures:
                    if header.startswith(sig) or sig in header[:20]:
                        return format_name

            # Check for ID3 tag (MP3 with metadata)
            if header[:3] == b"ID3":
                return "mp3"

            return None
        except Exception:
            return None

    @staticmethod
    def get_ffprobe_info(file_path: str) -> Dict[str, str]:
        """Get detailed audio info using ffprobe.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio information
        """
        info = {
            "format": "unknown",
            "codec": "unknown",
            "duration": "unknown",
            "sample_rate": "unknown",
            "channels": "unknown",
            "bit_rate": "unknown",
            "error": None,
        }

        try:
            # Check if ffprobe is available
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate,duration",
                    "-show_entries", "format=format_name,duration",
                    "-of", "csv=p=0",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 1:
                    parts = lines[0].split(",")
                    if len(parts) >= 4:
                        info["codec"] = parts[0] if parts[0] else "unknown"
                        info["sample_rate"] = parts[1] if parts[1] else "unknown"
                        info["channels"] = parts[2] if parts[2] else "unknown"
                        info["bit_rate"] = parts[3] if parts[3] else "unknown"
                if len(lines) >= 2:
                    format_parts = lines[1].split(",")
                    if format_parts:
                        info["format"] = format_parts[0]
                    if len(format_parts) >= 2:
                        info["duration"] = format_parts[1]
            else:
                info["error"] = result.stderr.strip() if result.stderr else "Unknown error"

        except subprocess.TimeoutExpired:
            info["error"] = "ffprobe timed out"
        except FileNotFoundError:
            info["error"] = "ffprobe not found - please install ffmpeg"
        except Exception as e:
            info["error"] = str(e)

        return info

    @staticmethod
    def diagnose_audio_issue(file_path: str, original_error: str) -> Dict[str, any]:
        """Diagnose audio file issues and provide helpful suggestions.

        Args:
            file_path: Path to problematic audio file
            original_error: The original error message

        Returns:
            Dictionary with diagnosis and suggestions
        """
        path = Path(file_path)
        diagnosis = {
            "filename": path.name,
            "extension": path.suffix.lower(),
            "file_size_mb": 0,
            "detected_type": None,
            "ffprobe_info": {},
            "issues": [],
            "suggestions": [],
        }

        # Get file size
        try:
            diagnosis["file_size_mb"] = path.stat().st_size / (1024 * 1024)
        except Exception:
            diagnosis["issues"].append("Cannot read file size")

        # Detect actual file type
        detected = AudioValidator.detect_file_type(file_path)
        diagnosis["detected_type"] = detected

        # Get ffprobe info
        diagnosis["ffprobe_info"] = AudioValidator.get_ffprobe_info(file_path)

        # Analyze issues
        extension = path.suffix.lower().lstrip(".")

        # Check for format mismatch
        if detected and detected != extension:
            diagnosis["issues"].append(
                f"File extension is .{extension} but actual format appears to be {detected}"
            )
            diagnosis["suggestions"].append(
                f"Try renaming the file to .{detected} extension"
            )

        # Check for corrupted file indicators
        if "Failed to find" in original_error or "Invalid data" in original_error:
            diagnosis["issues"].append("File appears to be corrupted or incomplete")
            diagnosis["suggestions"].extend([
                "Re-download or re-export the original file",
                "Try converting the file using: ffmpeg -i input.mp3 -acodec libmp3lame output.mp3",
                "Check if the file plays correctly in a media player",
            ])

        # Check for empty or very small files
        if diagnosis["file_size_mb"] < 0.001:
            diagnosis["issues"].append("File is empty or nearly empty")
            diagnosis["suggestions"].append("Upload a valid audio file with content")
        elif diagnosis["file_size_mb"] < 0.01:
            diagnosis["issues"].append("File is suspiciously small")
            diagnosis["suggestions"].append("Verify the file contains actual audio content")

        # Check ffprobe errors
        if diagnosis["ffprobe_info"].get("error"):
            ffprobe_error = diagnosis["ffprobe_info"]["error"]
            if "Invalid data" in ffprobe_error:
                diagnosis["issues"].append("Audio data is invalid or corrupted")
            elif "No such file" in ffprobe_error:
                diagnosis["issues"].append("File not found")

        # Add general suggestions if no specific ones
        if not diagnosis["suggestions"]:
            diagnosis["suggestions"] = [
                "Ensure the file is a valid audio file",
                "Try converting to WAV format: ffmpeg -i input.mp3 output.wav",
                "Try a different audio file to verify the system works",
            ]

        return diagnosis


class AudioProcessor:
    """Utility class for audio file processing."""

    SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}
    SUPPORTED_FORMATS_LIST = ["wav", "mp3", "m4a", "flac", "ogg", "aac", "wma"]
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

        if file_size_mb < 0.001:
            return False, "File is empty or too small"

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
            error_msg = str(e)
            # Get detailed diagnosis
            diagnosis = AudioValidator.diagnose_audio_issue(file_path, error_msg)
            
            # Build detailed error message
            issues = "; ".join(diagnosis["issues"]) if diagnosis["issues"] else "Unknown issue"
            return False, f"Cannot read audio file: {issues}"

    @staticmethod
    def validate_audio_file_detailed(file_path: str) -> None:
        """Validate audio file with detailed error reporting.

        Args:
            file_path: Path to audio file

        Raises:
            FileValidationError: If validation fails with detailed info
        """
        path = Path(file_path)
        file_size_mb = 0

        # Check file exists
        if not path.exists():
            raise FileValidationError(
                message="Audio file not found",
                details=f"The file {path.name} does not exist at the specified path",
                filename=path.name,
                suggestions=["Verify the file was uploaded correctly", "Try uploading again"],
            )

        # Get file size
        try:
            file_size_mb = path.stat().st_size / (1024 * 1024)
        except Exception as e:
            raise FileValidationError(
                message="Cannot read file",
                details=str(e),
                filename=path.name,
            )

        # Check file extension
        if path.suffix.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            detected_type = AudioValidator.detect_file_type(file_path)
            raise FileValidationError(
                message=f"Unsupported audio format: {path.suffix}",
                details=f"The file extension {path.suffix} is not in the list of supported formats",
                filename=path.name,
                expected_formats=AudioProcessor.SUPPORTED_FORMATS_LIST,
                actual_format=detected_type,
                file_size_mb=file_size_mb,
                suggestions=[
                    f"Convert to a supported format: {', '.join(AudioProcessor.SUPPORTED_FORMATS_LIST)}",
                    "Use ffmpeg to convert: ffmpeg -i input_file output.wav",
                ],
            )

        # Check file size limits
        if file_size_mb > 500:
            raise FileValidationError(
                message="File too large",
                details=f"File size is {file_size_mb:.1f}MB, maximum allowed is 500MB",
                filename=path.name,
                file_size_mb=file_size_mb,
                suggestions=[
                    "Compress the audio file",
                    "Split into smaller segments",
                    "Use a lower quality encoding",
                ],
            )

        if file_size_mb < 0.001:
            raise FileValidationError(
                message="File is empty",
                details="The uploaded file contains no data",
                filename=path.name,
                file_size_mb=file_size_mb,
                suggestions=["Upload a valid audio file with content"],
            )

        # Detect actual file type
        detected_type = AudioValidator.detect_file_type(file_path)
        extension = path.suffix.lower().lstrip(".")

        # Warn about format mismatch (but don't fail yet)
        if detected_type and detected_type != extension:
            logger.warning(
                f"File extension mismatch: {path.name} has .{extension} extension "
                f"but appears to be {detected_type} format"
            )

        # Try to read the file
        try:
            if path.suffix.lower() == ".wav":
                with sf.SoundFile(file_path) as audio:
                    sample_rate = audio.samplerate
                    duration = len(audio) / sample_rate
                    logger.info(f"WAV file validated: {duration:.1f}s, {sample_rate}Hz")
            else:
                # Use pydub for other formats
                audio = AudioSegment.from_file(file_path)
                duration = len(audio) / 1000.0
                logger.info(f"Audio file validated: {duration:.1f}s, {audio.frame_rate}Hz")

        except Exception as e:
            error_msg = str(e)
            diagnosis = AudioValidator.diagnose_audio_issue(file_path, error_msg)

            # Build a user-friendly error message
            if diagnosis["issues"]:
                main_issue = diagnosis["issues"][0]
            else:
                main_issue = "The file could not be decoded"

            raise FileValidationError(
                message=f"Invalid audio file: {main_issue}",
                details=error_msg,
                filename=path.name,
                expected_formats=AudioProcessor.SUPPORTED_FORMATS_LIST,
                actual_format=diagnosis["detected_type"],
                file_size_mb=file_size_mb,
                suggestions=diagnosis["suggestions"],
            )

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
