"""
Módulo de formulários da aplicação SPM-TO
"""
from app.forms.auth_forms import LoginForm
from app.forms.paciente_form import PacienteForm
from app.forms.avaliacao_form import AvaliacaoForm, RespostaForm
from app.forms.user_forms import UserForm, UserCreateForm, UserEditForm
from app.forms.instrumento_forms import InstrumentoForm
from app.forms.dominio_forms import DominioForm
from app.forms.questao_forms import QuestaoForm
from app.forms.pei_forms import PlanoTemplateItemForm, PlanoItemSelecaoForm

__all__ = [
    'LoginForm',
    'PacienteForm',
    'InstrumentoForm',
    'DominioForm',
    'QuestaoForm',
    'AvaliacaoForm',
    'RespostaForm',
    'UserForm',
    'UserCreateForm',
    'UserEditForm',
    'PlanoTemplateItemForm',
    'PlanoItemSelecaoForm'
]
