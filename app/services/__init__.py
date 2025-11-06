"""
Camada de Serviços (Service Layer)
Contém a lógica de negócio da aplicação
"""
from app.services.calculo_service import CalculoService
from app.services.classificacao_service import ClassificacaoService

__all__ = ['CalculoService', 'ClassificacaoService']
