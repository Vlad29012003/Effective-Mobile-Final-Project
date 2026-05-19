from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


def _dt(offset_days: int = 1, hour: int = 10) -> str:
    """ISO datetime string N days from now at given hour."""
    base = datetime.now(UTC).replace(hour=hour, minute=0, second=0, microsecond=0)
    return (base + timedelta(days=offset_days)).isoformat()


async def test_create_meeting(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    r = await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "Standup", "start_at": _dt(1, 9), "end_at": _dt(1, 10)},
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Standup"
    assert data["is_cancelled"] is False


async def test_list_meetings(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "Meeting 1", "start_at": _dt(1, 9), "end_at": _dt(1, 10)},
        headers=headers,
    )
    await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "Meeting 2", "start_at": _dt(2, 9), "end_at": _dt(2, 10)},
        headers=headers,
    )

    r = await client.get(f"/api/v1/teams/{team['id']}/meetings", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


async def test_create_meeting_overlap_conflict(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "First", "start_at": _dt(1, 9), "end_at": _dt(1, 11)},
        headers=headers,
    )

    # Overlapping time
    r = await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "Conflict", "start_at": _dt(1, 10), "end_at": _dt(1, 12)},
        headers=headers,
    )
    assert r.status_code == 409


async def test_cancel_meeting(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    r = await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "To Cancel", "start_at": _dt(1, 9), "end_at": _dt(1, 10)},
        headers=headers,
    )
    meeting_id = r.json()["id"]

    r = await client.delete(
        f"/api/v1/teams/{team['id']}/meetings/{meeting_id}",
        headers=headers,
    )
    assert r.status_code == 204

    meetings = await client.get(f"/api/v1/teams/{team['id']}/meetings", headers=headers)
    assert all(m["is_cancelled"] for m in meetings.json() if m["id"] == meeting_id)


async def test_cancel_already_cancelled_meeting(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    r = await client.post(
        f"/api/v1/teams/{team['id']}/meetings",
        json={"title": "Double Cancel", "start_at": _dt(1, 9), "end_at": _dt(1, 10)},
        headers=headers,
    )
    meeting_id = r.json()["id"]

    await client.delete(f"/api/v1/teams/{team['id']}/meetings/{meeting_id}", headers=headers)

    r = await client.delete(f"/api/v1/teams/{team['id']}/meetings/{meeting_id}", headers=headers)
    assert r.status_code == 422
