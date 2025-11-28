#!/usr/bin/env python3
"""Script to initialize the database."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine

from app.core.config import settings
from app.schemas.job import Base


def setup_database() -> None:
    """Initialize database tables."""
    print("\n" + "="*60)
    print("Database Setup")
    print("="*60)
    print(f"\nDatabase URL: {settings.DATABASE_URL}")

    # Ensure storage directory exists
    storage_dir = Path(settings.DATABASE_URL.replace("sqlite:///", "")).parent
    storage_dir.mkdir(parents=True, exist_ok=True)
    print(f"Storage directory: {storage_dir}")

    # Create engine and tables
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    )

    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)

    print("✓ Database tables created successfully")
    print("\nTables:")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")

    print("\n" + "="*60)
    print("Database setup complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    setup_database()
