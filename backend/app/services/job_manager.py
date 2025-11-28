"""Job management service for async task processing."""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.errors import JobNotFoundError
from app.core.logging import get_logger
from app.models.transcription import JobResponse, JobStatus, TranscriptionRequest
from app.schemas.job import Base, Job
from app.services.transcription import get_transcription_service

logger = get_logger(__name__)


class JobManager:
    """Manager for handling transcription jobs."""

    def __init__(self) -> None:
        """Initialize job manager with database connection."""
        self.engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # In-memory job tracking for active jobs
        self.active_jobs: Dict[str, asyncio.Task] = {}

        logger.info("JobManager initialized")

    def create_session(self) -> Session:
        """Create a new database session.

        Returns:
            Database session
        """
        return self.SessionLocal()

    def create_job(
        self,
        job_type: str,
        file_path: str,
        parameters: Dict,
    ) -> str:
        """Create a new job in the database.

        Args:
            job_type: Type of job (transcription, diarization, etc.)
            file_path: Path to audio file
            parameters: Job parameters

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        with self.create_session() as session:
            job = Job(
                id=job_id,
                type=job_type,
                status=JobStatus.PENDING.value,
                file_path=file_path,
            )
            job.set_parameters(parameters)
            session.add(job)
            session.commit()

        logger.info(f"Created job {job_id} of type {job_type}")
        return job_id

    def get_job(self, job_id: str) -> JobResponse:
        """Get job status and result.

        Args:
            job_id: Job ID to query

        Returns:
            JobResponse with current status

        Raises:
            JobNotFoundError: If job doesn't exist
        """
        with self.create_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()

            if not job:
                raise JobNotFoundError(job_id)

            return JobResponse(
                job_id=job.id,
                status=JobStatus(job.status),
                progress=job.progress,
                result=job.get_result(),
                error=job.error_message,
                created_at=job.created_at,
                completed_at=job.completed_at,
            )

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Update job status.

        Args:
            job_id: Job ID to update
            status: New status
            progress: Progress percentage (0-100)
            error: Error message if failed
        """
        with self.create_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = status.value
                job.progress = progress
                if error:
                    job.error_message = error
                if status == JobStatus.PROCESSING and not job.started_at:
                    job.started_at = datetime.utcnow()
                if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    job.completed_at = datetime.utcnow()
                    if job.started_at:
                        duration = (datetime.utcnow() - job.started_at).total_seconds()
                        job.duration = duration
                session.commit()
                logger.debug(f"Updated job {job_id} status to {status.value}")

    def save_job_result(self, job_id: str, result: Dict) -> None:
        """Save job result to database.

        Args:
            job_id: Job ID
            result: Result dictionary
        """
        with self.create_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                job.set_result(result)
                session.commit()
                logger.debug(f"Saved result for job {job_id}")

    async def start_transcription_job(
        self,
        job_id: str,
        file_path: str,
        request: TranscriptionRequest,
    ) -> None:
        """Start a transcription job asynchronously.

        Args:
            job_id: Job ID
            file_path: Path to audio file
            request: Transcription request parameters
        """
        try:
            logger.info(f"Starting transcription job {job_id}")
            self.update_job_status(job_id, JobStatus.PROCESSING, progress=10)

            # Get transcription service
            service = get_transcription_service()

            # Update model size if different from default
            if request.model_size.value != service.model_size:
                service.model_size = request.model_size.value
                service.model = None  # Force reload

            self.update_job_status(job_id, JobStatus.PROCESSING, progress=30)

            # Perform transcription
            result = await service.transcribe_file(
                audio_path=file_path,
                language=request.language,
            )

            self.update_job_status(job_id, JobStatus.PROCESSING, progress=90)

            # Save result
            self.save_job_result(job_id, result.model_dump())

            # Mark as completed
            self.update_job_status(job_id, JobStatus.COMPLETED, progress=100)

            logger.info(f"Completed transcription job {job_id}")

        except Exception as e:
            logger.error(f"Transcription job {job_id} failed: {str(e)}")
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                progress=0,
                error=str(e),
            )

        finally:
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    def submit_transcription_job(
        self,
        job_id: str,
        file_path: str,
        request: TranscriptionRequest,
    ) -> None:
        """Submit a transcription job for background processing.

        Args:
            job_id: Job ID
            file_path: Path to audio file
            request: Transcription request parameters
        """
        task = asyncio.create_task(
            self.start_transcription_job(job_id, file_path, request)
        )
        self.active_jobs[job_id] = task
        logger.info(f"Submitted job {job_id} for processing")

    async def shutdown(self) -> None:
        """Shutdown job manager and cancel active jobs."""
        logger.info("Shutting down JobManager")
        for job_id, task in self.active_jobs.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled active job {job_id}")

        # Wait for all tasks to complete
        if self.active_jobs:
            await asyncio.gather(*self.active_jobs.values(), return_exceptions=True)


# Global job manager instance
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get or create the global job manager instance.

    Returns:
        JobManager instance
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
