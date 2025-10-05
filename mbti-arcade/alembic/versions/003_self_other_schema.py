"""self/other participant schema groundwork

Revision ID: 003
Revises: 002
Create Date: 2025-09-27 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


participant_relation_enum = sa.Enum(
    "friend",
    "coworker",
    "family",
    "partner",
    "other",
    name="participantrelation",
)


def upgrade() -> None:
    # --- session owner snapshot fields -------------------------------------
    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("self_mbti", sa.String(length=4), nullable=True))
        batch.add_column(
            sa.Column("snapshot_owner_name", sa.String(length=120), nullable=True)
        )
        batch.add_column(
            sa.Column("snapshot_owner_avatar", sa.String(length=255), nullable=True)
        )

    # --- participant core table --------------------------------------------
    participant_relation_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("invite_token", sa.String(length=60), nullable=False),
        sa.Column("relation", participant_relation_enum, nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column(
            "consent_display",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("perceived_type", sa.String(length=4), nullable=True),
        sa.Column("axes_payload", sa.JSON(), nullable=True),
        sa.Column("answers_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("session_id", "invite_token", name="uq_participant_token"),
    )

    op.create_table(
        "participant_answers",
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("participant_id", "question_id"),
    )

    # --- aggregated insight per relation -----------------------------------
    op.create_table(
        "relation_aggregates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("relation", participant_relation_enum, nullable=False),
        sa.Column(
            "respondent_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("top_type", sa.String(length=4), nullable=True),
        sa.Column("top_fraction", sa.Float(), nullable=True),
        sa.Column("second_type", sa.String(length=4), nullable=True),
        sa.Column("second_fraction", sa.Float(), nullable=True),
        sa.Column("consensus", sa.Float(), nullable=True),
        sa.Column("pgi", sa.Float(), nullable=True),
        sa.Column("axes_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("session_id", "relation", name="uq_relation_per_session"),
    )

    # --- associate legacy other responses with participants ----------------
    with op.batch_alter_table("responses_other") as batch:
        batch.add_column(sa.Column("participant_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_responses_other_participant",
            "participants",
            ["participant_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("responses_other") as batch:
        batch.drop_constraint("fk_responses_other_participant", type_="foreignkey")
        batch.drop_column("participant_id")

    op.drop_table("relation_aggregates")
    op.drop_table("participant_answers")
    op.drop_table("participants")

    participant_relation_enum.drop(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("sessions") as batch:
        batch.drop_column("snapshot_owner_avatar")
        batch.drop_column("snapshot_owner_name")
        batch.drop_column("self_mbti")
