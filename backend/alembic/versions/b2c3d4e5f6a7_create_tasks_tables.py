"""create_tasks_and_task_progress_tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SEQUENCE IF NOT EXISTS task_id_seq START 1")

    op.create_table('tasks',
        sa.Column('id', sa.String(length=20), nullable=False),
        sa.Column('demand_id', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=10), nullable=False),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('team_status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('planned_end_time', sa.String(length=30), nullable=True),
        sa.Column('owner_id', sa.String(length=36), nullable=True),
        sa.Column('leader_id', sa.String(length=36), nullable=True),
        sa.Column('resource_links', sa.Text(), nullable=True),
        sa.Column('file_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_demand_id'), 'tasks', ['demand_id'])
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'])

    op.create_table('task_progress',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('file_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_progress_task_id'), 'task_progress', ['task_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_task_progress_task_id'), table_name='task_progress')
    op.drop_table('task_progress')
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_demand_id'), table_name='tasks')
    op.drop_table('tasks')
    op.execute("DROP SEQUENCE IF EXISTS task_id_seq")
