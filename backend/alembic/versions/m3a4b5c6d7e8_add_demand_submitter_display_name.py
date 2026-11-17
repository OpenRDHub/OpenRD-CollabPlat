"""Store the demand submitter's chosen display name."""

import sqlalchemy as sa
from alembic import op

revision = "m3a4b5c6d7e8"
down_revision = "l2f3a4b5c6d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("demands", sa.Column("submitter_display_name", sa.String(15), nullable=True))


def downgrade() -> None:
    op.drop_column("demands", "submitter_display_name")
