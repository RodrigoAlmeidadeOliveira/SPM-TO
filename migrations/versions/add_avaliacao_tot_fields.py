"""Add t_score_tot and classificacao_tot fields to avaliacoes

Revision ID: f9a34521c5e8
Revises: e4f56221b4d2
Create Date: 2025-11-07 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9a34521c5e8'
down_revision = 'e4f56221b4d2'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to avaliacoes table
    with op.batch_alter_table('avaliacoes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('t_score_tot', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('classificacao_tot', sa.String(length=50), nullable=True))


def downgrade():
    # Remove columns on downgrade
    with op.batch_alter_table('avaliacoes', schema=None) as batch_op:
        batch_op.drop_column('classificacao_tot')
        batch_op.drop_column('t_score_tot')
