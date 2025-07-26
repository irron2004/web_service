"""initial schema

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
    # Add my_* columns to Pair table (if not exists)
    try:
        op.add_column('pair', sa.Column('my_name', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    try:
        op.add_column('pair', sa.Column('my_email', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    try:
        op.add_column('pair', sa.Column('my_mbti', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    # Add relation column to Response table (if not exists)
    try:
        op.add_column('response', sa.Column('relation', sa.String(), nullable=True))
    except:
        pass  # Column already exists


def downgrade() -> None:
    # Remove my_* columns from Pair table
    op.drop_column('pair', 'my_mbti')
    op.drop_column('pair', 'my_email')
    op.drop_column('pair', 'my_name')
    
    # Remove relation column from Response table
    op.drop_column('response', 'relation') 