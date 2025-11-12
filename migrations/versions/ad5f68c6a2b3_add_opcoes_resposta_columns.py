"""Add options and metadata columns to Questao (if missing).

Revision ID: ad5f68c6a2b3
Revises: 6bfe157efc7f
Create Date: 2025-11-12 03:20:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'ad5f68c6a2b3'
down_revision = '6bfe157efc7f'
branch_labels = None
depends_on = None


def _column_exists(inspector, table_name, column_name):
    return column_name in {column['name'] for column in inspector.get_columns(table_name)}


def _alter_table(operation):
    with op.batch_alter_table('questoes') as batch_op:
        operation(batch_op)


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _column_exists(inspector, 'questoes', 'opcoes_resposta'):
        _alter_table(lambda batch_op: batch_op.add_column(sa.Column('opcoes_resposta', sa.JSON(), nullable=True)))

    if not _column_exists(inspector, 'questoes', 'metadados'):
        _alter_table(lambda batch_op: batch_op.add_column(sa.Column('metadados', sa.JSON(), nullable=True)))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if _column_exists(inspector, 'questoes', 'opcoes_resposta'):
        _alter_table(lambda batch_op: batch_op.drop_column('opcoes_resposta'))

    if _column_exists(inspector, 'questoes', 'metadados'):
        _alter_table(lambda batch_op: batch_op.drop_column('metadados'))
