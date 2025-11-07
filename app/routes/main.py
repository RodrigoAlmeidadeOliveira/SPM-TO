"""
Blueprint principal
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService
from app.models.user import User
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard analítico com métricas e KPIs"""
    # Filtros
    periodo = request.args.get('periodo', '30')  # dias
    avaliador_id = request.args.get('avaliador_id', type=int)

    # Calcular datas baseado no período
    if periodo == 'tudo':
        data_inicio = None
        data_fim = None
    else:
        dias = int(periodo)
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=dias)

    # Obter KPIs
    kpis = DashboardService.obter_kpis(
        data_inicio=data_inicio,
        data_fim=data_fim,
        avaliador_id=avaliador_id
    )

    # Gráficos
    grafico_mes = DashboardService.grafico_avaliacoes_por_mes(
        meses=12 if periodo == 'tudo' else min(12, int(periodo)//30 + 1),
        avaliador_id=avaliador_id
    )

    grafico_classificacao = DashboardService.grafico_distribuicao_classificacao(
        data_inicio=data_inicio,
        data_fim=data_fim,
        avaliador_id=avaliador_id
    )

    grafico_dominios = DashboardService.grafico_dominios_afetados(
        data_inicio=data_inicio,
        data_fim=data_fim,
        avaliador_id=avaliador_id
    )

    grafico_heatmap = DashboardService.grafico_heatmap_dominios(
        data_inicio=data_inicio,
        data_fim=data_fim,
        avaliador_id=avaliador_id
    )

    # Rankings e listas
    ranking_terapeutas = DashboardService.ranking_terapeutas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite=5
    )

    avaliacoes_pendentes = DashboardService.avaliacoes_pendentes(limite=10)

    evolucoes_destaque = DashboardService.evolucao_pacientes_destaque(limite=5)

    # Lista de avaliadores para filtro
    avaliadores = User.query.filter_by(ativo=True).order_by(User.nome_completo).all()

    return render_template('dashboard.html',
                         kpis=kpis,
                         grafico_mes=grafico_mes,
                         grafico_classificacao=grafico_classificacao,
                         grafico_dominios=grafico_dominios,
                         grafico_heatmap=grafico_heatmap,
                         ranking_terapeutas=ranking_terapeutas,
                         avaliacoes_pendentes=avaliacoes_pendentes,
                         evolucoes_destaque=evolucoes_destaque,
                         avaliadores=avaliadores,
                         periodo=periodo,
                         avaliador_id=avaliador_id)
