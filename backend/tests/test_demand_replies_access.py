from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.api.v1 import demand as demand_api


@pytest.fixture(autouse=True)
def clean_db():
    """These unit tests do not use the configured PostgreSQL database."""
    yield


def _user(user_id: str, role: str) -> dict:
    return {"user_id": user_id, "role": role}


@pytest.mark.parametrize(
    ("current_user", "expected_status"),
    [
        pytest.param(_user("creator", "requester"), 200, id="creator"),
        pytest.param(_user("other-requester", "requester"), 403, id="unrelated-requester"),
        pytest.param(_user("other-builder", "builder"), 403, id="unrelated-builder"),
        pytest.param(_user("owner", "requester"), 200, id="owner-pm"),
        pytest.param(_user("other-operator", "operator"), 200, id="operator"),
        pytest.param(_user("admin", "super_admin"), 200, id="super-admin"),
    ],
)
async def test_get_demand_replies_enforces_business_access(
    monkeypatch,
    current_user,
    expected_status,
):
    demand = SimpleNamespace(creator_id="creator", owner_id="owner")
    get_demand = AsyncMock(return_value=demand)
    list_replies = AsyncMock(return_value=([], 0))
    monkeypatch.setattr(demand_api, "get_demand_by_id", get_demand)
    monkeypatch.setattr(demand_api, "list_replies", list_replies)

    if expected_status == 200:
        response = await demand_api.get_demand_replies(
            demand_id="demand-1",
            page=1,
            page_size=20,
            current_user=current_user,
            db=AsyncMock(),
        )
        assert response.data.total == 0
        list_replies.assert_awaited_once()
    else:
        with pytest.raises(HTTPException) as exc_info:
            await demand_api.get_demand_replies(
                demand_id="demand-1",
                page=1,
                page_size=20,
                current_user=current_user,
                db=AsyncMock(),
            )
        assert exc_info.value.status_code == expected_status
        list_replies.assert_not_awaited()


async def test_get_demand_replies_returns_404_for_missing_demand(monkeypatch):
    monkeypatch.setattr(demand_api, "get_demand_by_id", AsyncMock(return_value=None))
    list_replies = AsyncMock()
    monkeypatch.setattr(demand_api, "list_replies", list_replies)

    with pytest.raises(HTTPException) as exc_info:
        await demand_api.get_demand_replies(
            demand_id="missing",
            page=1,
            page_size=20,
            current_user=_user("requester", "requester"),
            db=AsyncMock(),
        )

    assert exc_info.value.status_code == 404
    list_replies.assert_not_awaited()
