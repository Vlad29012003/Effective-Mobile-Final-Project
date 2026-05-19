import asyncio
import os
import pathlib
import sys

import pytest
from httpx import ASGITransport, AsyncClient

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PROJECT_ROOT = pathlib.Path(__file__).parent.parent


def pytest_configure(config: pytest.Config) -> None:
    if sys.platform == "win32":
        os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")

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


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for item in items:
        if isinstance(item, pytest.Function):
            item.add_marker(session_scope_marker, append=False)


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
