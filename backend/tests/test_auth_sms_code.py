import pytest
from httpx import AsyncClient


class TestSendSmsCode:
    """测试 POST /api/v1/auth/sms-code 接口"""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """每个测试前 mock 掉 sms_service.send_sms_code，避免真实发送"""
        self.called_with = {}

        async def mock_send_sms_code(redis, phone, scene):
            self.called_with = {"redis": redis, "phone": phone, "scene": scene}
            # 模拟业务逻辑校验：比如频率限制
            if phone == "13800138000" and scene == "register":
                raise ValueError("短信发送频率过高，请稍后再试")

        monkeypatch.setattr(
            "app.services.sms.send_sms_code", mock_send_sms_code
        )

    # ==================== Pydantic 校验层（422） ====================

    @pytest.mark.asyncio
    async def test_phone_empty(self, client: AsyncClient):
        """手机号为空 → 422"""
        resp = await client.post("/api/v1/auth/sms-code", json={"phone": "", "scene": "register"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert any("请输入手机号" in str(d["msg"]) for d in detail)

    @pytest.mark.asyncio
    async def test_phone_not_digits(self, client: AsyncClient):
        """手机号含非数字 → 422"""
        resp = await client.post("/api/v1/auth/sms-code", json={"phone": "1380013abcd", "scene": "register"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert any("手机号只能为数字" in str(d["msg"]) for d in detail)

    @pytest.mark.asyncio
    async def test_phone_length_not_11(self, client: AsyncClient):
        """手机号长度不是 11 位 → 422"""
        resp = await client.post("/api/v1/auth/sms-code", json={"phone": "138", "scene": "register"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert any("手机号应为 11 位数字" in str(d["msg"]) for d in detail)

    @pytest.mark.asyncio
    async def test_phone_invalid_prefix(self, client: AsyncClient):
        """手机号号段不合法（第二位不是 3-9）→ 422"""
        resp = await client.post("/api/v1/auth/sms-code", json={"phone": "12012345678", "scene": "register"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert any("手机号格式不正确" in str(d["msg"]) for d in detail)

    @pytest.mark.asyncio
    async def test_scene_invalid(self, client: AsyncClient):
        """scene 不合法 → 422"""
        resp = await client.post("/api/v1/auth/sms-code", json={"phone": "13800138000", "scene": "hack"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert any("场景参数不合法" in str(d["msg"]) or "register" in str(d["msg"]) for d in detail)

    # ==================== 业务层（200 / 400） ====================

    @pytest.mark.asyncio
    async def test_valid_request_success(self, client: AsyncClient):
        """合法请求 → 200，调用 service 层"""
        resp = await client.post(
            "/api/v1/auth/sms-code",
            json={"phone": "13800138001", "scene": "register"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "验证码已发送"
        # 确认 service 层被正确调用
        assert self.called_with["phone"] == "13800138001"
        assert self.called_with["scene"] == "register"

    @pytest.mark.asyncio
    async def test_service_raises_value_error(self, client: AsyncClient):
        """service 层抛 ValueError（如频率限制）→ 400"""
        resp = await client.post(
            "/api/v1/auth/sms-code",
            json={"phone": "13800138000", "scene": "register"}
        )
        assert resp.status_code == 400
        assert "频率过高" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_valid_reset_password_scene(self, client: AsyncClient):
        """reset_password 场景也能正常工作"""
        resp = await client.post(
            "/api/v1/auth/sms-code",
            json={"phone": "13912345678", "scene": "reset_password"}
        )
        assert resp.status_code == 200
        assert self.called_with["scene"] == "reset_password"