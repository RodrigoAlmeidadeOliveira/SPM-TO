"""Testes para geração de gráficos em múltiplos formatos."""
import base64
import pytest

try:
    import kaleido  # noqa: F401
    KALEIDO_AVAILABLE = True
except ImportError:  # pragma: no cover - ambiente sem dependência opcional
    KALEIDO_AVAILABLE = False

from app.services.grafico_service import GraficoService


@pytest.mark.skipif(not KALEIDO_AVAILABLE, reason='Dependência kaleido não instalada')
def test_obter_grafico_radar_retorna_png(db_session, avaliacao_completa):
    """Deve gerar representação em imagem para o gráfico radar."""
    dados = GraficoService.obter_grafico_radar(
        avaliacao_completa,
        incluir_html=False,
        incluir_png=True
    )

    conteudo = dados.get('png_base64')
    assert conteudo, 'Esperado base64 com o gráfico radar'
    assert base64.b64decode(conteudo), 'Base64 inválido para o gráfico radar'


@pytest.mark.skipif(not KALEIDO_AVAILABLE, reason='Dependência kaleido não instalada')
def test_obter_grafico_barras_retorna_png(db_session, avaliacao_completa):
    """Deve gerar representação em imagem para o gráfico de barras."""
    dados = GraficoService.obter_grafico_barras(
        avaliacao_completa,
        incluir_html=False,
        incluir_png=True
    )

    conteudo = dados.get('png_base64')
    assert conteudo, 'Esperado base64 com o gráfico de barras'
    assert base64.b64decode(conteudo), 'Base64 inválido para o gráfico de barras'
