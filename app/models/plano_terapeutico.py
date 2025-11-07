"""
Modelo de Plano Terapêutico - Planejamento de objetivos e estratégias terapêuticas
"""
from datetime import datetime
from app import db


class PlanoTerapeutico(db.Model):
    """
    Modelo de Plano Terapêutico

    Organiza objetivos e estratégias de intervenção para um período específico
    """
    __tablename__ = 'planos_terapeuticos'

    id = db.Column(db.Integer, primary_key=True)
    prontuario_id = db.Column(db.Integer, db.ForeignKey('prontuarios.id', ondelete='CASCADE'),
                              nullable=False, index=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'),
                           nullable=False, index=True)

    # Informações do plano
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)

    # Período de vigência
    data_inicio = db.Column(db.Date, nullable=False, index=True)
    data_fim = db.Column(db.Date)
    duracao_prevista_meses = db.Column(db.Integer)  # Duração prevista em meses

    # Frequência de atendimento
    frequencia_semanal = db.Column(db.Integer)  # Número de sessões por semana
    duracao_sessao_minutos = db.Column(db.Integer)  # Duração de cada sessão

    # Áreas de foco (JSON array)
    areas_foco = db.Column(db.Text)  # Ex: ["Motricidade Fina", "Integração Sensorial", "AVDs"]

    # Estratégias gerais
    estrategias_gerais = db.Column(db.Text)
    recursos_necessarios = db.Column(db.Text)

    # Orientações
    orientacoes_familia = db.Column(db.Text)
    orientacoes_escola = db.Column(db.Text)
    orientacoes_equipe = db.Column(db.Text)  # Para equipe multidisciplinar

    # Critérios de alta
    criterios_alta = db.Column(db.Text)

    # Observações
    observacoes = db.Column(db.Text)

    # Status
    status = db.Column(db.String(20), default='ativo', nullable=False)  # ativo, concluido, cancelado, suspenso
    motivo_status = db.Column(db.Text)  # Motivo do status atual

    # Profissional responsável
    profissional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    prontuario = db.relationship('Prontuario', back_populates='planos_terapeuticos')
    paciente = db.relationship('Paciente', backref=db.backref('planos_terapeuticos', lazy='dynamic'))
    profissional = db.relationship('User', backref=db.backref('planos_criados', lazy='dynamic'))
    objetivos = db.relationship('ObjetivoTerapeutico', back_populates='plano',
                               lazy='dynamic', cascade='all, delete-orphan',
                               order_by='ObjetivoTerapeutico.prioridade')

    def __repr__(self):
        return f'<PlanoTerapeutico {self.titulo}>'

    def get_areas_foco_list(self):
        """Retorna lista de áreas de foco"""
        import json
        try:
            return json.loads(self.areas_foco) if self.areas_foco else []
        except:
            return []

    def get_status_badge_class(self):
        """Retorna classe CSS para badge de status"""
        classes = {
            'ativo': 'bg-success',
            'concluido': 'bg-info',
            'cancelado': 'bg-danger',
            'suspenso': 'bg-warning'
        }
        return classes.get(self.status, 'bg-secondary')

    def get_status_display(self):
        """Retorna nome amigável do status"""
        status_map = {
            'ativo': 'Ativo',
            'concluido': 'Concluído',
            'cancelado': 'Cancelado',
            'suspenso': 'Suspenso'
        }
        return status_map.get(self.status, self.status)

    def count_objetivos(self):
        """Conta total de objetivos"""
        return self.objetivos.count()

    def count_objetivos_atingidos(self):
        """Conta objetivos atingidos"""
        return self.objetivos.filter_by(status='atingido').count()

    def get_progresso_percentual(self):
        """Calcula percentual de progresso baseado nos objetivos"""
        total = self.count_objetivos()
        if total == 0:
            return 0
        atingidos = self.count_objetivos_atingidos()
        return int((atingidos / total) * 100)

    def is_vencido(self):
        """Verifica se o plano está vencido"""
        if not self.data_fim:
            return False
        from datetime import date
        return date.today() > self.data_fim

    def dias_restantes(self):
        """Calcula dias restantes do plano"""
        if not self.data_fim:
            return None
        from datetime import date
        delta = self.data_fim - date.today()
        return delta.days if delta.days > 0 else 0
