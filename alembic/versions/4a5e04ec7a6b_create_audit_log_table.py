"""Create audit_log table

Revision ID: 4a5e04ec7a6b
Revises: 6b10c596986d
Create Date: 2026-02-11 16:46:04.628185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a5e04ec7a6b'
down_revision: Union[str, Sequence[str], None] = '6b10c596986d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create audit_log table."""
    op.create_table(
        sa.Table(
            "audit_log",
            sa.MetaData(),
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.Column("user", sa.String(100), nullable=False),
            sa.Column("operation", sa.String(10), nullable=False),
            sa.Column("entity_type", sa.String(100), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=False),
            sa.Column("field_changes", sa.Text(), nullable=False),
        )
    )


def downgrade() -> None:
    """Downgrade schema - Drop audit_log table."""
    op.drop_table("audit_log")
