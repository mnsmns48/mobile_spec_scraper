"""add user model

Revision ID: 959dd42e8b69
Revises: 
Create Date: 2025-04-17 13:06:37.761109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '959dd42e8b69'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(length=320), nullable=False),
                    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_superuser', sa.Boolean(), nullable=False),
                    sa.Column('is_verified', sa.Boolean(), nullable=False),
                    sa.Column('phone_number', sa.Integer(), nullable=False),
                    sa.Column('telegram_id', sa.Integer(), nullable=True),
                    sa.Column('vk_id', sa.Integer(), nullable=True),
                    sa.Column('full_name', sa.String(), nullable=True),
                    sa.Column('birthday', sa.DateTime(), nullable=True),
                    sa.Column('address', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
