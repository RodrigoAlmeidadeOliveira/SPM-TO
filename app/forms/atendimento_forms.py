"""
Formulários para Atendimento (Sessões Terapêuticas)
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from datetime import datetime


class AtendimentoForm(FlaskForm):
    """Formulário para registro de atendimento com formato SOAP"""

    # Dados básicos
    data_hora = DateTimeField(
        'Data e Hora',
        validators=[DataRequired(message='A data e hora são obrigatórias')],
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local'}
    )

    duracao_minutos = IntegerField(
        'Duração (minutos)',
        validators=[Optional(), NumberRange(min=15, max=480, message='A duração deve estar entre 15 e 480 minutos')],
        render_kw={'placeholder': 'Ex: 60', 'class': 'form-control'}
    )

    tipo = SelectField(
        'Tipo de Atendimento',
        choices=[
            ('sessao', 'Sessão Terapêutica'),
            ('avaliacao', 'Avaliação Inicial'),
            ('reavaliacao', 'Reavaliação'),
            ('orientacao', 'Orientação')
        ],
        validators=[DataRequired(message='O tipo é obrigatório')],
        render_kw={'class': 'form-select'}
    )

    modalidade = SelectField(
        'Modalidade',
        choices=[
            ('', 'Selecione...'),
            ('presencial', 'Presencial'),
            ('online', 'Online/Teleatendimento'),
            ('domiciliar', 'Domiciliar'),
            ('escolar', 'Escolar')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    local = StringField(
        'Local do Atendimento',
        validators=[Optional(), Length(max=200)],
        render_kw={
            'placeholder': 'Ex: Clínica, Residência, Escola...',
            'class': 'form-control'
        }
    )

    # Comparecimento
    compareceu = BooleanField(
        'Paciente Compareceu',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    motivo_falta = TextAreaField(
        'Motivo da Falta',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Se o paciente não compareceu, descreva o motivo...',
            'class': 'form-control',
            'rows': 2
        }
    )

    # SOAP - Subjetivo
    subjetivo = TextAreaField(
        'S - Subjetivo',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Relato do paciente/responsável: queixas, observações da família, relatos sobre a semana...',
            'class': 'form-control',
            'rows': 4
        },
        description='Relatos subjetivos do paciente ou responsável'
    )

    # SOAP - Objetivo
    objetivo = TextAreaField(
        'O - Objetivo',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Observações objetivas do terapeuta: comportamentos observados, desempenho em atividades, mensurações...',
            'class': 'form-control',
            'rows': 4
        },
        description='Observações objetivas do profissional'
    )

    # SOAP - Avaliação
    avaliacao = TextAreaField(
        'A - Avaliação/Análise',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Análise clínica: interpretação dos dados, raciocínio clínico, progresso em relação aos objetivos...',
            'class': 'form-control',
            'rows': 4
        },
        description='Avaliação e análise clínica'
    )

    # SOAP - Plano
    plano = TextAreaField(
        'P - Plano',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Plano de ação: próximos passos, condutas, orientações, ajustes no tratamento...',
            'class': 'form-control',
            'rows': 4
        },
        description='Plano de ação e próximos passos'
    )

    # Intervenções
    intervencoes = TextAreaField(
        'Intervenções Realizadas',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Liste as intervenções realizadas durante a sessão (uma por linha)...',
            'class': 'form-control',
            'rows': 3
        }
    )

    recursos_utilizados = TextAreaField(
        'Recursos Utilizados',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Materiais, equipamentos e recursos utilizados...',
            'class': 'form-control',
            'rows': 2
        }
    )

    # Orientações
    orientacoes_familia = TextAreaField(
        'Orientações à Família',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Orientações e recomendações dadas à família...',
            'class': 'form-control',
            'rows': 3
        }
    )

    orientacoes_escola = TextAreaField(
        'Orientações à Escola',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Orientações e recomendações para o contexto escolar...',
            'class': 'form-control',
            'rows': 3
        }
    )

    # Observações
    observacoes = TextAreaField(
        'Observações Gerais',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Outras observações relevantes...',
            'class': 'form-control',
            'rows': 2
        }
    )

    def validate_data_hora(self, field):
        """Valida se a data não é futura"""
        if field.data and field.data > datetime.now():
            raise ValidationError('A data e hora não podem ser futuras')

    def validate_motivo_falta(self, field):
        """Valida se motivo da falta foi preenchido quando compareceu = False"""
        if not self.compareceu.data and not field.data:
            raise ValidationError('Informe o motivo da falta quando o paciente não comparecer')


class FinalizarAtendimentoForm(FlaskForm):
    """Formulário rápido para finalizar atendimento"""

    status = SelectField(
        'Status',
        choices=[
            ('finalizado', 'Finalizado'),
            ('revisado', 'Revisado')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
