from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool, create_engine
from alembic import context
import os
import sys

config = context.config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base
from app.models.device import DeviceModel
from app.models.telemetry import HeartbeatModel, TelemetryModel
from app.models.user import UserModel

raw_url = settings.DATABASE_URL
if raw_url.startswith("postgresql://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

config.set_main_option("sqlalchemy.url", raw_url)
target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    try:
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()
    except Exception as exc:
        print(f"\n[Alembic Notice] Remote database connection issue: {exc}")
        print("[Alembic Notice] Applying migration to local SQLite (lab_guard.db) fallback...\n")
        fallback_engine = create_engine(
            "sqlite:///./lab_guard.db",
            connect_args={"check_same_thread": False}
        )
        with fallback_engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata, render_as_batch=True
            )
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
