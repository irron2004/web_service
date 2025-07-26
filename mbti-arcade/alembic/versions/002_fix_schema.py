"""fix schema - move my_* to response, relation to pair

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove my_* columns from Pair table
    try:
        op.drop_column('pair', 'my_name')
    except:
        pass  # Column doesn't exist
    
    try:
        op.drop_column('pair', 'my_email')
    except:
        pass  # Column doesn't exist
    
    try:
        op.drop_column('pair', 'my_mbti')
    except:
        pass  # Column doesn't exist
    
    # Remove relation column from Response table
    try:
        op.drop_column('response', 'relation')
    except:
        pass  # Column doesn't exist
    
    # Add relation column to Pair table (if not exists)
    try:
        op.add_column('pair', sa.Column('relation', sa.String(), nullable=True))
    except:
        pass  # Column already exists
    
    # Add my_* columns to Response table (if not exists)
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
    # Remove my_* columns from Response table
    op.drop_column('response', 'my_mbti')
    op.drop_column('response', 'my_email')
    op.drop_column('response', 'my_name')
    
    # Remove relation column from Pair table
    op.drop_column('pair', 'relation')
    
    # Add my_* columns back to Pair table
    op.add_column('pair', sa.Column('my_name', sa.String(), nullable=True))
    op.add_column('pair', sa.Column('my_email', sa.String(), nullable=True))
    op.add_column('pair', sa.Column('my_mbti', sa.String(), nullable=True))
    
    # Add relation column back to Response table
    op.add_column('response', sa.Column('relation', sa.String(), nullable=True)) 