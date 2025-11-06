"""
Formulários WTForms
"""
from app.forms.auth_forms import LoginForm
from app.forms.paciente_form import PacienteForm
from app.forms.avaliacao_forms import AvaliacaoForm, RespostaForm
from app.forms.user_forms import UserForm, UserCreateForm, UserEditForm

__all__ = [
    'LoginForm',
    'PacienteForm',
    'AvaliacaoForm',
    'RespostaForm',
    'UserForm',
    'UserCreateForm',
    'UserEditForm'
]
