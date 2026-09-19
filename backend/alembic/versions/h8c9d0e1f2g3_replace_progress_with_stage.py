"""replace task.progress with stage enum; drop numeric progress columns

Revision ID: h8c9d0e1f2g3
Revises: g7b8c9d0e1f2
Create Date: 2026-09-19 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.task import TaskStage


# revision identifiers, used by Alembic.
revision: str = "h8c9d0e1f2g3"
down_revision: Union[str, Sequence[str], None] = "g7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """用阶段枚举替代数值 progress（去数值化）。"""
    # PostgreSQL 枚举类型需在 ADD COLUMN 之前显式创建：
    # Alembic 的 op.add_column 不会为 ALTER TABLE 自动发出 CREATE TYPE（create_type 仅在建表时生效）。
    # 用 DO 块做幂等判断，避免重复执行时报 "type already exists"。
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_stage') THEN
                CREATE TYPE task_stage AS ENUM ('team', 'develop', 'beta', 'opensource');
              END IF;
            END $$;
            """
        )
    )
    # 主表 tasks：删除数值 progress，新增 stage 枚举列（默认 team）
    op.drop_column("tasks", "progress")
    op.add_column(
        "tasks",
        sa.Column(
            "stage",
            sa.Enum(name="task_stage", create_type=False),
            nullable=False,
            server_default=TaskStage.TEAM.value,
        ),
    )
    # 历史表 task_progress：删除数值 progress（阶段已由 stage 列存储）
    op.drop_column("task_progress", "progress")

    # 既有数据：默认已是 team，按状态尽量映射到更靠后的阶段
    op.execute(
        "UPDATE tasks SET stage = 'develop' "
        "WHERE status IN ('in_progress', 'pending_acceptance') AND stage = 'team'"
    )
    op.execute(
        "UPDATE tasks SET stage = 'opensource' WHERE status = 'completed' AND stage = 'team'"
    )


def downgrade() -> None:
    # 回滚：恢复数值 progress 列（默认 0），并删除 stage 枚举列与枚举类型
    op.add_column(
        "tasks",
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "task_progress",
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
    )
    op.drop_column("tasks", "stage")
    op.execute("DROP TYPE IF EXISTS task_stage")
