from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.v1.demand import _demand_to_out
from app.schemas.demand import DemandOut, DemandUpdateRequest


@pytest.fixture
def clean_db():
    """This schema-only contract suite must not require a running database."""
    yield


def test_demand_list_contract_exposes_canonical_fields() -> None:
    fields = DemandOut.model_fields

    assert "description" in fields
    assert "status" in fields
    assert "creator_id" in fields
    assert "linked_task_id" in fields
    assert "review_status" not in fields
    assert "publisher_id" not in fields
    assert "task_id" not in fields


def test_demand_list_mapper_includes_description() -> None:
    demand = SimpleNamespace(
        id="REQ-0001",
        title="需求标题",
        description="用于管理列表展示的需求描述",
        urgency="medium",
        status="pending_review",
        convert_status=None,
        creator_id="requester-1",
        progress=0,
        feedback=None,
        linked_task_id=None,
        linked_demand_id=None,
        owner_id=None,
        created_at=None,
        updated_at=None,
    )

    assert _demand_to_out(demand).description == demand.description


@pytest.mark.parametrize(
    "legacy_payload",
    [
        {"review_status": "待审核"},
        {"convert_status": "已转化"},
        {"task_id": "TASK-1001"},
        {"title": "不应由管理 PATCH 修改"},
    ],
)
def test_demand_update_rejects_legacy_management_fields(
    legacy_payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        DemandUpdateRequest.model_validate(legacy_payload)


def test_demand_update_accepts_only_non_action_fields() -> None:
    payload = DemandUpdateRequest.model_validate(
        {"progress": 40, "feedback": "等待补充材料", "owner_id": "operator-1"}
    )

    assert payload.model_dump(exclude_unset=True) == {
        "progress": 40,
        "feedback": "等待补充材料",
        "owner_id": "operator-1",
    }
