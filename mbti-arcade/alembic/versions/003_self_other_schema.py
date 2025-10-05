"""self/other participant schema groundwork

Revision ID: 003
Revises: 002
Create Date: 2025-09-27 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


def _ensure_base_tables() -> None:
    """Create legacy core tables if they are missing.

    Older deployments relied on `Base.metadata.create_all` to materialize the
    perception-gap schema. When a fresh database is migrated purely through
    Alembic, those tables (notably `sessions`) are absent and would cause this
    revision to fail. We create the minimum set of tables required for this
    migration in a check-first manner so existing databases are left untouched.
    """

    bind = op.get_bind()
    metadata = sa.MetaData()

    users = sa.Table(
        "users",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("nickname", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    sessions = sa.Table(
        "sessions",
        metadata,
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("invite_token", sa.String(length=60), nullable=False, unique=True),
        sa.Column(
            "is_anonymous",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_raters", sa.Integer(), nullable=False, server_default=sa.text("50")),
        sa.Column("self_mbti", sa.String(length=4), nullable=True),
        sa.Column("snapshot_owner_name", sa.String(length=120), nullable=True),
        sa.Column("snapshot_owner_avatar", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    questions = sa.Table(
        "questions",
        metadata,
        sa.Column(
            "id", sa.Integer(), primary_key=True, autoincrement=False
        ),
        sa.Column("code", sa.String(length=40), nullable=False, unique=True),
        sa.Column("dim", sa.String(length=4), nullable=False),
        sa.Column("sign", sa.Integer(), nullable=False),
        sa.Column("context", sa.String(length=20), nullable=False),
        sa.Column("prompt_self", sa.String(length=512), nullable=False),
        sa.Column("prompt_other", sa.String(length=512), nullable=False),
        sa.Column("theme", sa.String(length=60), nullable=False),
        sa.Column("scenario", sa.String(length=120), nullable=False),
    )

    responses_self = sa.Table(
        "responses_self",
        metadata,
        sa.Column("session_id", sa.String(length=36), primary_key=True),
        sa.Column("question_id", sa.Integer(), primary_key=True),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
    )

    aggregates = sa.Table(
        "aggregates",
        metadata,
        sa.Column("session_id", sa.String(length=36), primary_key=True),
        sa.Column("ei_self", sa.Float(), nullable=True),
        sa.Column("sn_self", sa.Float(), nullable=True),
        sa.Column("tf_self", sa.Float(), nullable=True),
        sa.Column("jp_self", sa.Float(), nullable=True),
        sa.Column("ei_other", sa.Float(), nullable=True),
        sa.Column("sn_other", sa.Float(), nullable=True),
        sa.Column("tf_other", sa.Float(), nullable=True),
        sa.Column("jp_other", sa.Float(), nullable=True),
        sa.Column("ei_gap", sa.Float(), nullable=True),
        sa.Column("sn_gap", sa.Float(), nullable=True),
        sa.Column("tf_gap", sa.Float(), nullable=True),
        sa.Column("jp_gap", sa.Float(), nullable=True),
        sa.Column("ei_sigma", sa.Float(), nullable=True),
        sa.Column("sn_sigma", sa.Float(), nullable=True),
        sa.Column("tf_sigma", sa.Float(), nullable=True),
        sa.Column("jp_sigma", sa.Float(), nullable=True),
        sa.Column("n", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("gap_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
    )

    for table in (users, sessions, questions, responses_self, aggregates):
        table.create(bind=bind, checkfirst=True)


def _ensure_responses_other_table() -> None:
    """Create `responses_other` with the participant linkage if missing."""

    bind = op.get_bind()
    metadata = sa.MetaData()
    # Ensure referenced tables are present in the metadata for FK resolution.
    for referenced in ("sessions", "questions", "participants"):
        if referenced not in metadata.tables:
            sa.Table(referenced, metadata, autoload_with=bind)

    responses_other = sa.Table(
        "responses_other",
        metadata,
        sa.Column("session_id", sa.String(length=36), primary_key=True),
        sa.Column("rater_hash", sa.String(length=64), primary_key=True),
        sa.Column("question_id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("relation_tag", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["participants.id"],
            ondelete="CASCADE",
            name="fk_responses_other_participant",
        ),
        sa.UniqueConstraint("session_id", "rater_hash", "question_id", name="uq_other"),
    )

    responses_other.create(bind=bind, checkfirst=True)


def _table_has_column(inspector: Inspector, table: str, column: str) -> bool:
    return column in {col["name"] for col in inspector.get_columns(table)}


def _has_fk(
    inspector: Inspector,
    table: str,
    constraint_name: str,
    *,
    referred_table: str | None = None,
    local_columns: tuple[str, ...] | None = None,
) -> bool:
    for fk in inspector.get_foreign_keys(table):
        if fk.get("name") == constraint_name:
            return True
        if referred_table and fk.get("referred_table") == referred_table:
            constrained = tuple(fk.get("constrained_columns") or ())
            if local_columns and tuple(local_columns) == constrained:
                return True
    return False


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
    _ensure_base_tables()

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # --- session owner snapshot fields -------------------------------------
    needs_self_mbti = not _table_has_column(inspector, "sessions", "self_mbti")
    needs_snapshot_name = not _table_has_column(
        inspector, "sessions", "snapshot_owner_name"
    )
    needs_snapshot_avatar = not _table_has_column(
        inspector, "sessions", "snapshot_owner_avatar"
    )

    if needs_self_mbti or needs_snapshot_name or needs_snapshot_avatar:
        with op.batch_alter_table("sessions") as batch:
            if needs_self_mbti:
                batch.add_column(sa.Column("self_mbti", sa.String(length=4), nullable=True))
            if needs_snapshot_name:
                batch.add_column(
                    sa.Column("snapshot_owner_name", sa.String(length=120), nullable=True)
                )
            if needs_snapshot_avatar:
                batch.add_column(
                    sa.Column(
                        "snapshot_owner_avatar",
                        sa.String(length=255),
                        nullable=True,
                    )
                )

    # --- participant core table --------------------------------------------
    participant_relation_enum.create(bind, checkfirst=True)

    existing_tables = set(inspector.get_table_names())

    if "participants" not in existing_tables:
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

    if "participant_answers" not in existing_tables:
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

    if "relation_aggregates" not in existing_tables:
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
    _ensure_responses_other_table()

    inspector = sa.inspect(bind)
    needs_participant_id = not _table_has_column(
        inspector, "responses_other", "participant_id"
    )
    needs_participant_fk = not _has_fk(
        inspector,
        "responses_other",
        "fk_responses_other_participant",
        referred_table="participants",
        local_columns=("participant_id",),
    )

    if needs_participant_id or needs_participant_fk:
        with op.batch_alter_table("responses_other") as batch:
            if needs_participant_id:
                batch.add_column(sa.Column("participant_id", sa.Integer(), nullable=True))
            if needs_participant_fk:
                batch.create_foreign_key(
                    "fk_responses_other_participant",
                    "participants",
                    ["participant_id"],
                    ["id"],
                    ondelete="CASCADE",
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_fk(
        inspector,
        "responses_other",
        "fk_responses_other_participant",
        referred_table="participants",
        local_columns=("participant_id",),
    ) or _table_has_column(inspector, "responses_other", "participant_id"):
        with op.batch_alter_table("responses_other") as batch:
            if _has_fk(
                inspector,
                "responses_other",
                "fk_responses_other_participant",
                referred_table="participants",
                local_columns=("participant_id",),
            ):
                batch.drop_constraint("fk_responses_other_participant", type_="foreignkey")
            if _table_has_column(inspector, "responses_other", "participant_id"):
                batch.drop_column("participant_id")

    for table_name in ("relation_aggregates", "participant_answers", "participants"):
        if table_name in inspector.get_table_names():
            op.drop_table(table_name)

    participant_relation_enum.drop(bind, checkfirst=True)

    inspector = sa.inspect(bind)
    needs_drop_avatar = _table_has_column(inspector, "sessions", "snapshot_owner_avatar")
    needs_drop_name = _table_has_column(inspector, "sessions", "snapshot_owner_name")
    needs_drop_self = _table_has_column(inspector, "sessions", "self_mbti")

    if needs_drop_avatar or needs_drop_name or needs_drop_self:
        with op.batch_alter_table("sessions") as batch:
            if needs_drop_avatar:
                batch.drop_column("snapshot_owner_avatar")
            if needs_drop_name:
                batch.drop_column("snapshot_owner_name")
            if needs_drop_self:
                batch.drop_column("self_mbti")
