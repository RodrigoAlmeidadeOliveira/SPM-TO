"""Add detalhes and paciente_id to auditoria_acessos

Revision ID: 9c6b6a9a63c7
Revises: e79e81ccec2b
Create Date: 2025-11-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c6b6a9a63c7'
down_revision = 'e79e81ccec2b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('auditoria_acessos', sa.Column('paciente_id', sa.Integer(), nullable=True))
    op.add_column('auditoria_acessos', sa.Column('detalhes', sa.Text(), nullable=True))
    op.create_foreign_key(
        'fk_auditoria_acessos_paciente_id',
        'auditoria_acessos',
        'pacientes',
        ['paciente_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_auditoria_acessos_paciente_id', 'auditoria_acessos', type_='foreignkey')
    op.drop_column('auditoria_acessos', 'detalhes')
    op.drop_column('auditoria_acessos', 'paciente_id')
