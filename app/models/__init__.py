"""
Modelos de dados SPM-TO
"""
from app.models.user import User
from app.models.paciente import Paciente, paciente_responsavel
from app.models.instrumento import Instrumento, Dominio, Questao, TabelaReferencia
from app.models.avaliacao import Avaliacao, Resposta
from app.models.plano import PlanoTemplateItem, PlanoItem
from app.models.auditoria import AuditoriaAcesso, CompartilhamentoPaciente
from app.models.anexo import AnexoAvaliacao

# Novos modelos - Arquitetura modular e prontuário
from app.models.modulo import Modulo
from app.models.prontuario import Prontuario
from app.models.atendimento import Atendimento, atendimento_avaliacao
from app.models.plano_terapeutico import PlanoTerapeutico
from app.models.objetivo_terapeutico import ObjetivoTerapeutico

__all__ = [
    'User',
    'Paciente',
    'paciente_responsavel',
    'Instrumento',
    'Dominio',
    'Questao',
    'TabelaReferencia',
    'Avaliacao',
    'Resposta',
    'PlanoTemplateItem',
    'PlanoItem',
    'AuditoriaAcesso',
    'CompartilhamentoPaciente',
    'AnexoAvaliacao',
    # Novos modelos
    'Modulo',
    'Prontuario',
    'Atendimento',
    'atendimento_avaliacao',
    'PlanoTerapeutico',
    'ObjetivoTerapeutico'
]
