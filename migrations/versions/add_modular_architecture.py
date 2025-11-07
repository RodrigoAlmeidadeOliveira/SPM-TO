"""Add modular architecture and prontuário tables

Revision ID: a7b92f3c1d4e
Revises: f9a34521c5e8
Create Date: 2025-11-07 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b92f3c1d4e'
down_revision = 'f9a34521c5e8'
branch_labels = None
depends_on = None


def upgrade():
    # Create modulos table
    op.create_table('modulos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('icone', sa.String(length=50), nullable=True),
        sa.Column('cor', sa.String(length=7), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('permite_reavaliacao', sa.Boolean(), nullable=False),
        sa.Column('intervalo_reavaliacao_dias', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modulos_codigo'), 'modulos', ['codigo'], unique=True)

    # Create prontuarios table
    op.create_table('prontuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('paciente_id', sa.Integer(), nullable=False),
        sa.Column('data_abertura', sa.DateTime(), nullable=False),
        sa.Column('profissional_abertura_id', sa.Integer(), nullable=False),
        sa.Column('queixa_principal', sa.Text(), nullable=True),
        sa.Column('historia_doenca_atual', sa.Text(), nullable=True),
        sa.Column('historia_previa', sa.Text(), nullable=True),
        sa.Column('gestacao', sa.Text(), nullable=True),
        sa.Column('parto', sa.Text(), nullable=True),
        sa.Column('desenvolvimento_motor', sa.Text(), nullable=True),
        sa.Column('desenvolvimento_linguagem', sa.Text(), nullable=True),
        sa.Column('desenvolvimento_social', sa.Text(), nullable=True),
        sa.Column('diagnosticos', sa.Text(), nullable=True),
        sa.Column('medicamentos_uso', sa.Text(), nullable=True),
        sa.Column('alergias', sa.Text(), nullable=True),
        sa.Column('cirurgias_previas', sa.Text(), nullable=True),
        sa.Column('internacoes_previas', sa.Text(), nullable=True),
        sa.Column('historia_familiar', sa.Text(), nullable=True),
        sa.Column('escola', sa.String(length=200), nullable=True),
        sa.Column('serie_ano', sa.String(length=50), nullable=True),
        sa.Column('possui_aee', sa.Boolean(), nullable=True),
        sa.Column('possui_cuidador', sa.Boolean(), nullable=True),
        sa.Column('composicao_familiar', sa.Text(), nullable=True),
        sa.Column('objetivos_gerais', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('data_encerramento', sa.DateTime(), nullable=True),
        sa.Column('motivo_encerramento', sa.Text(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profissional_abertura_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('paciente_id')
    )
    op.create_index(op.f('ix_prontuarios_paciente_id'), 'prontuarios', ['paciente_id'], unique=True)

    # Create planos_terapeuticos table
    op.create_table('planos_terapeuticos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prontuario_id', sa.Integer(), nullable=False),
        sa.Column('paciente_id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('duracao_prevista_meses', sa.Integer(), nullable=True),
        sa.Column('frequencia_semanal', sa.Integer(), nullable=True),
        sa.Column('duracao_sessao_minutos', sa.Integer(), nullable=True),
        sa.Column('areas_foco', sa.Text(), nullable=True),
        sa.Column('estrategias_gerais', sa.Text(), nullable=True),
        sa.Column('recursos_necessarios', sa.Text(), nullable=True),
        sa.Column('orientacoes_familia', sa.Text(), nullable=True),
        sa.Column('orientacoes_escola', sa.Text(), nullable=True),
        sa.Column('orientacoes_equipe', sa.Text(), nullable=True),
        sa.Column('criterios_alta', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('motivo_status', sa.Text(), nullable=True),
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profissional_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prontuario_id'], ['prontuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planos_terapeuticos_data_inicio'), 'planos_terapeuticos', ['data_inicio'], unique=False)
    op.create_index(op.f('ix_planos_terapeuticos_paciente_id'), 'planos_terapeuticos', ['paciente_id'], unique=False)
    op.create_index(op.f('ix_planos_terapeuticos_prontuario_id'), 'planos_terapeuticos', ['prontuario_id'], unique=False)

    # Create atendimentos table
    op.create_table('atendimentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prontuario_id', sa.Integer(), nullable=False),
        sa.Column('paciente_id', sa.Integer(), nullable=False),
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
        sa.Column('duracao_minutos', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('subjetivo', sa.Text(), nullable=True),
        sa.Column('objetivo', sa.Text(), nullable=True),
        sa.Column('avaliacao', sa.Text(), nullable=True),
        sa.Column('plano', sa.Text(), nullable=True),
        sa.Column('modalidade', sa.String(length=50), nullable=True),
        sa.Column('local', sa.String(length=200), nullable=True),
        sa.Column('compareceu', sa.Boolean(), nullable=False),
        sa.Column('motivo_falta', sa.Text(), nullable=True),
        sa.Column('intervencoes', sa.Text(), nullable=True),
        sa.Column('recursos_utilizados', sa.Text(), nullable=True),
        sa.Column('orientacoes_familia', sa.Text(), nullable=True),
        sa.Column('orientacoes_escola', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('finalizado_em', sa.DateTime(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profissional_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prontuario_id'], ['prontuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_atendimentos_data_hora'), 'atendimentos', ['data_hora'], unique=False)
    op.create_index(op.f('ix_atendimentos_paciente_id'), 'atendimentos', ['paciente_id'], unique=False)
    op.create_index(op.f('ix_atendimentos_profissional_id'), 'atendimentos', ['profissional_id'], unique=False)
    op.create_index(op.f('ix_atendimentos_prontuario_id'), 'atendimentos', ['prontuario_id'], unique=False)

    # Create objetivos_terapeuticos table
    op.create_table('objetivos_terapeuticos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plano_id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('area', sa.String(length=100), nullable=True),
        sa.Column('prioridade', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('criterio_sucesso', sa.Text(), nullable=True),
        sa.Column('meta_quantitativa', sa.String(length=200), nullable=True),
        sa.Column('estrategias', sa.Text(), nullable=True),
        sa.Column('recursos', sa.Text(), nullable=True),
        sa.Column('prazo_estimado', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('percentual_progresso', sa.Integer(), nullable=True),
        sa.Column('data_atingido', sa.Date(), nullable=True),
        sa.Column('evolucoes', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plano_id'], ['planos_terapeuticos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_objetivos_terapeuticos_plano_id'), 'objetivos_terapeuticos', ['plano_id'], unique=False)

    # Create atendimento_avaliacao association table
    op.create_table('atendimento_avaliacao',
        sa.Column('atendimento_id', sa.Integer(), nullable=False),
        sa.Column('avaliacao_id', sa.Integer(), nullable=False),
        sa.Column('data_vinculo', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['atendimento_id'], ['atendimentos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['avaliacao_id'], ['avaliacoes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('atendimento_id', 'avaliacao_id')
    )

    # Add modulo_id to instrumentos table
    with op.batch_alter_table('instrumentos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modulo_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_instrumentos_modulo_id'), ['modulo_id'], unique=False)
        batch_op.create_foreign_key('fk_instrumentos_modulo_id', 'modulos', ['modulo_id'], ['id'])


def downgrade():
    # Remove modulo_id from instrumentos
    with op.batch_alter_table('instrumentos', schema=None) as batch_op:
        batch_op.drop_constraint('fk_instrumentos_modulo_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_instrumentos_modulo_id'))
        batch_op.drop_column('modulo_id')

    # Drop tables in reverse order
    op.drop_table('atendimento_avaliacao')

    op.drop_index(op.f('ix_objetivos_terapeuticos_plano_id'), table_name='objetivos_terapeuticos')
    op.drop_table('objetivos_terapeuticos')

    op.drop_index(op.f('ix_atendimentos_prontuario_id'), table_name='atendimentos')
    op.drop_index(op.f('ix_atendimentos_profissional_id'), table_name='atendimentos')
    op.drop_index(op.f('ix_atendimentos_paciente_id'), table_name='atendimentos')
    op.drop_index(op.f('ix_atendimentos_data_hora'), table_name='atendimentos')
    op.drop_table('atendimentos')

    op.drop_index(op.f('ix_planos_terapeuticos_prontuario_id'), table_name='planos_terapeuticos')
    op.drop_index(op.f('ix_planos_terapeuticos_paciente_id'), table_name='planos_terapeuticos')
    op.drop_index(op.f('ix_planos_terapeuticos_data_inicio'), table_name='planos_terapeuticos')
    op.drop_table('planos_terapeuticos')

    op.drop_index(op.f('ix_prontuarios_paciente_id'), table_name='prontuarios')
    op.drop_table('prontuarios')

    op.drop_index(op.f('ix_modulos_codigo'), table_name='modulos')
    op.drop_table('modulos')
