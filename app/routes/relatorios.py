"""
Blueprint de Relatórios
"""
from flask import Blueprint, render_template, Response, make_response
from flask_login import login_required
from app.models.avaliacao import Avaliacao
from app.models.paciente import Paciente
from app.services.grafico_service import GraficoService
from io import BytesIO

relatorios_bp = Blueprint('relatorios', __name__)


@relatorios_bp.route('/avaliacao/<int:id>')
@login_required
def avaliacao(id):
    """Relatório completo de avaliação"""
    avaliacao_obj = Avaliacao.query.get_or_404(id)

    # Gerar gráficos
    grafico_radar = None
    grafico_barras = None

    if avaliacao_obj.status == 'concluida':
        grafico_radar = GraficoService.criar_grafico_radar(avaliacao_obj)
        grafico_barras = GraficoService.criar_grafico_barras_comparativo(avaliacao_obj)

    return render_template('relatorios/avaliacao.html',
                          avaliacao=avaliacao_obj,
                          grafico_radar=grafico_radar,
                          grafico_barras=grafico_barras)


@relatorios_bp.route('/avaliacao/<int:id>/pdf')
@login_required
def avaliacao_pdf(id):
    """Gera relatório de avaliação em PDF"""
    from app.services.pdf_service import PDFService

    avaliacao_obj = Avaliacao.query.get_or_404(id)

    # Gerar PDF
    pdf_buffer = PDFService.gerar_relatorio_avaliacao(avaliacao_obj)

    # Criar resposta
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=avaliacao_{id}_{avaliacao_obj.paciente.nome.replace(" ", "_")}.pdf'

    return response


@relatorios_bp.route('/evolucao/<int:paciente_id>')
@login_required
def evolucao(paciente_id):
    """Relatório de evolução do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)

    # Obter avaliações concluídas ordenadas por data
    avaliacoes = paciente.avaliacoes.filter_by(status='concluida')\
                                     .order_by(Avaliacao.data_avaliacao).all()

    # Gerar gráfico de evolução
    grafico_evolucao = None
    if len(avaliacoes) > 0:
        grafico_evolucao = GraficoService.criar_grafico_evolucao(avaliacoes)

    return render_template('relatorios/evolucao.html',
                          paciente=paciente,
                          avaliacoes=avaliacoes,
                          grafico_evolucao=grafico_evolucao)


@relatorios_bp.route('/pei/<int:avaliacao_id>')
@login_required
def pei(avaliacao_id):
    """Relatório de PEI (Plano Educacional Individualizado)"""
    avaliacao_obj = Avaliacao.query.get_or_404(avaliacao_id)

    # Identificar itens críticos (aqueles com classificação de disfunção)
    itens_criticos = []

    # Organizar respostas por domínio
    dominios_respostas = {}

    for resposta in avaliacao_obj.respostas:
        dominio_codigo = resposta.questao.dominio.codigo
        if dominio_codigo not in dominios_respostas:
            dominios_respostas[dominio_codigo] = {
                'dominio': resposta.questao.dominio,
                'respostas': []
            }

        # Considerar crítico se resposta for "SEMPRE" ou "FREQUENTE"
        # (dependendo da escala)
        is_critico = False
        if resposta.questao.dominio.escala_invertida:
            # Escala invertida: SEMPRE e FREQUENTE são problemáticos
            is_critico = resposta.valor in ['SEMPRE', 'FREQUENTE']
        else:
            # Escala normal: SEMPRE é problemático
            is_critico = resposta.valor == 'SEMPRE'

        dominios_respostas[dominio_codigo]['respostas'].append({
            'questao': resposta.questao,
            'valor': resposta.valor,
            'critico': is_critico
        })

        if is_critico:
            itens_criticos.append({
                'dominio': resposta.questao.dominio.nome,
                'questao': resposta.questao.texto,
                'valor': resposta.valor
            })

    return render_template('relatorios/pei.html',
                          avaliacao=avaliacao_obj,
                          dominios_respostas=dominios_respostas,
                          itens_criticos=itens_criticos)


@relatorios_bp.route('/comparativo/<int:paciente_id>')
@login_required
def comparativo(paciente_id):
    """Relatório comparativo entre casa e escola"""
    paciente = Paciente.query.get_or_404(paciente_id)

    # Obter última avaliação de casa e escola
    avaliacao_casa = paciente.avaliacoes.join(Avaliacao.instrumento)\
                                        .filter(Avaliacao.status == 'concluida')\
                                        .filter(Instrumento.contexto == 'casa')\
                                        .order_by(Avaliacao.data_avaliacao.desc())\
                                        .first()

    avaliacao_escola = paciente.avaliacoes.join(Avaliacao.instrumento)\
                                          .filter(Avaliacao.status == 'concluida')\
                                          .filter(Instrumento.contexto == 'escola')\
                                          .order_by(Avaliacao.data_avaliacao.desc())\
                                          .first()

    # Preparar dados comparativos
    comparacao = {}
    if avaliacao_casa and avaliacao_escola:
        dominios = ['soc', 'vis', 'hea', 'tou', 'bod', 'bal', 'pla']
        if avaliacao_casa.escore_olf:
            dominios.append('olf')

        for dom in dominios:
            escore_casa = getattr(avaliacao_casa, f'escore_{dom}')
            escore_escola = getattr(avaliacao_escola, f'escore_{dom}')

            if escore_casa is not None and escore_escola is not None:
                comparacao[dom] = {
                    'casa': escore_casa,
                    'escola': escore_escola,
                    'diferenca': abs(escore_casa - escore_escola)
                }

    return render_template('relatorios/comparativo.html',
                          paciente=paciente,
                          avaliacao_casa=avaliacao_casa,
                          avaliacao_escola=avaliacao_escola,
                          comparacao=comparacao)
