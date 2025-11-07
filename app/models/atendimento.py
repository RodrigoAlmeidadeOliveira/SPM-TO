"""
Modelo de Atendimento - Sessões terapêuticas com formato SOAP
"""
from datetime import datetime
from app import db


# Tabela de associação entre Atendimento e Avaliação
atendimento_avaliacao = db.Table('atendimento_avaliacao',
    db.Column('atendimento_id', db.Integer, db.ForeignKey('atendimentos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('avaliacao_id', db.Integer, db.ForeignKey('avaliacoes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('data_vinculo', db.DateTime, default=datetime.utcnow, nullable=False)
)


class Atendimento(db.Model):
    """
    Modelo de Atendimento/Sessão Terapêutica

    Segue o formato SOAP:
    - S (Subjetivo): Relato do paciente/responsável
    - O (Objetivo): Observações do profissional
    - A (Avaliação/Assessment): Análise clínica
    - P (Plano): Próximos passos e condutas
    """
    __tablename__ = 'atendimentos'

    id = db.Column(db.Integer, primary_key=True)
    prontuario_id = db.Column(db.Integer, db.ForeignKey('prontuarios.id', ondelete='CASCADE'),
                              nullable=False, index=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Dados básicos da sessão
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    duracao_minutos = db.Column(db.Integer)  # Duração da sessão
    tipo = db.Column(db.String(50), nullable=False, default='sessao')  # sessao, avaliacao, reavaliacao, orientacao

    # Formato SOAP
    subjetivo = db.Column(db.Text)  # S - Relato subjetivo do paciente/família
    objetivo = db.Column(db.Text)  # O - Observações objetivas do terapeuta
    avaliacao = db.Column(db.Text)  # A - Análise/Avaliação clínica
    plano = db.Column(db.Text)  # P - Plano de ação/próximos passos

    # Informações adicionais
    modalidade = db.Column(db.String(50))  # presencial, online, domiciliar, escolar
    local = db.Column(db.String(200))  # Local do atendimento

    # Comparecimento
    compareceu = db.Column(db.Boolean, default=True, nullable=False)
    motivo_falta = db.Column(db.Text)  # Se não compareceu, motivo

    # Intervenções realizadas
    intervencoes = db.Column(db.Text)  # JSON array de intervenções
    recursos_utilizados = db.Column(db.Text)  # Recursos e materiais utilizados

    # Orientações dadas
    orientacoes_familia = db.Column(db.Text)
    orientacoes_escola = db.Column(db.Text)

    # Anexos e referências
    observacoes = db.Column(db.Text)

    # Status
    status = db.Column(db.String(20), default='rascunho', nullable=False)  # rascunho, finalizado, revisado
    finalizado_em = db.Column(db.DateTime)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    prontuario = db.relationship('Prontuario', back_populates='atendimentos')
    paciente = db.relationship('Paciente', backref=db.backref('atendimentos', lazy='dynamic'))
    profissional = db.relationship('User', backref=db.backref('atendimentos_realizados', lazy='dynamic'))

    # Avaliações realizadas nesta sessão (muitos-para-muitos)
    avaliacoes = db.relationship('Avaliacao', secondary=atendimento_avaliacao,
                                backref=db.backref('atendimentos', lazy='dynamic'))

    def __repr__(self):
        return f'<Atendimento {self.id} - {self.data_hora.strftime("%d/%m/%Y")}>'

    def get_intervencoes_list(self):
        """Retorna lista de intervenções"""
        import json
        try:
            return json.loads(self.intervencoes) if self.intervencoes else []
        except:
            return []

    def get_tipo_display(self):
        """Retorna nome amigável do tipo"""
        tipos = {
            'sessao': 'Sessão Terapêutica',
            'avaliacao': 'Avaliação Inicial',
            'reavaliacao': 'Reavaliação',
            'orientacao': 'Orientação'
        }
        return tipos.get(self.tipo, self.tipo)

    def get_modalidade_display(self):
        """Retorna nome amigável da modalidade"""
        modalidades = {
            'presencial': 'Presencial',
            'online': 'Online/Teleatendimento',
            'domiciliar': 'Domiciliar',
            'escolar': 'Escolar'
        }
        return modalidades.get(self.modalidade, self.modalidade or 'Não informado')

    def get_status_badge_class(self):
        """Retorna classe CSS para badge de status"""
        classes = {
            'rascunho': 'bg-warning',
            'finalizado': 'bg-success',
            'revisado': 'bg-info'
        }
        return classes.get(self.status, 'bg-secondary')

    def finalizar(self):
        """Marca o atendimento como finalizado"""
        self.status = 'finalizado'
        self.finalizado_em = datetime.utcnow()

    def is_completo(self):
        """Verifica se o atendimento tem todas as seções SOAP preenchidas"""
        return bool(self.subjetivo and self.objetivo and self.avaliacao and self.plano)
