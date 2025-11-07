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
from app.forms.tabela_referencia_forms import TabelaReferenciaForm
from app.forms.pei_forms import PlanoTemplateItemForm, PlanoItemSelecaoForm
from app.forms.prontuario_forms import ProntuarioForm, EncerrarProntuarioForm
from app.forms.atendimento_forms import AtendimentoForm, FinalizarAtendimentoForm
from app.forms.plano_terapeutico_forms import (
    PlanoTerapeuticoForm, AlterarStatusPlanoForm,
    ObjetivoTerapeuticoForm, AtualizarProgressoObjetivoForm
)

__all__ = [
    'LoginForm',
    'PacienteForm',
    'InstrumentoForm',
    'DominioForm',
    'QuestaoForm',
    'TabelaReferenciaForm',
    'AvaliacaoForm',
    'RespostaForm',
    'UserForm',
    'UserCreateForm',
    'UserEditForm',
    'PlanoTemplateItemForm',
    'PlanoItemSelecaoForm',
    'ProntuarioForm',
    'EncerrarProntuarioForm',
    'AtendimentoForm',
    'FinalizarAtendimentoForm',
    'PlanoTerapeuticoForm',
    'AlterarStatusPlanoForm',
    'ObjetivoTerapeuticoForm',
    'AtualizarProgressoObjetivoForm'
]
