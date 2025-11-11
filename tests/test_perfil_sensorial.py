"""Testes para o módulo Perfil Sensorial 2."""
from app.services.modulos_service import ModulosService


def test_calcular_perfil_sensorial_retornando_secoes(db_session, avaliacao_perfil_sensorial):
    """Deve calcular os escores das seções sensoriais corretamente."""
    resultado = ModulosService.calcular_perfil_sensorial(avaliacao_perfil_sensorial.id)

    assert resultado is not None
    auditivo = resultado['secoes']['AUDITIVO']
    assert auditivo['escore_bruto'] == 40  # 8 questões x 5 pontos
    assert auditivo['classificacao']['nivel'] == 'MUITO_MAIS'

    visual = resultado['secoes']['VISUAL']
    assert visual['escore_bruto'] == 28
    assert visual['classificacao']['nivel'] == 'MUITO_MAIS'


def test_relatorio_perfil_sensorial_quadrantes(db_session, avaliacao_perfil_sensorial):
    """Relatório estruturado deve listar quadrantes e interpretações."""
    relatorio = ModulosService.gerar_relatorio_perfil_sensorial(avaliacao_perfil_sensorial.id)

    assert relatorio['secoes']
    quadrantes = {item['quadrante']: item for item in relatorio['quadrantes']}
    assert 'EXPLORACAO' in quadrantes
    assert 'ESQUIVA' in quadrantes
    assert relatorio['interpretacao_geral']
