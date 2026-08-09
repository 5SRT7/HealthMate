"""
Database connection management.

Uses SQLAlchemy with SQLite. To switch to PostgreSQL later,
change the DATABASE_URL and engine creation.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# DB file lives next to the app directory
DB_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.environ.get(
    "HEALTHMATE_DB_URL",
    f"sqlite:///{DB_DIR / 'healthmate.db'}"
)

engine = create_engine(DB_PATH, echo=False, connect_args={"check_same_thread": False})
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Create all tables if they don't exist. Safe to call multiple times."""
    import app.database.models  # noqa: ensure models are registered

    Base.metadata.create_all(bind=engine)
    
    # Migration: add messages column to daily_archives (safe to rerun)
    for col in ("messages", "bmi", "weight_kg"):
        try:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE daily_archives ADD COLUMN {col} TEXT"))
                conn.commit()
        except Exception:
            pass
    logger.info("Database initialized at %s", DB_PATH)


def get_session() -> Session:
    """Get a new database session.

    Usage:
        with get_session() as session:
            session.query(...)
    """
    return SessionLocal()


__all__ = ["init_db", "get_session", "Base"]
