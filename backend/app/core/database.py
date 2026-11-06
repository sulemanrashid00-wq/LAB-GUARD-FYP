from typing import Generator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("labguard.database")

Base = declarative_base()

# Supabase PostgreSQL connection URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Auto-adapt PostgreSQL driver for psycopg2
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Primary Engine (Supabase PostgreSQL / Configured DB)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fallback local SQLite engine if remote DB host is unreachable
fallback_engine = create_engine(
    "sqlite:///./lab_guard.db",
    connect_args={"check_same_thread": False}
)
FallbackSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fallback_engine)


def init_local_fallback():
    """Ensure fallback tables exist."""
    try:
        from app.models.device import DeviceModel
        from app.models.telemetry import HeartbeatModel, TelemetryModel
        Base.metadata.create_all(bind=fallback_engine)
    except Exception as e:
        logger.warning(f"Could not initialize fallback tables: {e}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to provide DB session in endpoints.
    Tries primary Supabase DB first; falls back smoothly if host is unreachable.
    """
    try:
        db = SessionLocal()
        db.connection()
        yield db
    except Exception as exc:
        logger.warning(f"Primary database unreachable ({exc}). Using local SQLite fallback.")
        db.close()
        init_local_fallback()
        db_fallback = FallbackSessionLocal()
        try:
            yield db_fallback
        finally:
            db_fallback.close()
        return
    finally:
        db.close()
