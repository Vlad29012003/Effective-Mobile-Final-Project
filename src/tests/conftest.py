"""Shared test helper fixtures."""

import pytest
from httpx import AsyncClient


@pytest.fixture
def make_user(client: AsyncClient):
    """Factory: registers a user, logs in, returns (user_data, auth_headers)."""
    counter = [0]

    async def _factory(
        email: str | None = None,
        password: str = "password123",
        first_name: str = "Test",
        last_name: str = "User",
    ) -> tuple[dict, dict]:
        counter[0] += 1
        if email is None:
            email = f"user{counter[0]}@example.com"

        r = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        assert r.status_code == 201, r.text
        user = r.json()

        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        return user, {"Authorization": f"Bearer {token}"}

    return _factory


@pytest.fixture
def make_team(client: AsyncClient):
    """Factory: creates a team and returns team data."""

    async def _factory(headers: dict, name: str = "Test Team") -> dict:
        r = await client.post("/api/v1/teams", json={"name": name}, headers=headers)
        assert r.status_code == 201, r.text
        return r.json()

    return _factory


@pytest.fixture
def make_task(client: AsyncClient):
    """Factory: creates a task in a team and returns task data."""

    async def _factory(headers: dict, team_id: int, title: str = "Test Task") -> dict:
        r = await client.post(
            f"/api/v1/teams/{team_id}/tasks",
            json={"title": title},
            headers=headers,
        )
        assert r.status_code == 201, r.text
        return r.json()

    return _factory
