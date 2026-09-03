import pytest

from app.models.user import User
from app.utils.security import decode_token


@pytest.fixture
async def sms_code_register(fake_redis):
    """Pre-set a register SMS code for 13800000001."""
    await fake_redis.set("sms_code:register:13800000001", "123456", ex=300)
    return "123456"


async def test_register(client, sms_code_register):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "OK"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["username"] == "testuser"


async def test_register_duplicate_username(client, sms_code_register, fake_redis):
    await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    await fake_redis.set("sms_code:register:13800000002", "654321", ex=300)
    resp = await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "phone": "13800000002",
        "password": "pass1234",
        "sms_code": "654321",
    })
    assert resp.status_code == 400
    assert "已存在" in resp.json()["detail"]


async def test_login(client, sms_code_register):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "pass1234",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


async def test_login_wrong_password(client, sms_code_register):
    await client.post("/api/v1/auth/register", json={
        "username": "wrongpw",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "wrongpw",
        "password": "wrongpassword",
    })
    assert resp.status_code == 400


async def test_refresh_token(client, sms_code_register):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "refreshuser",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    refresh_token = reg.json()["data"]["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


@pytest.mark.parametrize("role", ["builder", "operator", "super_admin"])
async def test_refresh_uses_current_database_role(
    client, sms_code_register, db_session, role
):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "role_refresh_user",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    assert reg.status_code == 200
    user_id = reg.json()["data"]["user"]["id"]
    refresh_token = reg.json()["data"]["refresh_token"]

    user = await db_session.get(User, user_id)
    user.role = role
    await db_session.commit()

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200, response.text
    access_payload = decode_token(response.json()["data"]["access_token"])
    assert access_payload["sub"] == user_id
    assert access_payload["role"] == role


async def test_locked_user_cannot_refresh(
    client, sms_code_register, db_session, fake_redis
):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "locked_refresh_user",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    user_id = reg.json()["data"]["user"]["id"]
    refresh_token = reg.json()["data"]["refresh_token"]
    refresh_payload = decode_token(refresh_token)

    user = await db_session.get(User, user_id)
    user.is_locked = 1
    await db_session.commit()

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 401
    assert "锁定" in response.json()["detail"]
    assert not await fake_redis.exists(
        f"refresh:{user_id}:{refresh_payload['jti']}"
    )


async def test_refresh_token_replay_revokes_rotated_session(
    client, sms_code_register
):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "refresh_replay_user",
        "phone": "13800000001",
        "password": "pass1234",
        "sms_code": sms_code_register,
    })
    old_refresh = reg.json()["data"]["refresh_token"]

    rotated = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh,
    })
    assert rotated.status_code == 200
    new_refresh = rotated.json()["data"]["refresh_token"]

    replay = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh,
    })
    assert replay.status_code == 401
    assert "重放" in replay.json()["detail"]

    revoked = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": new_refresh,
    })
    assert revoked.status_code == 401


async def test_sms_code_cooldown(client, fake_redis):
    resp = await client.post("/api/v1/auth/sms-code", json={
        "phone": "13800000099",
        "scene": "register",
    })
    assert resp.status_code == 200

    resp = await client.post("/api/v1/auth/sms-code", json={
        "phone": "13800000099",
        "scene": "register",
    })
    assert resp.status_code == 429
