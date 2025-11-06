"""
Formulários para gerenciamento de domínios de instrumento
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class DominioForm(FlaskForm):
    """Cadastro/Edição de domínio"""

    codigo = StringField(
        'Código',
        validators=[
            DataRequired(message='Informe o código do domínio'),
            Length(max=10, message='O código deve ter no máximo 10 caracteres')
        ],
        render_kw={'placeholder': 'Ex: SOC, VIS', 'class': 'form-control'}
    )

    nome = StringField(
        'Nome',
        validators=[
            DataRequired(message='Informe o nome do domínio'),
            Length(max=200, message='O nome deve ter no máximo 200 caracteres')
        ],
        render_kw={'placeholder': 'Ex: Participação Social', 'class': 'form-control'}
    )

    ordem = IntegerField(
        'Ordem',
        validators=[
            DataRequired(message='Informe a ordem do domínio'),
            NumberRange(min=1, max=20, message='A ordem deve estar entre 1 e 20')
        ],
        render_kw={'class': 'form-control', 'min': 1, 'max': 20}
    )

    escala_invertida = BooleanField(
        'Utiliza escala invertida',
        default=False,
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Salvar Domínio', render_kw={'class': 'btn btn-primary'})
