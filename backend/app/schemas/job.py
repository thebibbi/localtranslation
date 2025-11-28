"""Database schema for job tracking."""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    """Job database model."""

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # transcription, diarization, translation
    status = Column(String, nullable=False, default="pending")
    progress = Column(Integer, default=0)

    # Input data
    file_path = Column(String, nullable=False)
    parameters = Column(Text)  # JSON string of request parameters

    # Result data
    result_json = Column(Text)  # JSON string of result
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Metadata
    duration = Column(Float)  # Processing duration in seconds

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Store parameters as JSON.

        Args:
            params: Parameters dictionary to store
        """
        self.parameters = json.dumps(params)

    def get_parameters(self) -> Dict[str, Any]:
        """Retrieve parameters from JSON.

        Returns:
            Parameters dictionary
        """
        if self.parameters:
            return json.loads(self.parameters)
        return {}

    def set_result(self, result: Dict[str, Any]) -> None:
        """Store result as JSON.

        Args:
            result: Result dictionary to store
        """
        self.result_json = json.dumps(result)

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Retrieve result from JSON.

        Returns:
            Result dictionary if available, None otherwise
        """
        if self.result_json:
            return json.loads(self.result_json)
        return None
