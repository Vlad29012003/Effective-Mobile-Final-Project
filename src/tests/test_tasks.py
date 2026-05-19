from httpx import AsyncClient


async def test_create_task(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"], title="My Task")

    assert task["title"] == "My Task"
    assert task["status"] == "open"
    assert task["team_id"] == team["id"]


async def test_list_tasks(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    await make_task(headers, team["id"], title="Task 1")
    await make_task(headers, team["id"], title="Task 2")

    r = await client.get(f"/api/v1/teams/{team['id']}/tasks", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


async def test_list_tasks_filter_by_status(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    # Change status to in_progress
    await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/status",
        json={"status": "in_progress"},
        headers=headers,
    )

    r = await client.get(
        f"/api/v1/teams/{team['id']}/tasks",
        params={"status": "in_progress"},
        headers=headers,
    )
    assert r.status_code == 200
    assert all(t["status"] == "in_progress" for t in r.json())


async def test_update_task(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}",
        json={"title": "Updated Title", "description": "New desc"},
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "New desc"


async def test_change_status(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/status",
        json={"status": "done"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "done"


async def test_delete_task(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.delete(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}",
        headers=headers,
    )
    assert r.status_code == 204

    r = await client.get(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}",
        headers=headers,
    )
    assert r.status_code == 404
