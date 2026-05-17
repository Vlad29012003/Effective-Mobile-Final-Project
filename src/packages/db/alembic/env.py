import importlib
from logging.config import fileConfig
from typing import cast

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from configs.settings import Settings
from framework.discovery.core import discover_app_paths
from packages.db.base import Base

settings = Settings()

# Auto-import all app models so Base.metadata is populated for autogenerate
for app_path in discover_app_paths():
    try:
        importlib.import_module(f"{app_path}.models")
    except (ImportError, ModuleNotFoundError):
        pass

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)


def get_database_url() -> str:
    url = settings.get_database_url()
    # Alembic runs sync migrations — replace async driver with psycopg2
    return url.replace("+asyncpg", "+psycopg2")


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = alembic_config.get_section(alembic_config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=cast(Connection, connection),
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
