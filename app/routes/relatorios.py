"""
Blueprint de Relatórios
"""
from collections import OrderedDict
from flask import Blueprint, render_template, Response, make_response, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.avaliacao import Avaliacao
from app.models.instrumento import Instrumento
from app.models.paciente import Paciente
from app.models.plano import PlanoItem, PlanoTemplateItem
from app.services.grafico_service import GraficoService
from app.services.modulos_service import ModulosService
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
    grafico_radar_img = None
    grafico_barras_img = None

    perfil_sensorial_relatorio = None

    if avaliacao_obj.status == 'concluida':
        dados_radar = GraficoService.obter_grafico_radar(avaliacao_obj)
        dados_barras = GraficoService.obter_grafico_barras(avaliacao_obj)

        grafico_radar = dados_radar.get('html')
        grafico_barras = dados_barras.get('html')
        grafico_radar_img = dados_radar.get('png_base64')
        grafico_barras_img = dados_barras.get('png_base64')

        if avaliacao_obj.instrumento and avaliacao_obj.instrumento.codigo.startswith('PERFIL_SENS'):
            perfil_sensorial_relatorio = ModulosService.gerar_relatorio_perfil_sensorial(avaliacao_obj.id)

    scores_spm_table = None
    if avaliacao_obj.status == 'concluida':
        scores_spm_table = ModulosService.criar_scores_spm_casa(avaliacao_obj)

    return render_template('relatorios/avaliacao.html',
                          avaliacao=avaliacao_obj,
                          grafico_radar=grafico_radar,
                          grafico_barras=grafico_barras,
                          grafico_radar_img=grafico_radar_img,
                          grafico_barras_img=grafico_barras_img,
                          perfil_sensorial_relatorio=perfil_sensorial_relatorio,
                          scores_spm_table=scores_spm_table)


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

    plano_selecionado = (
        avaliacao_obj.plano_itens.join(PlanoItem.template_item)
        .order_by(PlanoTemplateItem.ordem)
        .all()
    )

    plano_por_dominio = OrderedDict()
    for item in plano_selecionado:
        if not item.selecionado:
            continue
        nome = item.template_item.dominio_nome
        plano_por_dominio.setdefault(nome, []).append(item.template_item.texto)

    scores_spm_table = ModulosService.criar_scores_spm_casa(avaliacao_obj)

    return render_template('relatorios/pei.html',
                          avaliacao=avaliacao_obj,
                          dominios_respostas=dominios_respostas,
                          itens_criticos=itens_criticos,
                          plano_por_dominio=plano_por_dominio,
                          scores_spm_table=scores_spm_table)


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


@relatorios_bp.route('/pei/<int:avaliacao_id>/plano', methods=['GET', 'POST'])
@login_required
def pei_plano(avaliacao_id):
    """Formulário para seleção de itens de intervenção (PEI)"""
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    template_itens = (
        PlanoTemplateItem.query
        .filter_by(instrumento_id=avaliacao.instrumento_id, ativo=True)
        .order_by(PlanoTemplateItem.ordem)
        .all()
    )

    if not template_itens:
        flash('Não há itens de plano cadastrados para este instrumento.', 'warning')
        return redirect(url_for('relatorios.pei', avaliacao_id=avaliacao.id))

    itens_existentes = {
        item.template_item_id: item
        for item in avaliacao.plano_itens.all()
    }

    if request.method == 'POST':
        selecionados = {int(item_id) for item_id in request.form.getlist('itens')}

        for template_item in template_itens:
            plano_item = itens_existentes.get(template_item.id)
            if plano_item is None:
                plano_item = PlanoItem(
                    avaliacao_id=avaliacao.id,
                    template_item_id=template_item.id
                )
                avaliacao.plano_itens.append(plano_item)
                itens_existentes[template_item.id] = plano_item

            plano_item.selecionado = template_item.id in selecionados

        db.session.commit()
        flash('Plano de intervenção atualizado com sucesso!', 'success')
        return redirect(url_for('relatorios.pei', avaliacao_id=avaliacao.id))

    return render_template(
        'relatorios/pei_plano.html',
        avaliacao=avaliacao,
        template_itens=template_itens,
        itens_existentes=itens_existentes
    )
