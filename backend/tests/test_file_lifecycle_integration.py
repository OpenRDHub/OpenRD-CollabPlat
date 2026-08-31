import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models.file import File
from app.models.task import Task
from app.models.team import TaskMember
from app.models.user import User
from app.services.file import cleanup_expired_files
from app.utils.security import create_access_token, hash_password

VALID_PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


async def create_user(db_session, suffix: int, role: str) -> User:
    user = User(
        id=uuid.uuid4().hex,
        platform_id=f"ORD{suffix:06d}",
        username=f"file_test_{suffix}",
        phone=f"139{suffix:08d}",
        password_hash=hash_password("Test123!"),
        role=role,
        nickname=f"File Test {suffix}",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.file.get_storage_root", lambda: tmp_path)
    return tmp_path


@pytest.mark.asyncio
async def test_temporary_file_is_private_expires_and_is_cleaned(
    client, db_session, isolated_storage
):
    owner = await create_user(db_session, 1, "requester")
    stranger = await create_user(db_session, 2, "requester")

    response = await client.post(
        "/api/v1/files",
        headers=auth_headers(owner),
        files={"file": ("../../proof.pdf", VALID_PDF, "application/octet-stream")},
    )
    assert response.status_code == 200, response.text
    file_id = response.json()["data"]["file_id"]

    record = await db_session.get(File, file_id)
    assert record is not None
    assert record.original_name == "proof.pdf"
    assert record.content_type == "application/pdf"
    assert record.detected_content_type == "application/pdf"
    assert record.sha256 == hashlib.sha256(VALID_PDF).hexdigest()
    assert record.lifecycle_status == "temporary"
    assert record.expires_at is not None
    assert (isolated_storage / record.storage_path).exists()

    denied = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(stranger))
    assert denied.status_code == 403

    record.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await db_session.commit()
    expired = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(owner))
    assert expired.status_code == 410

    result = await cleanup_expired_files(db_session)
    await db_session.refresh(record)
    assert result["expired"] == 1
    assert record.lifecycle_status == "expired"
    assert record.is_deleted == 1
    assert not (isolated_storage / record.storage_path).exists()


@pytest.mark.asyncio
async def test_demand_binding_controls_download_and_prevents_direct_delete(
    client, db_session, isolated_storage
):
    creator = await create_user(db_session, 10, "requester")
    unrelated = await create_user(db_session, 11, "requester")
    operator = await create_user(db_session, 12, "operator")
    admin = await create_user(db_session, 13, "super_admin")

    upload = await client.post(
        "/api/v1/files",
        headers=auth_headers(creator),
        files={"file": ("evidence.pdf", VALID_PDF, "application/pdf")},
    )
    assert upload.status_code == 200, upload.text
    file_id = upload.json()["data"]["file_id"]

    demand = await client.post(
        "/api/v1/demands",
        headers=auth_headers(creator),
        json={
            "title": "Attachment authorization acceptance",
            "description": "Bind a temporary upload to the new demand.",
            "urgency": "high",
            "attachment_ids": [file_id],
        },
    )
    assert demand.status_code == 200, demand.text
    demand_id = demand.json()["data"]["id"]

    record = await db_session.get(File, file_id)
    await db_session.refresh(record)
    assert record.biz_type == "demand"
    assert record.biz_id == demand_id
    assert record.lifecycle_status == "bound"
    assert record.expires_at is None

    for user in (creator, operator, admin):
        allowed = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(user))
        assert allowed.status_code == 200

    denied = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(unrelated))
    assert denied.status_code == 403

    delete = await client.delete(f"/api/v1/files/{file_id}", headers=auth_headers(creator))
    assert delete.status_code == 409
    assert (isolated_storage / record.storage_path).exists()


@pytest.mark.asyncio
async def test_task_member_can_upload_directly_but_non_member_cannot_download(
    client, db_session, isolated_storage
):
    operator = await create_user(db_session, 20, "operator")
    member = await create_user(db_session, 21, "builder")
    unrelated = await create_user(db_session, 22, "builder")
    task = Task(
        id="TASK-900001",
        title="File authorization task",
        description="Integration acceptance",
        priority="medium",
        owner_id=operator.id,
        leader_id=operator.id,
    )
    db_session.add(task)
    db_session.add(
        TaskMember(
            id=uuid.uuid4().hex,
            task_id=task.id,
            user_id=member.id,
            role="developer",
            source="acceptance-test",
            status="active",
        )
    )
    await db_session.commit()

    upload = await client.post(
        f"/api/v1/files?biz_type=task&biz_id={task.id}",
        headers=auth_headers(member),
        files={"file": ("task-proof.pdf", VALID_PDF, "application/pdf")},
    )
    assert upload.status_code == 200, upload.text
    file_id = upload.json()["data"]["file_id"]

    allowed = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(member))
    assert allowed.status_code == 200
    denied = await client.get(f"/api/v1/files/{file_id}", headers=auth_headers(unrelated))
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_fake_pdf_is_rejected_without_database_or_storage_residue(
    client, db_session, isolated_storage
):
    owner = await create_user(db_session, 30, "requester")
    before = await db_session.scalar(select(func.count()).select_from(File))

    response = await client.post(
        "/api/v1/files",
        headers=auth_headers(owner),
        files={"file": ("malicious.pdf", b"MZ-not-a-pdf", "application/pdf")},
    )
    assert response.status_code == 400

    db_session.expire_all()
    after = await db_session.scalar(select(func.count()).select_from(File))
    assert after == before
    assert list(isolated_storage.iterdir()) == []
