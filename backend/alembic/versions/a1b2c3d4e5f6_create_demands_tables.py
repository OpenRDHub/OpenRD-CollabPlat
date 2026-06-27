"""create_demands_and_demand_replies_tables

Revision ID: a1b2c3d4e5f6
Revises: 32f9fac9e6bd
Create Date: 2026-06-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '32f9fac9e6bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SEQUENCE IF NOT EXISTS demand_id_seq START 1")

    op.create_table('demands',
        sa.Column('id', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('urgency', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('convert_status', sa.String(length=20), nullable=True),
        sa.Column('creator_id', sa.String(length=36), nullable=False),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('attachment_ids', sa.Text(), nullable=True),
        sa.Column('linked_task_id', sa.String(length=20), nullable=True),
        sa.Column('linked_demand_id', sa.String(length=20), nullable=True),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demands_creator_id'), 'demands', ['creator_id'])
    op.create_index(op.f('ix_demands_status'), 'demands', ['status'])

    op.create_table('demand_replies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('demand_id', sa.String(length=20), nullable=False),
        sa.Column('thread_id', sa.String(length=36), nullable=False),
        sa.Column('sender_id', sa.String(length=36), nullable=False),
        sa.Column('sender_role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('attachment_ids', sa.Text(), nullable=True),
        sa.Column('is_revoked', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demand_replies_demand_id'), 'demand_replies', ['demand_id'])
    op.create_index(op.f('ix_demand_replies_thread_id'), 'demand_replies', ['thread_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_demand_replies_thread_id'), table_name='demand_replies')
    op.drop_index(op.f('ix_demand_replies_demand_id'), table_name='demand_replies')
    op.drop_table('demand_replies')
    op.drop_index(op.f('ix_demands_status'), table_name='demands')
    op.drop_index(op.f('ix_demands_creator_id'), table_name='demands')
    op.drop_table('demands')
    op.execute("DROP SEQUENCE IF EXISTS demand_id_seq")
