"""
Formulários para gerenciamento de questões de instrumento
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class QuestaoForm(FlaskForm):
    """Cadastro/Edição de questão"""

    numero = IntegerField(
        'Número (dentro do domínio)',
        validators=[
            DataRequired(message='Informe o número da questão'),
            NumberRange(min=1, max=200, message='O número deve estar entre 1 e 200')
        ],
        render_kw={'class': 'form-control', 'min': 1}
    )

    numero_global = IntegerField(
        'Número global',
        validators=[
            DataRequired(message='Informe o número global da questão'),
            NumberRange(min=1, max=500, message='O número global deve estar entre 1 e 500')
        ],
        render_kw={'class': 'form-control', 'min': 1}
    )

    texto = TextAreaField(
        'Descrição da questão',
        validators=[
            DataRequired(message='Descreva a questão'),
            Length(max=2000, message='A descrição deve ter no máximo 2000 caracteres')
        ],
        render_kw={'class': 'form-control', 'rows': 4}
    )

    ativo = BooleanField(
        'Questão ativa',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Salvar Questão', render_kw={'class': 'btn btn-primary'})
