"""create_messages_system_logs_files_tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Messages
    op.create_table('messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('target_type', sa.String(length=20), nullable=True),
        sa.Column('target_id', sa.String(length=36), nullable=True),
        sa.Column('sender_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_category'), 'messages', ['category'])

    op.create_table('message_recipients',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('message_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('is_read', sa.Integer(), server_default='0', nullable=False),
        sa.Column('read_at', sa.String(length=30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_recipients_message_id'), 'message_recipients', ['message_id'])
    op.create_index(op.f('ix_message_recipients_user_id'), 'message_recipients', ['user_id'])

    # System logs
    op.create_table('system_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('actor_id', sa.String(length=36), nullable=False),
        sa.Column('actor_role', sa.String(length=20), nullable=True),
        sa.Column('actor_nickname', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('module', sa.String(length=30), nullable=False),
        sa.Column('target_type', sa.String(length=30), nullable=True),
        sa.Column('target_id', sa.String(length=36), nullable=True),
        sa.Column('target_name', sa.String(length=200), nullable=True),
        sa.Column('risk_level', sa.String(length=10), nullable=False, server_default='low'),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=False, server_default='success'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_actor_id'), 'system_logs', ['actor_id'])
    op.create_index(op.f('ix_system_logs_action'), 'system_logs', ['action'])
    op.create_index(op.f('ix_system_logs_module'), 'system_logs', ['module'])

    # Files
    op.create_table('files',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('biz_type', sa.String(length=30), nullable=True),
        sa.Column('uploader_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_biz_type'), 'files', ['biz_type'])
    op.create_index(op.f('ix_files_uploader_id'), 'files', ['uploader_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_files_uploader_id'), table_name='files')
    op.drop_index(op.f('ix_files_biz_type'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_system_logs_module'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_action'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_actor_id'), table_name='system_logs')
    op.drop_table('system_logs')
    op.drop_index(op.f('ix_message_recipients_user_id'), table_name='message_recipients')
    op.drop_index(op.f('ix_message_recipients_message_id'), table_name='message_recipients')
    op.drop_table('message_recipients')
    op.drop_index(op.f('ix_messages_category'), table_name='messages')
    op.drop_table('messages')
