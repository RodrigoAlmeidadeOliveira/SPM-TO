"""
Modelo de Objetivo Terapêutico - Objetivos específicos do plano terapêutico
"""
from datetime import datetime
from app import db


class ObjetivoTerapeutico(db.Model):
    """
    Modelo de Objetivo Terapêutico

    Representa objetivos específicos e mensuráveis dentro de um plano terapêutico
    """
    __tablename__ = 'objetivos_terapeuticos'

    id = db.Column(db.Integer, primary_key=True)
    plano_id = db.Column(db.Integer, db.ForeignKey('planos_terapeuticos.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    # Descrição do objetivo
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(100))  # Área do objetivo (ex: Motricidade, AVD, Social)

    # Prioridade
    prioridade = db.Column(db.Integer, default=1)  # 1=alta, 2=média, 3=baixa

    # Tipo de objetivo
    tipo = db.Column(db.String(50), default='curto_prazo')  # curto_prazo, medio_prazo, longo_prazo

    # Mensuração
    criterio_sucesso = db.Column(db.Text)  # Como será medido o sucesso
    meta_quantitativa = db.Column(db.String(200))  # Meta numérica (ex: "80% de acertos")

    # Estratégias específicas
    estrategias = db.Column(db.Text)  # Como alcançar o objetivo
    recursos = db.Column(db.Text)  # Recursos necessários

    # Prazo
    prazo_estimado = db.Column(db.Date)  # Data estimada para atingir

    # Progresso
    status = db.Column(db.String(20), default='em_andamento', nullable=False)
    # em_andamento, atingido, parcialmente_atingido, nao_atingido, cancelado

    percentual_progresso = db.Column(db.Integer, default=0)  # 0-100
    data_atingido = db.Column(db.Date)

    # Evolução do objetivo
    evolucoes = db.Column(db.Text)  # JSON array de registros de evolução

    # Observações
    observacoes = db.Column(db.Text)

    # Auditoria
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    plano = db.relationship('PlanoTerapeutico', back_populates='objetivos')

    def __repr__(self):
        return f'<ObjetivoTerapeutico {self.id}: {self.descricao[:50]}>'

    def get_prioridade_display(self):
        """Retorna nome amigável da prioridade"""
        prioridades = {
            1: 'Alta',
            2: 'Média',
            3: 'Baixa'
        }
        return prioridades.get(self.prioridade, 'Não definida')

    def get_prioridade_badge_class(self):
        """Retorna classe CSS para badge de prioridade"""
        classes = {
            1: 'bg-danger',  # Alta
            2: 'bg-warning',  # Média
            3: 'bg-info'  # Baixa
        }
        return classes.get(self.prioridade, 'bg-secondary')

    def get_tipo_display(self):
        """Retorna nome amigável do tipo"""
        tipos = {
            'curto_prazo': 'Curto Prazo',
            'medio_prazo': 'Médio Prazo',
            'longo_prazo': 'Longo Prazo'
        }
        return tipos.get(self.tipo, self.tipo)

    def get_status_display(self):
        """Retorna nome amigável do status"""
        status_map = {
            'em_andamento': 'Em Andamento',
            'atingido': 'Atingido',
            'parcialmente_atingido': 'Parcialmente Atingido',
            'nao_atingido': 'Não Atingido',
            'cancelado': 'Cancelado'
        }
        return status_map.get(self.status, self.status)

    def get_status_badge_class(self):
        """Retorna classe CSS para badge de status"""
        classes = {
            'em_andamento': 'bg-primary',
            'atingido': 'bg-success',
            'parcialmente_atingido': 'bg-info',
            'nao_atingido': 'bg-danger',
            'cancelado': 'bg-secondary'
        }
        return classes.get(self.status, 'bg-secondary')

    def get_evolucoes_list(self):
        """Retorna lista de evoluções"""
        import json
        try:
            return json.loads(self.evolucoes) if self.evolucoes else []
        except:
            return []

    def adicionar_evolucao(self, descricao, percentual=None):
        """Adiciona uma evolução ao objetivo"""
        import json
        evolucoes = self.get_evolucoes_list()
        nova_evolucao = {
            'data': datetime.utcnow().isoformat(),
            'descricao': descricao,
            'percentual': percentual or self.percentual_progresso
        }
        evolucoes.append(nova_evolucao)
        self.evolucoes = json.dumps(evolucoes, ensure_ascii=False)

        if percentual is not None:
            self.percentual_progresso = percentual

            # Atualizar status baseado no percentual
            if percentual >= 100:
                self.status = 'atingido'
                self.data_atingido = datetime.utcnow().date()
            elif percentual >= 50:
                self.status = 'parcialmente_atingido'

    def is_vencido(self):
        """Verifica se o prazo do objetivo foi ultrapassado"""
        if not self.prazo_estimado:
            return False
        from datetime import date
        return date.today() > self.prazo_estimado and self.status not in ['atingido', 'cancelado']

    def dias_para_prazo(self):
        """Calcula dias restantes até o prazo"""
        if not self.prazo_estimado:
            return None
        from datetime import date
        delta = self.prazo_estimado - date.today()
        return delta.days
