"""
Formulários para o sistema PEI (Plano Educacional Individualizado)
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class PlanoTemplateItemForm(FlaskForm):
    """Formulário para cadastro de item de template PEI"""
    instrumento_id = SelectField('Instrumento', coerce=int, validators=[DataRequired()])
    dominio_id = SelectField('Domínio', coerce=int, validators=[Optional()])
    ordem = IntegerField('Ordem', validators=[DataRequired()])
    texto = TextAreaField('Texto do Item', validators=[
        DataRequired(),
        Length(min=10, max=1000, message='O texto deve ter entre 10 e 1000 caracteres')
    ])
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')


class PlanoItemSelecaoForm(FlaskForm):
    """Formulário para seleção de itens do PEI para uma avaliação"""
    observacoes = TextAreaField('Observações Gerais', validators=[Optional()])
    submit = SubmitField('Gerar PEI')
