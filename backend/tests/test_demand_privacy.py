from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.api.v1 import demand as demand_api


@pytest.fixture(autouse=True)
async def clean_db():
    """This unit test mocks persistence and does not require the integration-test database."""
    yield


def make_demand(**overrides):
    values = {
        "id": "REQ-0001",
        "title": "测试需求",
        "description": "用于验证联系方式脱敏。",
        "urgency": "medium",
        "status": "pending_review",
        "convert_status": None,
        "creator_id": "requester-1",
        "contact_phone": "13800000001",
        "attachment_ids": None,
        "linked_task_id": None,
        "linked_demand_id": None,
        "progress": 0,
        "feedback": None,
        "owner_id": "operator-1",
        "created_at": None,
        "updated_at": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("current_user", "expected_phone"),
    [
        ({"user_id": "unrelated-requester", "role": "requester"}, "138****0001"),
        ({"user_id": "unrelated-builder", "role": "builder"}, "138****0001"),
        ({"user_id": "requester-1", "role": "requester"}, "13800000001"),
        ({"user_id": "operator-1", "role": "operator"}, "13800000001"),
        ({"user_id": "admin-1", "role": "super_admin"}, "13800000001"),
    ],
)
async def test_get_demand_masks_contact_phone_by_viewer(monkeypatch, current_user, expected_phone):
    demand = make_demand()
    monkeypatch.setattr(demand_api, "get_demand_by_id", AsyncMock(return_value=demand))

    response = await demand_api.get_demand("REQ-0001", current_user=current_user, db=AsyncMock())

    assert response.data.contact_phone == expected_phone
