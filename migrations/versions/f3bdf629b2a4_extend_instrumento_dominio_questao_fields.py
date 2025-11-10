"""extend instrumento, dominio e questao para novos modulos

Revision ID: f3bdf629b2a4
Revises: 9c6b6a9a63c7_add_auditoria_details_fields.py
Create Date: 2025-11-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3bdf629b2a4'
down_revision = '9c6b6a9a63c7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('instrumentos') as batch_op:
        batch_op.add_column(sa.Column('descricao', sa.Text(), nullable=True))

    with op.batch_alter_table('dominios') as batch_op:
        batch_op.add_column(sa.Column('descricao', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('categoria', sa.String(length=50), nullable=True))

    with op.batch_alter_table('questoes') as batch_op:
        batch_op.add_column(sa.Column('codigo', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('ordem', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('tipo_resposta', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('obrigatoria', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('opcoes_resposta', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('metadados', sa.JSON(), nullable=True))
        batch_op.create_index('ix_questoes_codigo', ['codigo'], unique=True)


def downgrade():
    with op.batch_alter_table('questoes') as batch_op:
        batch_op.drop_index('ix_questoes_codigo')
        batch_op.drop_column('metadados')
        batch_op.drop_column('opcoes_resposta')
        batch_op.drop_column('obrigatoria')
        batch_op.drop_column('tipo_resposta')
        batch_op.drop_column('ordem')
        batch_op.drop_column('codigo')

    with op.batch_alter_table('dominios') as batch_op:
        batch_op.drop_column('categoria')
        batch_op.drop_column('descricao')

    with op.batch_alter_table('instrumentos') as batch_op:
        batch_op.drop_column('descricao')
