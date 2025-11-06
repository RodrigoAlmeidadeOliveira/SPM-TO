"""Add plano template and plano items tables

Revision ID: e4f56221b4d2
Revises: 6b81f67155a4
Create Date: 2025-11-06 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4f56221b4d2'
down_revision = '6b81f67155a4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'plano_template_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instrumento_id', sa.Integer(), nullable=False),
        sa.Column('dominio_id', sa.Integer(), nullable=True),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['dominio_id'], ['dominios.id'], ),
        sa.ForeignKeyConstraint(['instrumento_id'], ['instrumentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plano_template_itens_instrumento', 'plano_template_itens', ['instrumento_id'])

    op.create_table(
        'plano_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('avaliacao_id', sa.Integer(), nullable=False),
        sa.Column('template_item_id', sa.Integer(), nullable=False),
        sa.Column('selecionado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['avaliacao_id'], ['avaliacoes.id'], ),
        sa.ForeignKeyConstraint(['template_item_id'], ['plano_template_itens.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('avaliacao_id', 'template_item_id', name='uq_plano_item_avaliacao_template')
    )
    op.create_index('ix_plano_itens_avaliacao', 'plano_itens', ['avaliacao_id'])
    op.create_index('ix_plano_itens_template', 'plano_itens', ['template_item_id'])


def downgrade():
    op.drop_index('ix_plano_itens_template', table_name='plano_itens')
    op.drop_index('ix_plano_itens_avaliacao', table_name='plano_itens')
    op.drop_table('plano_itens')
    op.drop_index('ix_plano_template_itens_instrumento', table_name='plano_template_itens')
    op.drop_table('plano_template_itens')
