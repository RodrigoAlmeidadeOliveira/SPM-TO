"""
Modelos de Instrumento, Domínio, Questão e Tabela de Referência
"""
from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict, MutableList
from app import db


class Instrumento(db.Model):
    """Modelo de Instrumento SPM"""
    __tablename__ = 'instrumentos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)

    # Vinculação com módulo (para arquitetura modular)
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulos.id'), nullable=True, index=True)

    # Faixa etária e contexto
    idade_minima = db.Column(db.Integer, nullable=False)  # em anos
    idade_maxima = db.Column(db.Integer, nullable=False)  # em anos
    contexto = db.Column(db.String(20), nullable=False)  # 'casa' ou 'escola'

    # Instruções
    instrucoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    modulo = db.relationship('Modulo', back_populates='instrumentos')
    dominios = db.relationship('Dominio', back_populates='instrumento',
                               lazy='dynamic', cascade='all, delete-orphan',
                               order_by='Dominio.ordem')
    avaliacoes = db.relationship('Avaliacao', back_populates='instrumento', lazy='dynamic')

    def __repr__(self):
        return f'<Instrumento {self.codigo}>'


class Dominio(db.Model):
    """Modelo de Domínio (ex: Participação Social, Visão, etc.)"""
    __tablename__ = 'dominios'

    id = db.Column(db.Integer, primary_key=True)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False)
    codigo = db.Column(db.String(10), nullable=False)  # SOC, VIS, HEA, TOU, BOD, BAL, PLA
    nome = db.Column(db.String(200), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))

    # Escala de pontuação
    # Normal: Nunca=4, Ocasional=3, Frequente=2, Sempre=1
    # Invertido: Nunca=1, Ocasional=2, Frequente=3, Sempre=4
    escala_invertida = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    instrumento = db.relationship('Instrumento', back_populates='dominios')
    questoes = db.relationship('Questao', back_populates='dominio',
                               lazy='dynamic', cascade='all, delete-orphan',
                               order_by='Questao.numero')

    def __repr__(self):
        return f'<Dominio {self.codigo} - {self.nome}>'


class Questao(db.Model):
    """Modelo de Questão/Item do teste"""
    __tablename__ = 'questoes'

    id = db.Column(db.Integer, primary_key=True)
    dominio_id = db.Column(db.Integer, db.ForeignKey('dominios.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)  # Número sequencial dentro do domínio
    numero_global = db.Column(db.Integer, nullable=False)  # Número global no instrumento
    codigo = db.Column(db.String(100), unique=True, index=True)
    ordem = db.Column(db.Integer)
    texto = db.Column(db.Text, nullable=False)
    tipo_resposta = db.Column(db.String(50), default='TEXTO_LONGO')
    obrigatoria = db.Column(db.Boolean, default=True, nullable=False)
    opcoes_resposta = MutableList.as_mutable(db.JSON)
    metadados = MutableDict.as_mutable(db.JSON)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamentos
    dominio = db.relationship('Dominio', back_populates='questoes')
    respostas = db.relationship('Resposta', back_populates='questao', lazy='dynamic')

    def __repr__(self):
        return f'<Questao {self.numero_global}: {self.texto[:50]}>'


class TabelaReferencia(db.Model):
    """Modelo de Tabela de Referência para classificação de resultados"""
    __tablename__ = 'tabelas_referencia'

    id = db.Column(db.Integer, primary_key=True)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False)
    dominio_codigo = db.Column(db.String(10), nullable=False)  # SOC, VIS, HEA, TOU, BOD, BAL, PLA

    # T-score e classificação
    t_score = db.Column(db.Integer, nullable=False)
    percentil_min = db.Column(db.Integer)
    percentil_max = db.Column(db.Integer)

    # Faixas de escore bruto
    escore_min = db.Column(db.Integer, nullable=False)
    escore_max = db.Column(db.Integer, nullable=False)

    # Classificação: 'TIPICO', 'PROVAVEL_DISFUNCAO', 'DISFUNCAO_DEFINITIVA'
    classificacao = db.Column(db.String(50), nullable=False)

    # Relacionamentos
    instrumento = db.relationship('Instrumento')

    __table_args__ = (
        db.Index('idx_tabela_ref_lookup',
                 'instrumento_id', 'dominio_codigo', 't_score'),
    )

    def __repr__(self):
        return f'<TabelaReferencia {self.dominio_codigo} T={self.t_score}>'
