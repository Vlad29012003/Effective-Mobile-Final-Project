import os
import pathlib

import pytest
from httpx import ASGITransport, AsyncClient

PROJECT_ROOT = pathlib.Path(__file__).parent.parent


def pytest_configure(config: pytest.Config) -> None:
    from testcontainers.postgres import PostgresContainer

    pg: PostgresContainer = PostgresContainer("postgres:16-alpine")
    pg.start()

    sync_url = pg.get_connection_url()
    async_url = sync_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    os.environ.update(
        {
            "DATABASE_URL": async_url,
            "SYNC_DATABASE_URL": sync_url,
            "JWT_SECRET_KEY": "test-secret-key-for-tests-only-1234567890",
            "SENTRY_ENABLED": "false",
            "COOKIE_SECURE": "false",
            "DEBUG": "false",
            "REDIS_URL": "",
        }
    )

    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(str(PROJECT_ROOT / "alembic.ini"))
    alembic_command.upgrade(alembic_cfg, "head")

    config._pg = pg  # type: ignore[attr-defined]


def pytest_unconfigure(config: pytest.Config) -> None:
    pg = getattr(config, "_pg", None)
    if pg is not None:
        pg.stop()


@pytest.fixture(scope="session")
def app():
    from startup.api import create_app

    return create_app()


@pytest.fixture(scope="session")
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    import sqlalchemy as sa

    from configs import settings

    engine = sa.create_engine(settings.get_sync_database_url())
    with engine.connect() as conn:
        conn.execute(
            sa.text(
                "TRUNCATE meetings, evaluations, comments, tasks,"
                " team_members, teams, refresh_tokens, users"
                " RESTART IDENTITY CASCADE"
            )
        )
        conn.commit()
    engine.dispose()
