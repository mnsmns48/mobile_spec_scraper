"""create access token table

Revision ID: f77dbb45f5db
Revises: 959dd42e8b69
Create Date: 2025-04-17 16:00:34.406671

"""
from typing import Sequence, Union

import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f77dbb45f5db'
down_revision: Union[str, None] = '959dd42e8b69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('access_token',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=43), nullable=False),
    sa.Column('created_at', fastapi_users_db_sqlalchemy.generics.TIMESTAMPAware(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('token')
    )
    op.create_index(op.f('ix_access_token_created_at'), 'access_token', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_access_token_created_at'), table_name='access_token')
    op.drop_table('access_token')
