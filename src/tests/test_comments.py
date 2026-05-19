from httpx import AsyncClient


async def test_add_and_list_comments(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments",
        json={"text": "First comment"},
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["text"] == "First comment"

    r = await client.get(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments",
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_update_comment_by_author(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments",
        json={"text": "Original"},
        headers=headers,
    )
    comment_id = r.json()["id"]

    r = await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments/{comment_id}",
        json={"text": "Edited"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["text"] == "Edited"


async def test_update_comment_by_non_author_forbidden(
    client: AsyncClient, make_user, make_team, make_task
):
    _, admin_headers = await make_user()
    member_user, member_headers = await make_user()
    team = await make_team(admin_headers)

    await client.post(
        "/api/v1/users/join",
        json={"join_code": team["join_code"]},
        headers=member_headers,
    )

    task = await make_task(admin_headers, team["id"])

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments",
        json={"text": "Admin comment"},
        headers=admin_headers,
    )
    comment_id = r.json()["id"]

    # member tries to edit admin's comment
    r = await client.patch(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments/{comment_id}",
        json={"text": "Hijacked"},
        headers=member_headers,
    )
    assert r.status_code == 403


async def test_delete_comment_by_author(client: AsyncClient, make_user, make_team, make_task):
    _, headers = await make_user()
    team = await make_team(headers)
    task = await make_task(headers, team["id"])

    r = await client.post(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments",
        json={"text": "To delete"},
        headers=headers,
    )
    comment_id = r.json()["id"]

    r = await client.delete(
        f"/api/v1/teams/{team['id']}/tasks/{task['id']}/comments/{comment_id}",
        headers=headers,
    )
    assert r.status_code == 204
