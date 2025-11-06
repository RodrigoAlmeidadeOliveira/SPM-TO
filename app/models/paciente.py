"""
Modelo de Paciente
"""
from datetime import datetime
from app import db


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

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    avaliacoes = db.relationship('Avaliacao', back_populates='paciente',
                                 lazy='dynamic', cascade='all, delete-orphan')

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
