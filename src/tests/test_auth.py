from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"

_USER = {
    "email": "auth@example.com",
    "password": "password123",
    "first_name": "Auth",
    "last_name": "User",
}


async def test_register_success(client: AsyncClient):
    r = await client.post(REGISTER_URL, json=_USER)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == _USER["email"]
    assert data["first_name"] == _USER["first_name"]
    assert "id" in data
    assert "password_hash" not in data


async def test_register_duplicate_email(client: AsyncClient):
    await client.post(REGISTER_URL, json=_USER)
    r = await client.post(REGISTER_URL, json=_USER)
    assert r.status_code == 409


async def test_login_success(client: AsyncClient):
    await client.post(REGISTER_URL, json=_USER)
    r = await client.post(LOGIN_URL, json={"email": _USER["email"], "password": _USER["password"]})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post(REGISTER_URL, json=_USER)
    r = await client.post(LOGIN_URL, json={"email": _USER["email"], "password": "wrong-password"})
    assert r.status_code == 401


async def test_refresh_token(client: AsyncClient):
    await client.post(REGISTER_URL, json=_USER)
    # Login sets the refresh cookie
    login_r = await client.post(
        LOGIN_URL, json={"email": _USER["email"], "password": _USER["password"]}
    )
    assert login_r.status_code == 200

    # The cookie is stored in the client cookie jar
    r = await client.post(REFRESH_URL)
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_logout(client: AsyncClient):
    await client.post(REGISTER_URL, json=_USER)
    await client.post(LOGIN_URL, json={"email": _USER["email"], "password": _USER["password"]})

    r = await client.post(LOGOUT_URL)
    assert r.status_code == 204

    # After logout, refresh should fail
    r = await client.post(REFRESH_URL)
    assert r.status_code == 401
