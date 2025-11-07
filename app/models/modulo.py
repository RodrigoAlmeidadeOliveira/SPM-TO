"""
Modelo de Módulo - Sistema genérico de módulos de avaliação
"""
from datetime import datetime
from app import db


class Modulo(db.Model):
    """
    Modelo para representar módulos de avaliação e atendimento

    Cada módulo representa um tipo de avaliação ou ferramenta terapêutica
    (ex: SPM, COPM, PEDI, Avaliação Cognitiva, ADL, etc.)
    """
    __tablename__ = 'modulos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)

    # Categorização
    categoria = db.Column(db.String(50), nullable=False)  # 'sensorial', 'ocupacional', 'motor', 'cognitivo', 'funcional'

    # Apresentação visual
    icone = db.Column(db.String(50))  # Nome do ícone Bootstrap (ex: 'activity', 'clipboard-check')
    cor = db.Column(db.String(7))  # Cor em formato HEX (ex: '#0d6efd')

    # Configurações do módulo
    tipo = db.Column(db.String(50), nullable=False, default='avaliacao')  # 'avaliacao', 'terapia', 'misto'
    permite_reavaliacao = db.Column(db.Boolean, default=True, nullable=False)
    intervalo_reavaliacao_dias = db.Column(db.Integer)  # Intervalo mínimo recomendado entre avaliações

    # Status
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    instrumentos = db.relationship('Instrumento', back_populates='modulo', lazy='dynamic')

    def __repr__(self):
        return f'<Modulo {self.codigo}>'

    def get_cor_badge(self):
        """Retorna a cor do badge para exibição"""
        cores_padrao = {
            'sensorial': '#0d6efd',  # azul
            'ocupacional': '#198754',  # verde
            'motor': '#dc3545',  # vermelho
            'cognitivo': '#ffc107',  # amarelo
            'funcional': '#0dcaf0',  # cyan
        }
        return self.cor or cores_padrao.get(self.categoria, '#6c757d')

    def get_icone_badge(self):
        """Retorna o ícone do badge para exibição"""
        icones_padrao = {
            'sensorial': 'activity',
            'ocupacional': 'clipboard-check',
            'motor': 'person-walking',
            'cognitivo': 'brain',
            'funcional': 'list-check',
        }
        return self.icone or icones_padrao.get(self.categoria, 'file-earmark-text')
