"""
Formulários para Prontuário Eletrônico
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class ProntuarioForm(FlaskForm):
    """Formulário para abertura e edição de prontuário"""

    # Queixa e história
    queixa_principal = TextAreaField(
        'Queixa Principal',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva a queixa principal que motivou a busca pelo atendimento...',
            'class': 'form-control',
            'rows': 3
        }
    )

    historia_doenca_atual = TextAreaField(
        'História da Doença Atual (HDA)',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Evolução da queixa atual, quando iniciou, características, fatores de melhora/piora...',
            'class': 'form-control',
            'rows': 4
        }
    )

    historia_previa = TextAreaField(
        'História Pregressa',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Doenças prévias, hospitalizações, cirurgias, uso de medicamentos...',
            'class': 'form-control',
            'rows': 3
        }
    )

    # Desenvolvimento
    gestacao = TextAreaField(
        'Gestação',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Intercorrências na gestação, pré-natal, uso de medicamentos...',
            'class': 'form-control',
            'rows': 3
        }
    )

    parto = TextAreaField(
        'Parto',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Tipo de parto, idade gestacional, peso ao nascer, APGAR, intercorrências...',
            'class': 'form-control',
            'rows': 3
        }
    )

    desenvolvimento_motor = TextAreaField(
        'Desenvolvimento Motor',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Marcos do desenvolvimento motor (sentar, engatinhar, andar, correr, pular...)...',
            'class': 'form-control',
            'rows': 3
        }
    )

    desenvolvimento_linguagem = TextAreaField(
        'Desenvolvimento de Linguagem',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Primeiras palavras, frases, compreensão, dificuldades de comunicação...',
            'class': 'form-control',
            'rows': 3
        }
    )

    desenvolvimento_social = TextAreaField(
        'Desenvolvimento Social',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Interação social, brincadeiras, relacionamentos, autonomia...',
            'class': 'form-control',
            'rows': 3
        }
    )

    # Histórico médico (serão JSON no backend)
    diagnosticos = TextAreaField(
        'Diagnósticos Médicos',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Liste os diagnósticos médicos (um por linha)...',
            'class': 'form-control',
            'rows': 3
        }
    )

    medicamentos_uso = TextAreaField(
        'Medicamentos em Uso',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Liste os medicamentos e dosagens (um por linha)...',
            'class': 'form-control',
            'rows': 3
        }
    )

    alergias = TextAreaField(
        'Alergias',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Liste alergias conhecidas (uma por linha)...',
            'class': 'form-control',
            'rows': 2
        }
    )

    cirurgias_previas = TextAreaField(
        'Cirurgias Prévias',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Liste cirurgias realizadas com datas (uma por linha)...',
            'class': 'form-control',
            'rows': 2
        }
    )

    internacoes_previas = TextAreaField(
        'Internações Prévias',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Liste internações hospitalares com motivos e datas (uma por linha)...',
            'class': 'form-control',
            'rows': 2
        }
    )

    # História familiar
    historia_familiar = TextAreaField(
        'História Familiar',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Doenças ou condições relevantes na família...',
            'class': 'form-control',
            'rows': 3
        }
    )

    # Contexto
    escola = StringField(
        'Escola',
        validators=[Optional(), Length(max=200)],
        render_kw={
            'placeholder': 'Nome da escola',
            'class': 'form-control'
        }
    )

    serie_ano = StringField(
        'Série/Ano',
        validators=[Optional(), Length(max=50)],
        render_kw={
            'placeholder': 'Ex: 3º ano',
            'class': 'form-control'
        }
    )

    possui_aee = BooleanField(
        'Possui AEE (Atendimento Educacional Especializado)',
        render_kw={'class': 'form-check-input'}
    )

    possui_cuidador = BooleanField(
        'Possui Cuidador',
        render_kw={'class': 'form-check-input'}
    )

    composicao_familiar = TextAreaField(
        'Composição Familiar',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva a composição familiar e dinâmica...',
            'class': 'form-control',
            'rows': 3
        }
    )

    # Objetivos
    objetivos_gerais = TextAreaField(
        'Objetivos Gerais do Tratamento',
        validators=[Optional(), Length(max=3000)],
        render_kw={
            'placeholder': 'Descreva os objetivos gerais e expectativas para o tratamento...',
            'class': 'form-control',
            'rows': 4
        }
    )

    # Observações
    observacoes = TextAreaField(
        'Observações Gerais',
        validators=[Optional(), Length(max=5000)],
        render_kw={
            'placeholder': 'Outras informações relevantes...',
            'class': 'form-control',
            'rows': 3
        }
    )


class EncerrarProntuarioForm(FlaskForm):
    """Formulário para encerramento de prontuário"""

    status = SelectField(
        'Status',
        choices=[
            ('alta', 'Alta'),
            ('transferido', 'Transferido'),
            ('inativo', 'Inativo')
        ],
        validators=[DataRequired(message='O status é obrigatório')],
        render_kw={'class': 'form-select'}
    )

    data_encerramento = DateField(
        'Data de Encerramento',
        validators=[DataRequired(message='A data de encerramento é obrigatória')],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    motivo_encerramento = TextAreaField(
        'Motivo do Encerramento',
        validators=[DataRequired(message='O motivo é obrigatório'), Length(max=2000)],
        render_kw={
            'placeholder': 'Descreva o motivo do encerramento...',
            'class': 'form-control',
            'rows': 4
        }
    )
