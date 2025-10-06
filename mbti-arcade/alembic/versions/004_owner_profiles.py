"""owner profiles table

Revision ID: 004
Revises: 003
Create Date: 2025-10-05 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def _create_owner_profiles_table() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()

    owner_profiles = sa.Table(
        "owner_profiles",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_key", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column(
            "mbti_source",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'input'"),
        ),
        sa.Column("mbti_value", sa.String(length=4), nullable=True),
        sa.Column(
            "show_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("owner_key", name="uq_owner_profile_key"),
    )

    owner_profiles.create(bind=bind, checkfirst=True)


def upgrade() -> None:
    _create_owner_profiles_table()


def downgrade() -> None:
    op.drop_table("owner_profiles")
