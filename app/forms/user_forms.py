"""
Formulários de Usuário
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models.user import User


class UserCreateForm(FlaskForm):
    """Formulário de cadastro de usuário"""
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
        DataRequired(message='Campo obrigatório'),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])

    password_confirm = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Campo obrigatório'),
        EqualTo('password', message='As senhas devem ser iguais')
    ])

    ativo = BooleanField('Usuário Ativo', default=True)

    submit = SubmitField('Cadastrar')

    def validate_username(self, field):
        """Valida se username já existe"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, field):
        """Valida se email já existe"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email já está cadastrado.')


class UserEditForm(FlaskForm):
    """Formulário de edição de usuário"""
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

    password = PasswordField('Nova Senha (deixe em branco para não alterar)', validators=[
        Optional(),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])

    password_confirm = PasswordField('Confirmar Nova Senha', validators=[
        EqualTo('password', message='As senhas devem ser iguais')
    ])

    ativo = BooleanField('Usuário Ativo')

    submit = SubmitField('Salvar')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, field):
        """Valida se username já existe (exceto o próprio)"""
        if field.data != self.original_username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, field):
        """Valida se email já existe (exceto o próprio)"""
        if field.data != self.original_email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Este email já está cadastrado.')


# Mantém compatibilidade com código antigo
UserForm = UserCreateForm
