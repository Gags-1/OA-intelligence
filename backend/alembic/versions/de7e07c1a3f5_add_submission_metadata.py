"""add submission metadata

Revision ID: de7e07c1a3f5
Revises: 8f0d03910bad
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "de7e07c1a3f5"
down_revision: Union[str, Sequence[str], None] = "8f0d03910bad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Add columns as nullable first.
    #
    # Existing submissions already exist, so we cannot add
    # NOT NULL columns without providing values for them.
    # ---------------------------------------------------------

    op.add_column(
        "question_submissions",
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "question_submissions",
        sa.Column(
            "role",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "question_submissions",
        sa.Column(
            "difficulty",
            sa.String(length=20),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Backfill existing submissions.
    #
    # Existing historical submissions don't have metadata.
    # We use safe placeholder values for those records.
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE question_submissions
        SET
            company_id = 1,
            role = 'unknown',
            difficulty = 'unknown'
        WHERE company_id IS NULL
        """
    )

    # ---------------------------------------------------------
    # 3. Enforce the new schema.
    # ---------------------------------------------------------

    op.alter_column(
        "question_submissions",
        "company_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "question_submissions",
        "role",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "question_submissions",
        "difficulty",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 4. Add foreign-key relationship to companies.
    # ---------------------------------------------------------

    op.create_foreign_key(
        "fk_question_submissions_company_id",
        "question_submissions",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_question_submissions_company_id",
        "question_submissions",
        type_="foreignkey",
    )

    op.drop_column(
        "question_submissions",
        "difficulty",
    )

    op.drop_column(
        "question_submissions",
        "role",
    )

    op.drop_column(
        "question_submissions",
        "company_id",
    )
