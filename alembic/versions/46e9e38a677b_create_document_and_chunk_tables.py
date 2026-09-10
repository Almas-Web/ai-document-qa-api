"""create document and chunk tables

Revision ID: 46e9e38a677b
Revises:
Create Date: 2026-09-10 01:34:43.440740
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import pgvector

revision: str = "46e9e38a677b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("text_length", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documents_id"),
        "documents",
        ["id"],
        unique=False,
    )
    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "embedding",
            pgvector.sqlalchemy.vector.VECTOR(dim=384),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chunks_id"),
        "chunks",
        ["id"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_chunks_id"), table_name="chunks")
    op.drop_table("chunks")
    op.drop_index(op.f("ix_documents_id"), table_name="documents")
    op.drop_table("documents")
    op.execute("DROP EXTENSION IF EXISTS vector")