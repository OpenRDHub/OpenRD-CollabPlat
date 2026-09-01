from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.file import File
from app.services.file import bind_files, ensure_file_access


@pytest.fixture(autouse=True)
async def clean_db():
    """These unit tests use a queued session stub and never touch PostgreSQL."""
    yield


class StubResult:
    def __init__(self, *, one=None, many=None):
        self.one = one
        self.many = many or []

    def scalar_one_or_none(self):
        return self.one

    def scalars(self):
        return self

    def all(self):
        return self.many


class StubSession:
    def __init__(self, *results):
        self.results = list(results)

    async def execute(self, _statement):
        return self.results.pop(0)


def make_file(*, uploader_id="uploader", biz_type=None, biz_id=None):
    return File(
        id="file-1",
        filename="file-1.pdf",
        original_name="proof.pdf",
        content_type="application/pdf",
        size=10,
        storage_path="file-1.pdf",
        biz_type=biz_type,
        biz_id=biz_id,
        uploader_id=uploader_id,
    )


@pytest.mark.asyncio
async def test_unbound_file_is_private_to_uploader_or_admin():
    record = make_file()
    await ensure_file_access(
        StubSession(), record, user_id="uploader", role="requester"
    )
    await ensure_file_access(
        StubSession(), record, user_id="operator-1", role="operator"
    )

    with pytest.raises(HTTPException) as exc:
        await ensure_file_access(
            StubSession(), record, user_id="unrelated", role="builder"
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_demand_attachment_reuses_demand_relationships():
    record = make_file(biz_type="demand", biz_id="REQ-0001")
    demand = SimpleNamespace(
        id="REQ-0001",
        creator_id="creator",
        owner_id="pm",
    )

    await ensure_file_access(
        StubSession(StubResult(one=demand)),
        record,
        user_id="creator",
        role="requester",
    )
    await ensure_file_access(
        StubSession(StubResult(one=demand)),
        record,
        user_id="pm",
        role="operator",
    )

    with pytest.raises(HTTPException) as exc:
        await ensure_file_access(
            StubSession(StubResult(one=demand)),
            record,
            user_id="unrelated",
            role="requester",
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_reply_attachment_inherits_parent_demand_access():
    record = make_file(biz_type="demand_reply", biz_id="reply-1")
    reply = SimpleNamespace(id="reply-1", demand_id="REQ-0001")
    demand = SimpleNamespace(id="REQ-0001", creator_id="creator", owner_id="pm")

    await ensure_file_access(
        StubSession(StubResult(one=reply), StubResult(one=demand)),
        record,
        user_id="creator",
        role="requester",
    )


@pytest.mark.asyncio
async def test_task_attachment_allows_active_member_but_denies_non_member():
    record = make_file(biz_type="task", biz_id="TASK-0001")
    task = SimpleNamespace(id="TASK-0001", owner_id="owner", leader_id="leader")
    active_member = SimpleNamespace(user_id="member", status="active")

    await ensure_file_access(
        StubSession(StubResult(one=task), StubResult(one=active_member)),
        record,
        user_id="member",
        role="builder",
    )

    with pytest.raises(HTTPException) as exc:
        await ensure_file_access(
            StubSession(StubResult(one=task), StubResult(one=None)),
            record,
            user_id="unrelated",
            role="builder",
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_binding_requires_uploader_and_prevents_rebinding():
    record = make_file()
    session = StubSession(StubResult(many=[record]))
    await bind_files(
        session,
        [record.id],
        biz_type="demand",
        biz_id="REQ-0001",
        actor_id="uploader",
        actor_role="requester",
    )
    assert record.biz_type == "demand"
    assert record.biz_id == "REQ-0001"

    with pytest.raises(HTTPException) as exc:
        await bind_files(
            StubSession(StubResult(many=[record])),
            [record.id],
            biz_type="demand_reply",
            biz_id="reply-1",
            actor_id="uploader",
            actor_role="requester",
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_user_cannot_bind_another_users_temporary_upload():
    record = make_file(uploader_id="alice")
    with pytest.raises(HTTPException) as exc:
        await bind_files(
            StubSession(StubResult(many=[record])),
            [record.id],
            biz_type="demand",
            biz_id="REQ-0001",
            actor_id="bob",
            actor_role="requester",
        )
    assert exc.value.status_code == 403
