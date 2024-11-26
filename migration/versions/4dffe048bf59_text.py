"""text

Revision ID: 4dffe048bf59
Revises:
Create Date: 2024-11-23 13:35:21.900905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4dffe048bf59'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the text table
    op.create_table(
        'text',
        sa.Column('text_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('topic', sa.String(length=50), nullable=False),
        sa.Column('difficult', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create the update_timestamp function
    op.execute("""
    CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create the set_timestamp trigger
    op.execute("""
    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON text
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();
    """)



def downgrade():
    # Drop the trigger
    op.execute("DROP TRIGGER IF EXISTS set_timestamp ON text;")

    # Drop the function
    op.execute("DROP FUNCTION IF EXISTS update_timestamp();")

    # Drop the text table
    op.drop_table('text')