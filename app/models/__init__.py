"""
Modelos de dados SPM-TO
"""
from app.models.user import User
from app.models.paciente import Paciente
from app.models.instrumento import Instrumento, Dominio, Questao, TabelaReferencia
from app.models.avaliacao import Avaliacao, Resposta
from app.models.plano import PlanoTemplateItem, PlanoItem

__all__ = [
    'User',
    'Paciente',
    'Instrumento',
    'Dominio',
    'Questao',
    'TabelaReferencia',
    'Avaliacao',
    'Resposta',
    'PlanoTemplateItem',
    'PlanoItem'
]
