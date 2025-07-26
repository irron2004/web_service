"""add share & relation columns

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add relation column to Pair table (if not exists)
    try:
        op.add_column('pair', sa.Column('relation', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    # Add my_name, my_email, my_mbti columns to Response table (if not exists)
    try:
        op.add_column('response', sa.Column('my_name', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    try:
        op.add_column('response', sa.Column('my_email', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    try:
        op.add_column('response', sa.Column('my_mbti', sa.String(), nullable=True))
    except:
        pass  # Column already exists


def downgrade() -> None:
    # Remove columns from Response table
    op.drop_column('response', 'my_mbti')
    op.drop_column('response', 'my_email')
    op.drop_column('response', 'my_name')
    
    # Remove relation column from Pair table
    op.drop_column('pair', 'relation') 