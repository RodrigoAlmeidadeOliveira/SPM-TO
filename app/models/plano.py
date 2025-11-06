"""
Modelos relacionados ao Plano Educacional Individualizado (PEI)
"""
from datetime import datetime
from app import db


class PlanoTemplateItem(db.Model):
    """
    Item de plano baseado em template (derivado das planilhas PEI)
    """
    __tablename__ = 'plano_template_itens'

    id = db.Column(db.Integer, primary_key=True)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False, index=True)
    dominio_id = db.Column(db.Integer, db.ForeignKey('dominios.id'))
    ordem = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow, nullable=False)

    instrumento = db.relationship('Instrumento')
    dominio = db.relationship('Dominio')
    itens = db.relationship('PlanoItem', back_populates='template_item', cascade='all, delete-orphan')

    @property
    def dominio_nome(self):
        """Nome amigável do domínio associado ao item"""
        return self.dominio.nome if self.dominio else 'Geral'

    def __repr__(self):
        return f'<PlanoTemplateItem {self.id} - {self.texto[:40]}>'


class PlanoItem(db.Model):
    """
    Item selecionado para um plano específico (por avaliação)
    """
    __tablename__ = 'plano_itens'

    id = db.Column(db.Integer, primary_key=True)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacoes.id'), nullable=False, index=True)
    template_item_id = db.Column(db.Integer, db.ForeignKey('plano_template_itens.id'), nullable=False, index=True)
    selecionado = db.Column(db.Boolean, default=False, nullable=False)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow, nullable=False)

    avaliacao = db.relationship('Avaliacao', back_populates='plano_itens')
    template_item = db.relationship('PlanoTemplateItem', back_populates='itens')

    __table_args__ = (
        db.UniqueConstraint('avaliacao_id', 'template_item_id', name='uq_plano_item_avaliacao_template'),
    )

    def __repr__(self):
        return f'<PlanoItem avaliacao={self.avaliacao_id} template={self.template_item_id}>'
