"""
Modelos de Avaliação e Resposta
"""
from datetime import datetime
from sqlalchemy.orm import validates
from app import db
from app.models.utils import coerce_date


class Avaliacao(db.Model):
    """Modelo de Avaliação"""
    __tablename__ = 'avaliacoes'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False, index=True)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False)
    avaliador_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Informações da avaliação (espelhando o cabeçalho das planilhas)
    data_avaliacao = db.Column(db.Date, nullable=False, index=True)
    relacionamento_respondente = db.Column(db.String(100), nullable=False, default='Responsavel')
    # Ex: 'pai', 'mãe', 'professor', 'terapeuta'

    # Comentários
    comentarios = db.Column(db.Text)

    # Status: 'em_andamento', 'concluida', 'revisao'
    status = db.Column(db.String(20), default='em_andamento', nullable=False)

    # Escores calculados por domínio
    escore_soc = db.Column(db.Integer)  # Participação Social
    escore_vis = db.Column(db.Integer)  # Visão
    escore_hea = db.Column(db.Integer)  # Audição (Hearing)
    escore_tou = db.Column(db.Integer)  # Tato (Touch)
    escore_bod = db.Column(db.Integer)  # Consciência Corporal (Body)
    escore_bal = db.Column(db.Integer)  # Equilíbrio e Movimento (Balance)
    escore_pla = db.Column(db.Integer)  # Planejamento e Ideação (Planning)
    escore_olf = db.Column(db.Integer)  # Olfato e Paladar (apenas SPM-P)
    escore_total = db.Column(db.Integer)

    # T-scores e classificações
    t_score_soc = db.Column(db.Integer)
    t_score_vis = db.Column(db.Integer)
    t_score_hea = db.Column(db.Integer)
    t_score_tou = db.Column(db.Integer)
    t_score_bod = db.Column(db.Integer)
    t_score_bal = db.Column(db.Integer)
    t_score_pla = db.Column(db.Integer)
    t_score_olf = db.Column(db.Integer)

    classificacao_soc = db.Column(db.String(50))
    classificacao_vis = db.Column(db.String(50))
    classificacao_hea = db.Column(db.String(50))
    classificacao_tou = db.Column(db.String(50))
    classificacao_bod = db.Column(db.String(50))
    classificacao_bal = db.Column(db.String(50))
    classificacao_pla = db.Column(db.String(50))
    classificacao_olf = db.Column(db.String(50))

    # T-score e classificação total
    t_score_tot = db.Column(db.Integer)
    classificacao_tot = db.Column(db.String(50))

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)
    data_conclusao = db.Column(db.DateTime)

    # Relacionamentos
    paciente = db.relationship('Paciente', back_populates='avaliacoes')
    instrumento = db.relationship('Instrumento', back_populates='avaliacoes')
    avaliador = db.relationship('User', back_populates='avaliacoes')
    respostas = db.relationship('Resposta', back_populates='avaliacao',
                                lazy='dynamic', cascade='all, delete-orphan')
    plano_itens = db.relationship('PlanoItem', back_populates='avaliacao',
                                  lazy='dynamic', cascade='all, delete-orphan')

    def calcular_escores(self):
        """
        Calcula os escores por domínio baseado nas respostas

        Returns:
            dict: Escores por domínio
        """
        from app.services.calculo_service import CalculoService
        return CalculoService.calcular_escores(self)

    def classificar_resultados(self):
        """
        Classifica os resultados baseado nos T-scores

        Returns:
            dict: Classificações por domínio
        """
        from app.services.classificacao_service import ClassificacaoService
        return ClassificacaoService.classificar_avaliacao(self)

    def esta_completa(self):
        """
        Verifica se a avaliação está completa (todas as questões respondidas)

        Returns:
            bool: True se completa
        """
        total_questoes = sum([d.questoes.filter_by(ativo=True).count()
                             for d in self.instrumento.dominios.filter_by(ativo=True)])
        total_respostas = self.respostas.count()
        return total_respostas >= total_questoes

    def __repr__(self):
        return f'<Avaliacao {self.id} - Paciente {self.paciente_id}>'

    @validates('data_avaliacao')
    def _validate_data_avaliacao(self, key, value):
        """Permite atribuir a data da avaliação usando string ou datetime."""
        return coerce_date(value, key)


class Resposta(db.Model):
    """Modelo de Resposta a uma questão"""
    __tablename__ = 'respostas'

    id = db.Column(db.Integer, primary_key=True)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacoes.id'),
                            nullable=False, index=True)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id'), nullable=False)

    # Valor da resposta: 'NUNCA', 'OCASIONAL', 'FREQUENTE', 'SEMPRE'
    valor = db.Column(db.String(20), nullable=False)

    # Pontuação calculada (1-4, dependendo se escala é invertida ou não)
    pontuacao = db.Column(db.Integer, nullable=False)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    avaliacao = db.relationship('Avaliacao', back_populates='respostas')
    questao = db.relationship('Questao', back_populates='respostas')

    __table_args__ = (
        db.UniqueConstraint('avaliacao_id', 'questao_id',
                           name='uq_avaliacao_questao'),
    )

    def __repr__(self):
        return f'<Resposta Q{self.questao_id}: {self.valor}>'
