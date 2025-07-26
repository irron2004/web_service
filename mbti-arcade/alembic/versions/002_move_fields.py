"""move fields - add my_* to pair, relation to response

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
    # Add my_* columns to Pair table
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
    
    # Add relation column to Response table
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