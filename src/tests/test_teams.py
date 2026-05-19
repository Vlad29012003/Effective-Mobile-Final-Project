from httpx import AsyncClient


async def test_create_team(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers, name="Alpha Team")
    assert team["name"] == "Alpha Team"
    assert "join_code" in team
    assert "id" in team


async def test_list_teams_only_mine(client: AsyncClient, make_user, make_team):
    _, h1 = await make_user()
    _, h2 = await make_user()

    await make_team(h1, name="Team A")
    await make_team(h2, name="Team B")

    r = await client.get("/api/v1/teams", headers=h1)
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "Team A" in names
    assert "Team B" not in names


async def test_get_team(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    r = await client.get(f"/api/v1/teams/{team['id']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == team["id"]


async def test_update_team(client: AsyncClient, make_user, make_team):
    _, headers = await make_user()
    team = await make_team(headers)

    r = await client.patch(
        f"/api/v1/teams/{team['id']}",
        json={"name": "Updated Name"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Name"


async def test_join_team_via_code(client: AsyncClient, make_user, make_team):
    _, admin_headers = await make_user()
    _, member_headers = await make_user()
    team = await make_team(admin_headers)

    r = await client.post(
        "/api/v1/users/join",
        json={"join_code": team["join_code"]},
        headers=member_headers,
    )
    assert r.status_code == 200

    members_r = await client.get(f"/api/v1/teams/{team['id']}/members", headers=admin_headers)
    assert members_r.status_code == 200
    assert len(members_r.json()) == 2


async def test_update_member_role(client: AsyncClient, make_user, make_team):
    admin_user, admin_headers = await make_user()
    member_user, member_headers = await make_user()
    team = await make_team(admin_headers)

    await client.post(
        "/api/v1/users/join",
        json={"join_code": team["join_code"]},
        headers=member_headers,
    )

    r = await client.patch(
        f"/api/v1/teams/{team['id']}/members/{member_user['id']}",
        json={"role": "manager"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["role"] == "manager"
