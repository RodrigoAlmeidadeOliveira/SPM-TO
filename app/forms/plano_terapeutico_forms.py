"""
Formulários para Plano Terapêutico e Objetivos Terapêuticos
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from datetime import date


class PlanoTerapeuticoForm(FlaskForm):
    """Formulário para criar/editar plano terapêutico"""

    titulo = StringField(
        'Título do Plano',
        validators=[
            DataRequired(message='O título é obrigatório'),
            Length(min=5, max=200, message='O título deve ter entre 5 e 200 caracteres')
        ],
        render_kw={'placeholder': 'Ex: Plano Terapêutico Semestral - Integração Sensorial', 'class': 'form-control'}
    )

    descricao = TextAreaField(
        'Descrição',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva brevemente o foco e propósito deste plano terapêutico...',
            'class': 'form-control',
            'rows': 3
        }
    )

    data_inicio = DateField(
        'Data de Início',
        validators=[DataRequired(message='A data de início é obrigatória')],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    data_fim = DateField(
        'Data de Término (prevista)',
        validators=[Optional()],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    duracao_prevista_meses = IntegerField(
        'Duração Prevista (meses)',
        validators=[Optional(), NumberRange(min=1, max=60, message='A duração deve estar entre 1 e 60 meses')],
        render_kw={'placeholder': 'Ex: 6', 'class': 'form-control'}
    )

    frequencia_semanal = IntegerField(
        'Frequência Semanal (sessões)',
        validators=[Optional(), NumberRange(min=1, max=7, message='A frequência deve estar entre 1 e 7 sessões')],
        render_kw={'placeholder': 'Ex: 2', 'class': 'form-control'}
    )

    duracao_sessao_minutos = IntegerField(
        'Duração da Sessão (minutos)',
        validators=[Optional(), NumberRange(min=15, max=240, message='A duração deve estar entre 15 e 240 minutos')],
        render_kw={'placeholder': 'Ex: 60', 'class': 'form-control'}
    )

    areas_foco = TextAreaField(
        'Áreas de Foco',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Liste as áreas de foco do tratamento (uma por linha)...\nEx: Motricidade Fina, Integração Sensorial, AVDs',
            'class': 'form-control',
            'rows': 3
        }
    )

    estrategias_gerais = TextAreaField(
        'Estratégias Gerais',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Descreva as estratégias gerais que serão utilizadas...',
            'class': 'form-control',
            'rows': 4
        }
    )

    recursos_necessarios = TextAreaField(
        'Recursos Necessários',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Liste os recursos e materiais necessários...',
            'class': 'form-control',
            'rows': 3
        }
    )

    orientacoes_familia = TextAreaField(
        'Orientações para a Família',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Orientações específicas para a família seguir em casa...',
            'class': 'form-control',
            'rows': 3
        }
    )

    orientacoes_escola = TextAreaField(
        'Orientações para a Escola',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Orientações específicas para o contexto escolar...',
            'class': 'form-control',
            'rows': 3
        }
    )

    orientacoes_equipe = TextAreaField(
        'Orientações para a Equipe Multidisciplinar',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Orientações para outros profissionais da equipe...',
            'class': 'form-control',
            'rows': 3
        }
    )

    criterios_alta = TextAreaField(
        'Critérios de Alta',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva os critérios para considerar a alta do tratamento...',
            'class': 'form-control',
            'rows': 3
        }
    )

    observacoes = TextAreaField(
        'Observações',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Outras observações relevantes...',
            'class': 'form-control',
            'rows': 2
        }
    )

    def validate_data_fim(self, field):
        """Valida se a data de término é posterior à data de início"""
        if field.data and self.data_inicio.data:
            if field.data < self.data_inicio.data:
                raise ValidationError('A data de término deve ser posterior à data de início')


class AlterarStatusPlanoForm(FlaskForm):
    """Formulário para alterar status do plano"""

    status = SelectField(
        'Status',
        choices=[
            ('ativo', 'Ativo'),
            ('concluido', 'Concluído'),
            ('cancelado', 'Cancelado'),
            ('suspenso', 'Suspenso')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )

    motivo_status = TextAreaField(
        'Motivo da Alteração',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Descreva o motivo da alteração de status...',
            'class': 'form-control',
            'rows': 3
        }
    )


class ObjetivoTerapeuticoForm(FlaskForm):
    """Formulário para criar/editar objetivo terapêutico"""

    descricao = TextAreaField(
        'Descrição do Objetivo',
        validators=[
            DataRequired(message='A descrição é obrigatória'),
            Length(min=10, max=1000, message='A descrição deve ter entre 10 e 1000 caracteres')
        ],
        render_kw={
            'placeholder': 'Descreva o objetivo de forma clara e mensurável...',
            'class': 'form-control',
            'rows': 3
        }
    )

    area = StringField(
        'Área',
        validators=[Optional(), Length(max=100)],
        render_kw={
            'placeholder': 'Ex: Motricidade Fina, AVDs, Integração Sensorial',
            'class': 'form-control'
        }
    )

    prioridade = SelectField(
        'Prioridade',
        choices=[
            ('1', 'Alta'),
            ('2', 'Média'),
            ('3', 'Baixa')
        ],
        coerce=int,
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )

    tipo = SelectField(
        'Tipo de Objetivo',
        choices=[
            ('curto_prazo', 'Curto Prazo'),
            ('medio_prazo', 'Médio Prazo'),
            ('longo_prazo', 'Longo Prazo')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )

    criterio_sucesso = TextAreaField(
        'Critério de Sucesso',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Como será avaliado o sucesso deste objetivo?',
            'class': 'form-control',
            'rows': 2
        }
    )

    meta_quantitativa = StringField(
        'Meta Quantitativa',
        validators=[Optional(), Length(max=200)],
        render_kw={
            'placeholder': 'Ex: 80% de acertos, 5 repetições consecutivas',
            'class': 'form-control'
        }
    )

    estrategias = TextAreaField(
        'Estratégias',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva as estratégias para alcançar este objetivo...',
            'class': 'form-control',
            'rows': 3
        }
    )

    recursos = TextAreaField(
        'Recursos Necessários',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Materiais e recursos necessários...',
            'class': 'form-control',
            'rows': 2
        }
    )

    prazo_estimado = DateField(
        'Prazo Estimado',
        validators=[Optional()],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    observacoes = TextAreaField(
        'Observações',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Outras observações relevantes...',
            'class': 'form-control',
            'rows': 2
        }
    )

    def validate_prazo_estimado(self, field):
        """Valida se o prazo não é passado"""
        if field.data and field.data < date.today():
            raise ValidationError('O prazo estimado não pode ser uma data passada')


class AtualizarProgressoObjetivoForm(FlaskForm):
    """Formulário para atualizar progresso do objetivo"""

    percentual_progresso = IntegerField(
        'Progresso (%)',
        validators=[
            DataRequired(message='O percentual de progresso é obrigatório'),
            NumberRange(min=0, max=100, message='O percentual deve estar entre 0 e 100')
        ],
        render_kw={'class': 'form-control', 'min': 0, 'max': 100, 'type': 'number'}
    )

    descricao_evolucao = TextAreaField(
        'Descrição da Evolução',
        validators=[
            DataRequired(message='A descrição da evolução é obrigatória'),
            Length(min=10, max=1000)
        ],
        render_kw={
            'placeholder': 'Descreva a evolução observada...',
            'class': 'form-control',
            'rows': 3
        }
    )

    status = SelectField(
        'Status',
        choices=[
            ('em_andamento', 'Em Andamento'),
            ('parcialmente_atingido', 'Parcialmente Atingido'),
            ('atingido', 'Atingido'),
            ('nao_atingido', 'Não Atingido'),
            ('cancelado', 'Cancelado')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
