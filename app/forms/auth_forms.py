"""
Formulários de autenticação
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Formulário de login"""
    username = StringField('Usuário', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=80, message='Usuário deve ter entre 3 e 80 caracteres')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Campo obrigatório')
    ])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
