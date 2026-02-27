"""
storage/database.py
--------------------
SQLAlchemy engine and session management for FacePass.

Connection parameters are read from ``settings.database_url`` so they
can be overridden via environment variables without touching code.

Usage in FastAPI route handlers — use ``get_db`` as a dependency::

    from storage.database import get_db

    @app.get("/example")
    def example(db = Depends(get_db)):
        ...
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from configs.settings import settings

logger = logging.getLogger(__name__)

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,   # verify connection health before handing it out
    echo=False,           # set to True to log all SQL (verbose, dev-only)
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

from storage.models import Base
Base.metadata.create_all(bind=engine)

# ── Session helpers ───────────────────────────────────────────────────────────

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager that yields a SQLAlchemy session and auto-closes it.

    Example::

        with get_db() as db:
            results = db.query(FaceEmbedding).all()
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Database session rolled back due to error")
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """Return *True* if the database is reachable, *False* otherwise."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("Database connectivity check failed")
        return False
