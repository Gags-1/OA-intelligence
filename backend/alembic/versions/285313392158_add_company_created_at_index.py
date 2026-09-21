"""add company created_at index

Revision ID: 285313392158
Revises: 24a1004e636f
Create Date: 2026-09-21 12:15:50.273948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '285313392158'
down_revision: Union[str, Sequence[str], None] = '24a1004e636f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_questions_company_created_at",
        "questions",
        ["company_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_questions_company_created_at",
        table_name="questions",
    )
