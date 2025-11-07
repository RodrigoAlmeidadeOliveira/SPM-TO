"""
Modelo de Prontuário - Prontuário Eletrônico do Paciente
"""
from datetime import datetime
from app import db


class Prontuario(db.Model):
    """
    Modelo de Prontuário Eletrônico

    Centraliza todas as informações clínicas do paciente,
    incluindo anamnese, histórico, diagnósticos e evolução
    """
    __tablename__ = 'prontuarios'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'),
                            nullable=False, unique=True, index=True)

    # Dados iniciais de admissão
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    profissional_abertura_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Anamnese
    queixa_principal = db.Column(db.Text)
    historia_doenca_atual = db.Column(db.Text)
    historia_previa = db.Column(db.Text)

    # Histórico de desenvolvimento
    gestacao = db.Column(db.Text)  # Informações sobre gestação
    parto = db.Column(db.Text)  # Tipo de parto, intercorrências
    desenvolvimento_motor = db.Column(db.Text)  # Marcos motores
    desenvolvimento_linguagem = db.Column(db.Text)  # Marcos de linguagem
    desenvolvimento_social = db.Column(db.Text)  # Marcos sociais

    # Histórico médico
    diagnosticos = db.Column(db.Text)  # JSON array de diagnósticos
    medicamentos_uso = db.Column(db.Text)  # JSON array de medicamentos
    alergias = db.Column(db.Text)  # JSON array de alergias
    cirurgias_previas = db.Column(db.Text)  # JSON array de cirurgias
    internacoes_previas = db.Column(db.Text)  # JSON array de internações

    # Histórico familiar
    historia_familiar = db.Column(db.Text)

    # Contexto social e educacional
    escola = db.Column(db.String(200))
    serie_ano = db.Column(db.String(50))
    possui_aee = db.Column(db.Boolean)  # Atendimento Educacional Especializado
    possui_cuidador = db.Column(db.Boolean)
    composicao_familiar = db.Column(db.Text)

    # Objetivos gerais do tratamento
    objetivos_gerais = db.Column(db.Text)

    # Observações gerais
    observacoes = db.Column(db.Text)

    # Status
    status = db.Column(db.String(20), default='ativo', nullable=False)  # ativo, alta, transferido, inativo
    data_encerramento = db.Column(db.DateTime)
    motivo_encerramento = db.Column(db.Text)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    paciente = db.relationship('Paciente', backref=db.backref('prontuario', uselist=False))
    profissional_abertura = db.relationship('User', foreign_keys=[profissional_abertura_id])
    atendimentos = db.relationship('Atendimento', back_populates='prontuario',
                                   lazy='dynamic', cascade='all, delete-orphan',
                                   order_by='desc(Atendimento.data_hora)')
    planos_terapeuticos = db.relationship('PlanoTerapeutico', back_populates='prontuario',
                                          lazy='dynamic', cascade='all, delete-orphan',
                                          order_by='desc(PlanoTerapeutico.data_inicio)')

    def __repr__(self):
        return f'<Prontuario Paciente: {self.paciente_id}>'

    def get_diagnosticos_list(self):
        """Retorna lista de diagnósticos"""
        import json
        try:
            return json.loads(self.diagnosticos) if self.diagnosticos else []
        except:
            return []

    def get_medicamentos_list(self):
        """Retorna lista de medicamentos"""
        import json
        try:
            return json.loads(self.medicamentos_uso) if self.medicamentos_uso else []
        except:
            return []

    def get_alergias_list(self):
        """Retorna lista de alergias"""
        import json
        try:
            return json.loads(self.alergias) if self.alergias else []
        except:
            return []

    def get_status_badge_class(self):
        """Retorna classe CSS para badge de status"""
        classes = {
            'ativo': 'bg-success',
            'alta': 'bg-info',
            'transferido': 'bg-warning',
            'inativo': 'bg-secondary'
        }
        return classes.get(self.status, 'bg-secondary')

    def get_ultimo_atendimento(self):
        """Retorna o último atendimento registrado"""
        return self.atendimentos.first()

    def get_plano_terapeutico_ativo(self):
        """Retorna o plano terapêutico ativo"""
        return self.planos_terapeuticos.filter_by(status='ativo').first()

    def count_atendimentos(self):
        """Conta total de atendimentos"""
        return self.atendimentos.count()
