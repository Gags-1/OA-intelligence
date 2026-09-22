"""link submissions to questions

Revision ID: b3c0f00100d5
Revises: 8fb3173be8c6
Create Date: 2026-09-22 01:45:55.006217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c0f00100d5'
down_revision: Union[str, Sequence[str], None] = '8fb3173be8c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "question_submissions",
        sa.Column("question_id", sa.Integer(), nullable=True),
    )

    op.create_foreign_key(
        "fk_question_submissions_question_id",
        "question_submissions",
        "questions",
        ["question_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_question_submissions_question_id",
        "question_submissions",
        type_="foreignkey",
    )

    op.drop_column(
        "question_submissions",
        "question_id",
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_question_submissions_question_id",
        "question_submissions",
        type_="foreignkey",
    )

    op.drop_column(
        "question_submissions",
        "question_id",
    )
