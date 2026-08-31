"""bind files to business objects

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-29 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("files", sa.Column("biz_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_files_biz_id"), "files", ["biz_id"])

    # Existing attachment columns contain JSON arrays serialized as text. Backfill
    # the first matching owner in the same order used by current business flows.
    op.execute(
        """
        UPDATE files AS f
        SET biz_type = 'demand', biz_id = d.id
        FROM demands AS d
        WHERE f.biz_id IS NULL
          AND d.is_deleted = 0
          AND d.attachment_ids IS NOT NULL
          AND d.attachment_ids::jsonb ? f.id
        """
    )
    op.execute(
        """
        UPDATE files AS f
        SET biz_type = 'demand_reply', biz_id = r.id
        FROM demand_replies AS r
        WHERE f.biz_id IS NULL
          AND r.is_deleted = 0
          AND r.attachment_ids IS NOT NULL
          AND r.attachment_ids::jsonb ? f.id
        """
    )
    op.execute(
        """
        UPDATE files AS f
        SET biz_type = 'task', biz_id = t.id
        FROM tasks AS t
        WHERE f.biz_id IS NULL
          AND t.is_deleted = 0
          AND t.file_ids IS NOT NULL
          AND t.file_ids::jsonb ? f.id
        """
    )
    op.execute(
        """
        UPDATE files AS f
        SET biz_type = 'task_progress', biz_id = p.id
        FROM task_progress AS p
        WHERE f.biz_id IS NULL
          AND p.is_deleted = 0
          AND p.file_ids IS NOT NULL
          AND p.file_ids::jsonb ? f.id
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_files_biz_id"), table_name="files")
    op.drop_column("files", "biz_id")
