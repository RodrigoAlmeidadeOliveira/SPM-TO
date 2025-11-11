"""expand dominio.codigo length to support perfil sensorial"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0d6e3b4fd6f0'
down_revision = 'f3bdf629b2a4'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('dominios') as batch_op:
        batch_op.alter_column('codigo',
                              existing_type=sa.String(length=10),
                              type_=sa.String(length=30),
                              existing_nullable=False)

def downgrade():
    with op.batch_alter_table('dominios') as batch_op:
        batch_op.alter_column('codigo',
                              existing_type=sa.String(length=30),
                              type_=sa.String(length=10),
                              existing_nullable=False)
