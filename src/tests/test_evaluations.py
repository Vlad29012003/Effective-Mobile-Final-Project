from httpx import AsyncClient


async def _setup_done_task(client, make_user, make_team, make_task):
    """Create admin + member, team, task in 'done' state. Returns (team, task, admin_h, member_h)."""
    _, admin_headers = await make_user()
    _, member_headers = await make_user()
    team = await make_team(admin_headers)

    await client.post(
        "/api/v1/users/join",
        json={"join_code": team["join_code"]},
        headers=member_headers,
    )

    task = await make_task(admin_headers, team["id"])

    await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/status",
        json={"status": "done"},
        headers=admin_headers,
    )
    return team, task, admin_headers, member_headers


async def test_create_evaluation_by_admin(client: AsyncClient, make_user, make_team, make_task):
    team, task, admin_h, _ = await _setup_done_task(client, make_user, make_team, make_task)

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/evaluation",
        json={"score": 5, "comment": "Excellent work"},
        headers=admin_h,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["score"] == 5
    assert data["comment"] == "Excellent work"
    assert data["task_id"] == task["id"]


async def test_create_evaluation_task_not_done(
    client: AsyncClient, make_user, make_team, make_task
):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/evaluation",
        json={"score": 3},
        headers=headers,
    )
    assert r.status_code == 422


async def test_create_evaluation_by_member_forbidden(
    client: AsyncClient, make_user, make_team, make_task
):
    team, task, _, member_h = await _setup_done_task(client, make_user, make_team, make_task)

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/evaluation",
        json={"score": 4},
        headers=member_h,
    )
    assert r.status_code == 403


async def test_get_evaluation(client: AsyncClient, make_user, make_team, make_task):
    team, task, admin_h, member_h = await _setup_done_task(client, make_user, make_team, make_task)

    await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/evaluation",
        json={"score": 4},
        headers=admin_h,
    )

    r = await client.get(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/evaluation",
        headers=member_h,
    )
    assert r.status_code == 200
    assert r.json()["score"] == 4
