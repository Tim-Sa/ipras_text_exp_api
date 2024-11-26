"""create_user_table

Revision ID: 16c052e011bc
Revises: 
Create Date: 2024-11-23 13:28:57.026825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '16c052e011bc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '4dffe048bf59'


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('user_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now())
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table('users')
     ###
