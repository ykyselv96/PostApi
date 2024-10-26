"""Add is_block field

Revision ID: f13179c3383c
Revises: b38609f39f90
Create Date: 2024-10-24 16:34:29.182888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f13179c3383c'
down_revision: Union[str, None] = 'b38609f39f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('is_blocked', sa.Boolean(), nullable=True))
    op.add_column('posts', sa.Column('is_blocked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'is_blocked')
    op.drop_column('comments', 'is_blocked')
    # ### end Alembic commands ###
