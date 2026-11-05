"""Run with: python -m pytest --confcutdir=tests/isolated tests/isolated

An isolated SQLite database exercises API contracts and persisted data. PostgreSQL
row-lock/concurrency semantics must also be validated in the deployment test DB.
"""
import json

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.task import router as task_router
from app.api.v1.team import router as team_router
from app.api.v1.stats import router as stats_router
from app.api.v1.demand import router as demand_router
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.base import Base
from app.models.admin import SystemLog
from app.models.task import Task, TaskProgress
from app.models.team import TaskMember
from app.models.demand import Demand
from app.services.file import can_access_business_object
from app.services.task import set_task_deleted


@pytest.fixture
async def scene():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add_all([
            Task(id='DELETE-1', title='Keep history', status='in_progress',
                 team_status='collaborating', stage='beta', leader_id='tester', owner_id='tester'),
            TaskMember(id='MEMBER-1', task_id='DELETE-1', user_id='tester', role='成员', status='active'),
            TaskProgress(id='PROGRESS-1', task_id='DELETE-1', user_id='tester', stage='beta', content='Keep me'),
            Demand(id='DEMAND-1', title='Source', description='Keep source', creator_id='tester',
                   status='converted', linked_task_id='DELETE-1'),
        ])
        await db.commit()
    identity = {'user_id': 'tester', 'role': 'super_admin', 'jti': 'test'}
    app = FastAPI()
    for router in (task_router, team_router, stats_router, demand_router):
        app.include_router(router, prefix='/api/v1')

    async def db_override():
        async with factory() as db:
            yield db

    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[get_current_user] = lambda: dict(identity)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client, factory, identity
    await engine.dispose()


async def test_delete_restore_preserves_history_and_hides_access(scene):
    client, factory, identity = scene
    result = await client.post('/api/v1/tasks/DELETE-1/delete', json={'reason': '  重复项目  '})
    assert result.status_code == 200, result.text
    assert (await client.get('/api/v1/tasks')).json()['data']['total'] == 0
    deleted = (await client.get('/api/v1/tasks?deleted=true')).json()['data']['items'][0]
    assert deleted['delete_reason'] == '重复项目'
    assert deleted['deleted_by'] == 'tester'
    assert deleted['deleted_at']
    for path in ('', '/team', '/timeline', '/progress'):
        assert (await client.get('/api/v1/tasks/DELETE-1' + path)).status_code == 404
    assert (await client.post('/api/v1/tasks/DELETE-1/status', json={'status': 'closed'})).status_code == 404
    assert (await client.post('/api/v1/tasks/DELETE-1/progress', json={
        'stage': 'opensource', 'expected_updated_at': None,
    })).status_code == 404
    assert (await client.get('/api/v1/me/tasks')).json()['data']['total'] == 0
    assert (await client.get('/api/v1/me/stats')).json()['data']['task_count'] == 0
    assert (await client.get('/api/v1/demands/DEMAND-1')).json()['data']['linked_task_deleted']
    async with factory() as db:
        for biz_type, biz_id in [('task', 'DELETE-1'), ('task_progress', 'PROGRESS-1')]:
            assert not await can_access_business_object(db, biz_type=biz_type, biz_id=biz_id, user_id='tester', role='builder')
    assert (await client.post('/api/v1/tasks/DELETE-1/delete', json={'reason': 'again'})).status_code == 409
    assert (await client.post('/api/v1/tasks/DELETE-1/restore')).status_code == 200
    assert (await client.post('/api/v1/tasks/DELETE-1/restore')).status_code == 409
    detail = (await client.get('/api/v1/tasks/DELETE-1')).json()['data']
    assert (detail['status'], detail['team_status'], detail['stage']) == ('in_progress', 'collaborating', 'beta')
    assert (await client.get('/api/v1/me/stats')).json()['data']['task_count'] == 1
    assert not (await client.get('/api/v1/demands/DEMAND-1')).json()['data']['linked_task_deleted']
    async with factory() as db:
        assert await db.scalar(select(func.count()).select_from(TaskProgress)) == 1
        logs = (await db.execute(select(SystemLog).order_by(SystemLog.created_at))).scalars().all()
        assert {log.action for log in logs} == {'task.delete', 'task.restore'}
        assert all(json.loads(log.detail)['reason'] == '重复项目' for log in logs)


@pytest.mark.parametrize('role', ['operator', 'builder', 'requester'])
async def test_only_super_admin_even_when_owner_or_leader(scene, role):
    client, _, identity = scene
    identity['role'] = role
    for action in ('delete', 'restore'):
        result = await client.post(f'/api/v1/tasks/DELETE-1/{action}', json={'reason': 'test'})
        assert result.status_code == 403
    assert (await client.get('/api/v1/tasks?deleted=true')).status_code == 403


@pytest.mark.parametrize('reason', ['', '  ', 'a' * 501])
async def test_reason_validation_does_not_delete(scene, reason):
    client, _, _ = scene
    assert (await client.post('/api/v1/tasks/DELETE-1/delete', json={'reason': reason})).status_code == 422
    assert (await client.get('/api/v1/tasks/DELETE-1')).status_code == 200


async def test_audit_failure_rolls_back_task(scene, monkeypatch):
    _, factory, identity = scene
    async def fail(*args, **kwargs):
        raise RuntimeError('audit unavailable')
    monkeypatch.setattr('app.services.admin.create_system_log', fail)
    async with factory() as db:
        with pytest.raises(RuntimeError):
            await set_task_deleted(db, 'DELETE-1', deleted=True, actor=identity, reason='test')
        await db.rollback()
    async with factory() as db:
        task = await db.get(Task, 'DELETE-1')
        assert task.is_deleted == 0
        assert task.delete_reason is None
