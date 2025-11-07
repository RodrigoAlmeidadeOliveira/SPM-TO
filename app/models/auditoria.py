"""
Modelo de Auditoria de Acessos
"""
from datetime import datetime
from app import db


class AuditoriaAcesso(db.Model):
    """Registra todos os acessos a pacientes e avaliações"""
    __tablename__ = 'auditoria_acessos'

    id = db.Column(db.Integer, primary_key=True)

    # Quem acessou
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # O que foi acessado
    recurso_tipo = db.Column(db.String(50), nullable=False)  # 'paciente', 'avaliacao', 'relatorio'
    recurso_id = db.Column(db.Integer, nullable=False)

    # Ação realizada
    acao = db.Column(db.String(50), nullable=False)  # 'visualizar', 'editar', 'excluir', 'criar', 'exportar'

    # Detalhes do acesso
    ip_address = db.Column(db.String(45))  # Suporta IPv6
    user_agent = db.Column(db.String(500))

    # Timestamp
    data_acesso = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relacionamentos
    user = db.relationship('User', backref='acessos_auditados')

    def __repr__(self):
        return f'<AuditoriaAcesso {self.user_id} - {self.recurso_tipo}:{self.recurso_id} - {self.acao}>'


class CompartilhamentoPaciente(db.Model):
    """Histórico de compartilhamentos de pacientes entre profissionais"""
    __tablename__ = 'compartilhamentos_paciente'

    id = db.Column(db.Integer, primary_key=True)

    # Paciente compartilhado
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False)

    # Quem compartilhou
    compartilhou_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Com quem foi compartilhado
    recebeu_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Tipo de acesso concedido
    tipo_acesso = db.Column(db.String(20), nullable=False, default='leitura')  # 'leitura', 'edicao', 'completo'

    # Status
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    data_compartilhamento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_revogacao = db.Column(db.DateTime)

    # Motivo/observações
    motivo = db.Column(db.Text)

    # Relacionamentos
    paciente = db.relationship('Paciente', backref='historico_compartilhamentos')
    compartilhou_por = db.relationship('User', foreign_keys=[compartilhou_user_id], backref='compartilhamentos_feitos')
    recebeu_por = db.relationship('User', foreign_keys=[recebeu_user_id], backref='compartilhamentos_recebidos')

    def __repr__(self):
        return f'<CompartilhamentoPaciente P:{self.paciente_id} -> U:{self.recebeu_user_id}>'
