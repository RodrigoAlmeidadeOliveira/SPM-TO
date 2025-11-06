"""
Módulo de formulários da aplicação SPM-TO
"""
from app.forms.auth_forms import LoginForm
from app.forms.paciente_form import PacienteForm
from app.forms.avaliacao_form import AvaliacaoForm, RespostaForm
from app.forms.user_forms import UserForm, UserCreateForm, UserEditForm
from app.forms.instrumento_forms import InstrumentoForm

__all__ = [
    'LoginForm',
    'PacienteForm',
    'InstrumentoForm',
    'AvaliacaoForm',
    'RespostaForm',
    'UserForm',
    'UserCreateForm',
    'UserEditForm'
]
