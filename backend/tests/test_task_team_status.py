import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from scripts.repair_task_team_status import repair


@pytest.mark.parametrize(('initial', 'target', 'expected'), [
    ('recruiting', 'in_progress', 'collaborating'),
    ('team_ready', 'in_progress', 'collaborating'),
    ('in_progress', 'pending_acceptance', 'collaborating'),
    ('pending_acceptance', 'in_progress', 'collaborating'),
    ('pending_acceptance', 'completed', 'accepted'),
    ('recruiting', 'closed', 'ended'),
    ('pending_acceptance', 'closed', 'ended'),
])
async def test_status_api_persists_team_status(client, db_session, initial, target, expected):
    task = Task(id='SYNC-1', title='Status sync', status=initial, team_status='forming', stage='beta')
    db_session.add(task)
    await db_session.commit()

    async def admin():
        return {'user_id': 'sync-admin', 'role': 'super_admin', 'jti': 'sync-test'}

    app.dependency_overrides[get_current_user] = admin
    try:
        response = await client.post('/api/v1/tasks/SYNC-1/status', json={'status': target})
        assert response.status_code == 200, response.text
        assert response.json()['data']['team_status'] == expected
        detail = await client.get('/api/v1/tasks/SYNC-1')
        assert detail.json()['data']['team_status'] == expected
        assert detail.json()['data']['stage'] == 'beta'
        listing = await client.get('/api/v1/tasks', params={'team_status': expected})
        assert any(item['id'] == 'SYNC-1' for item in listing.json()['data']['items'])
        await db_session.refresh(task)
        assert task.status == target
        assert task.team_status == expected
    finally:
        app.dependency_overrides.pop(get_current_user, None)


async def test_repair_is_previewable_idempotent_and_skips_deleted(db_session):
    task = Task(id='REPAIR-1', title='Old completed task', status='completed', team_status='forming', stage='beta')
    deleted = Task(id='REPAIR-2', title='Deleted', status='closed', team_status='forming', is_deleted=1)
    db_session.add_all([task, deleted])
    await db_session.commit()
    assert await repair(db_session) == 1
    await db_session.refresh(task)
    assert task.team_status == 'forming'
    assert await repair(db_session, apply=True) == 1
    await db_session.refresh(task)
    await db_session.refresh(deleted)
    assert task.team_status == 'accepted'
    assert task.stage == 'beta'
    assert deleted.team_status == 'forming'
    assert await repair(db_session, apply=True) == 0
