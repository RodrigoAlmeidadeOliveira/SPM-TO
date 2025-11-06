"""
Formulários de Paciente
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class PacienteForm(FlaskForm):
    """Formulário de cadastro/edição de paciente"""
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=200, message='Nome deve ter entre 3 e 200 caracteres')
    ])

    identificacao = StringField('Número de Identificação', validators=[
        Optional(),
        Length(max=100)
    ])

    data_nascimento = DateField('Data de Nascimento', validators=[
        DataRequired(message='Campo obrigatório')
    ], format='%Y-%m-%d')

    sexo = SelectField('Sexo', validators=[
        DataRequired(message='Campo obrigatório')
    ], choices=[
        ('', 'Selecione...'),
        ('M', 'Masculino'),
        ('F', 'Feminino')
    ])

    raca_etnia = StringField('Raça/Etnia', validators=[
        Optional(),
        Length(max=100)
    ])

    observacoes = TextAreaField('Observações', validators=[
        Optional()
    ])

    submit = SubmitField('Salvar')
