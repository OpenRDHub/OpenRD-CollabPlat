"""create leave applications

Revision ID: k1f2a3b4c5d6
Revises: j0e1f2a3b4c5
Create Date: 2026-10-15 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "j0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leave_applications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=20), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reviewer_id", sa.String(length=36), nullable=True),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leave_applications_task_id", "leave_applications", ["task_id"])
    op.create_index("ix_leave_applications_member_id", "leave_applications", ["member_id"])
    op.create_index("ix_leave_applications_user_id", "leave_applications", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_leave_applications_user_id", table_name="leave_applications")
    op.drop_index("ix_leave_applications_member_id", table_name="leave_applications")
    op.drop_index("ix_leave_applications_task_id", table_name="leave_applications")
    op.drop_table("leave_applications")
