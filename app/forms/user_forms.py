"""
Formulários de Usuário
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class UserForm(FlaskForm):
    """Formulário de cadastro/edição de usuário"""
    username = StringField('Nome de Usuário', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=80, message='Usuário deve ter entre 3 e 80 caracteres')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Campo obrigatório'),
        Email(message='Email inválido'),
        Length(max=120)
    ])

    nome_completo = StringField('Nome Completo', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=200)
    ])

    tipo = SelectField('Tipo de Usuário', validators=[
        DataRequired(message='Campo obrigatório')
    ], choices=[
        ('', 'Selecione...'),
        ('admin', 'Administrador'),
        ('terapeuta', 'Terapeuta'),
        ('professor', 'Professor'),
        ('familiar', 'Familiar')
    ])

    password = PasswordField('Senha', validators=[
        Optional(),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])

    password_confirm = PasswordField('Confirmar Senha', validators=[
        EqualTo('password', message='As senhas devem ser iguais')
    ])

    ativo = BooleanField('Usuário Ativo', default=True)

    submit = SubmitField('Salvar')
