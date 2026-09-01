"""harden file lifecycle

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-31 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("files", sa.Column("sha256", sa.String(length=64), nullable=True))
    op.add_column(
        "files", sa.Column("detected_content_type", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "files",
        sa.Column(
            "lifecycle_status",
            sa.String(length=20),
            server_default="temporary",
            nullable=False,
        ),
    )
    op.add_column(
        "files",
        sa.Column(
            "scan_status",
            sa.String(length=20),
            server_default="legacy",
            nullable=False,
        ),
    )
    op.add_column(
        "files", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(op.f("ix_files_sha256"), "files", ["sha256"])
    op.create_index(op.f("ix_files_lifecycle_status"), "files", ["lifecycle_status"])
    op.create_index(op.f("ix_files_expires_at"), "files", ["expires_at"])

    op.execute(
        """
        UPDATE files
        SET lifecycle_status = CASE WHEN biz_id IS NULL THEN 'temporary' ELSE 'bound' END,
            expires_at = CASE
                WHEN biz_id IS NULL THEN created_at + INTERVAL '24 hours'
                ELSE NULL
            END
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_files_expires_at"), table_name="files")
    op.drop_index(op.f("ix_files_lifecycle_status"), table_name="files")
    op.drop_index(op.f("ix_files_sha256"), table_name="files")
    op.drop_column("files", "expires_at")
    op.drop_column("files", "scan_status")
    op.drop_column("files", "lifecycle_status")
    op.drop_column("files", "detected_content_type")
    op.drop_column("files", "sha256")
