"""
Formulários relacionados a Instrumentos SPM
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class InstrumentoForm(FlaskForm):
    """Formulário de cadastro/edição de instrumentos"""

    codigo = StringField(
        'Código',
        validators=[
            DataRequired(message='Informe o código do instrumento'),
            Length(max=50, message='O código deve ter no máximo 50 caracteres')
        ],
        render_kw={'placeholder': 'Ex: SPM_P_3_5_CASA', 'class': 'form-control'}
    )

    nome = StringField(
        'Nome',
        validators=[
            DataRequired(message='Informe o nome do instrumento'),
            Length(max=200, message='O nome deve ter no máximo 200 caracteres')
        ],
        render_kw={'placeholder': 'Ex: SPM-P 3-5 anos - Casa', 'class': 'form-control'}
    )

    descricao = TextAreaField(
        'Descrição',
        validators=[Optional(), Length(max=2000, message='A descrição deve ter no máximo 2000 caracteres')],
        render_kw={
            'placeholder': 'Resumo do objetivo do instrumento, população alvo, etc.',
            'class': 'form-control',
            'rows': 3
        }
    )

    contexto = SelectField(
        'Contexto',
        choices=[
            ('', 'Selecione...'),
            ('casa', 'Casa'),
            ('escola', 'Escola'),
            ('clinica', 'Clínica'),
            ('hospital', 'Hospital'),
            ('geral', 'Geral'),
            ('comunidade', 'Comunidade')
        ],
        validators=[DataRequired(message='Selecione o contexto do instrumento')],
        render_kw={'class': 'form-select'}
    )

    idade_minima = IntegerField(
        'Idade mínima (anos)',
        validators=[
            DataRequired(message='Informe a idade mínima'),
            NumberRange(min=0, max=120, message='A idade mínima deve estar entre 0 e 120 anos')
        ],
        render_kw={'class': 'form-control', 'min': 0, 'max': 120}
    )

    idade_maxima = IntegerField(
        'Idade máxima (anos)',
        validators=[
            DataRequired(message='Informe a idade máxima'),
            NumberRange(min=0, max=120, message='A idade máxima deve estar entre 0 e 120 anos')
        ],
        render_kw={'class': 'form-control', 'min': 0, 'max': 120}
    )

    instrucoes = TextAreaField(
        'Instruções',
        validators=[
            Optional(),
            Length(max=5000, message='As instruções devem ter no máximo 5000 caracteres')
        ],
        render_kw={
            'placeholder': 'Instruções gerais para aplicação do instrumento...',
            'class': 'form-control',
            'rows': 4
        }
    )

    ativo = BooleanField(
        'Instrumento ativo',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Salvar Instrumento', render_kw={'class': 'btn btn-primary'})

    def validate(self, extra_validators=None):
        """Validações extras"""
        initial_validation = super().validate(extra_validators=extra_validators)
        if not initial_validation:
            return False

        if self.idade_maxima.data is not None and self.idade_minima.data is not None:
            if self.idade_maxima.data < self.idade_minima.data:
                self.idade_maxima.errors.append('A idade máxima deve ser maior ou igual à idade mínima.')
                return False

        return True
