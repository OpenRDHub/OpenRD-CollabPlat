"""Add task soft-deletion reason."""
from alembic import op
import sqlalchemy as sa

revision = "l2f3a4b5c6d7"
down_revision = "k1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("delete_reason", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "delete_reason")
