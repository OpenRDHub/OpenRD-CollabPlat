import pytest


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
