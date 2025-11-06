"""
Formulários WTForms
"""
from app.forms.auth_forms import LoginForm
from app.forms.paciente_forms import PacienteForm
from app.forms.avaliacao_forms import AvaliacaoForm, RespostaForm
from app.forms.user_forms import UserForm

__all__ = [
    'LoginForm',
    'PacienteForm',
    'AvaliacaoForm',
    'RespostaForm',
    'UserForm'
]
