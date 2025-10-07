"""Database session utilities.

Provides a synchronous SQLAlchemy engine and session factory bound to the
configured database URL. Also exposes a small context manager helper for
service-layer usage and a FastAPI-friendly `get_db` generator if needed.
"""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from corner_pocket_backend.core.config import settings


# Create a single engine per process. Pre-ping avoids stale connections.
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

# Session factory. Disable autocommit/autoflush for explicit control.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations.

    Example:
        with session_scope() as db:
            db.add(obj)
            db.commit()
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Iterator[Session]:
    """FastAPI dependency to yield a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()







