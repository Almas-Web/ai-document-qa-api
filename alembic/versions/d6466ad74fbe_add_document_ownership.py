"""add document ownership

Revision ID: d6466ad74fbe
Revises: 11efdba4bc2a
Create Date: 2026-09-10 16:38:32.147884
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d6466ad74fbe"
down_revision: Union[str, Sequence[str], None] = "11efdba4bc2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    op.execute(
        "UPDATE documents SET user_id = 1 WHERE user_id IS NULL"
    )

    op.alter_column(
        "documents",
        "user_id",
        nullable=False,
    )

    op.create_index(
        op.f("ix_documents_user_id"),
        "documents",
        ["user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_documents_user_id_users",
        "documents",
        "users",
        ["user_id"],
        ["id"],
    )

def downgrade() -> None:
    op.drop_constraint(
        "fk_documents_user_id_users",
        "documents",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_documents_user_id"),
        table_name="documents",
    )
    op.drop_column("documents", "user_id")