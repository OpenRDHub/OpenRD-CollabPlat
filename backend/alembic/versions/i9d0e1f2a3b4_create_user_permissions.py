"""create_user_permissions_table

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2g3
Create Date: 2026-09-18 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i9d0e1f2a3b4'
down_revision: Union[str, Sequence[str], None] = 'h8c9d0e1f2g3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('permission_id', sa.String(length=50), nullable=False),
        sa.Column('granted_by', sa.String(length=36), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'permission_id', name='uq_user_permissions_user_id_permission_id'),
    )
    op.create_index(op.f('ix_user_permissions_user_id'), 'user_permissions', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_permissions_user_id'), table_name='user_permissions')
    op.drop_table('user_permissions')
