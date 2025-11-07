"""
Modelo de Paciente
"""
from datetime import datetime
from sqlalchemy.orm import validates
from app import db
from app.models.utils import coerce_date

# Tabela de associação muitos-para-muitos entre User e Paciente
paciente_responsavel = db.Table('paciente_responsavel',
    db.Column('paciente_id', db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tipo_vinculo', db.String(20), nullable=False, default='terapeuta'),  # terapeuta, professor, familiar
    db.Column('data_vinculo', db.DateTime, default=datetime.utcnow, nullable=False)
)


class Paciente(db.Model):
    """Modelo de Paciente (Criança)"""
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    identificacao = db.Column(db.String(100), unique=True, nullable=True, index=True)
    data_nascimento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)  # M ou F
    raca_etnia = db.Column(db.String(100))

    # Informações adicionais
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Quem criou o paciente (proprietário principal)
    criador_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    avaliacoes = db.relationship('Avaliacao', back_populates='paciente',
                                 lazy='dynamic', cascade='all, delete-orphan')

    criador = db.relationship('User', foreign_keys=[criador_id], backref='pacientes_criados')

    # Relacionamento muitos-para-muitos com User (responsáveis/terapeutas)
    responsaveis = db.relationship('User', secondary=paciente_responsavel,
                                   backref=db.backref('pacientes_vinculados', lazy='dynamic'),
                                   lazy='dynamic')

    def calcular_idade(self, data_referencia=None):
        """
        Calcula a idade do paciente em anos e meses

        Args:
            data_referencia: Data de referência (default: hoje)

        Returns:
            tuple: (anos, meses)
        """
        if data_referencia is None:
            data_referencia = datetime.now().date()

        anos = data_referencia.year - self.data_nascimento.year
        meses = data_referencia.month - self.data_nascimento.month

        if meses < 0:
            anos -= 1
            meses += 12

        return anos, meses

    def get_instrumento_adequado(self, contexto='casa'):
        """
        Retorna o instrumento adequado baseado na idade

        Args:
            contexto: 'casa' ou 'escola'

        Returns:
            str: Código do instrumento (ex: 'SPM_5_12_CASA')
        """
        anos, _ = self.calcular_idade()

        if 3 <= anos <= 5:
            return f'SPM_P_3_5_{contexto.upper()}'
        elif 5 <= anos <= 12:
            return f'SPM_5_12_{contexto.upper()}'
        else:
            return None

    def __repr__(self):
        return f'<Paciente {self.nome}>'

    @validates('data_nascimento')
    def _validate_data_nascimento(self, key, value):
        """Permite atribuir datas como string, datetime ou date."""
        return coerce_date(value, key)
