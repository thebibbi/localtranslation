"""File handling utilities."""
import os
import uuid
from pathlib import Path
from typing import BinaryIO

import aiofiles

from app.core.config import settings
from app.core.errors import FileValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Utility class for handling file uploads and storage."""

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename preserving the extension.

        Args:
            original_filename: Original uploaded filename

        Returns:
            Unique filename with UUID prefix
        """
        ext = Path(original_filename).suffix
        unique_id = uuid.uuid4().hex[:12]
        safe_name = Path(original_filename).stem[:50]  # Limit length
        return f"{unique_id}_{safe_name}{ext}"

    @staticmethod
    async def save_upload_file(
        file: BinaryIO,
        filename: str,
        destination_dir: str,
    ) -> str:
        """Save an uploaded file to disk.

        Args:
            file: File object to save
            filename: Filename to use
            destination_dir: Directory to save file in

        Returns:
            Full path to saved file

        Raises:
            FileValidationError: If save fails
        """
        try:
            # Ensure directory exists
            Path(destination_dir).mkdir(parents=True, exist_ok=True)

            file_path = os.path.join(destination_dir, filename)

            # Read and save file asynchronously
            async with aiofiles.open(file_path, "wb") as f:
                content = file.read()
                await f.write(content)

            logger.info(f"Saved file to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise FileValidationError(
                "Failed to save uploaded file",
                details=str(e),
            )

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size is within limits.

        Args:
            file_size: File size in bytes

        Returns:
            True if valid, False otherwise
        """
        max_size_bytes = settings.MAX_UPLOAD_SIZE * 1024 * 1024  # Convert MB to bytes
        return file_size <= max_size_bytes

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in megabytes.

        Args:
            file_path: Path to file

        Returns:
            File size in MB
        """
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)

    @staticmethod
    def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
        """Remove files older than specified age.

        Args:
            directory: Directory to clean
            max_age_hours: Maximum file age in hours

        Returns:
            Number of files deleted
        """
        import time

        deleted_count = 0
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()

        try:
            for file_path in Path(directory).glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old file: {file_path}")

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old files from {directory}")

        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")

        return deleted_count
