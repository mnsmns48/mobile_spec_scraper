"""delete additional fields

Revision ID: b9cf596a293d
Revises: f77dbb45f5db
Create Date: 2025-04-18 22:19:21.361739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b9cf596a293d'
down_revision: Union[str, None] = 'f77dbb45f5db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('user', 'birthday')
    op.drop_column('user', 'address')
    op.drop_column('user', 'vk_id')
    op.drop_column('user', 'phone_number')
    op.drop_column('user', 'full_name')



def downgrade() -> None:
    op.add_column('user', sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('phone_number', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('vk_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('address', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('birthday', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))

