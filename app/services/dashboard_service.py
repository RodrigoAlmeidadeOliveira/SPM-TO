"""
Dashboard Service - Cálculos de métricas e estatísticas
"""
from app.models.avaliacao import Avaliacao
from app.models.paciente import Paciente
from app.models.user import User
from app.models.instrumento import Dominio
from app import db
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class DashboardService:
    """Service para geração de métricas e gráficos do dashboard"""

    @staticmethod
    def obter_kpis(data_inicio=None, data_fim=None, avaliador_id=None):
        """
        Retorna KPIs principais do sistema
        """
        query = Avaliacao.query

        # Aplicar filtros
        if data_inicio:
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio)
        if data_fim:
            query = query.filter(Avaliacao.data_avaliacao <= data_fim)
        if avaliador_id:
            query = query.filter_by(avaliador_id=avaliador_id)

        # Total de avaliações
        total_avaliacoes = query.count()

        # Avaliações concluídas
        concluidas = query.filter_by(status='concluida').count()

        # Avaliações em andamento
        em_andamento = query.filter_by(status='em_andamento').count()

        # Pacientes únicos avaliados
        pacientes_unicos = db.session.query(func.count(func.distinct(Avaliacao.paciente_id)))\
            .filter(Avaliacao.id.in_([a.id for a in query.all()])).scalar()

        # Tempo médio de conclusão (dias entre criação e conclusão)
        avaliacoes_concluidas = query.filter(
            Avaliacao.status == 'concluida',
            Avaliacao.data_conclusao.isnot(None)
        ).all()

        if avaliacoes_concluidas:
            deltas = [(a.data_conclusao.date() - a.data_avaliacao).days
                     for a in avaliacoes_concluidas
                     if a.data_conclusao]
            tempo_medio = sum(deltas) / len(deltas) if deltas else 0
        else:
            tempo_medio = 0

        # Taxa de conclusão
        taxa_conclusao = (concluidas / total_avaliacoes * 100) if total_avaliacoes > 0 else 0

        return {
            'total_avaliacoes': total_avaliacoes,
            'concluidas': concluidas,
            'em_andamento': em_andamento,
            'pacientes_unicos': pacientes_unicos,
            'tempo_medio_dias': round(tempo_medio, 1),
            'taxa_conclusao': round(taxa_conclusao, 1)
        }

    @staticmethod
    def grafico_avaliacoes_por_mes(meses=12, avaliador_id=None):
        """
        Gráfico de linha: avaliações por mês
        """
        data_inicio = datetime.now() - timedelta(days=meses*30)

        query = db.session.query(
            func.date_trunc('month', Avaliacao.data_avaliacao).label('mes'),
            func.count(Avaliacao.id).label('total')
        ).filter(Avaliacao.data_avaliacao >= data_inicio)

        if avaliador_id:
            query = query.filter_by(avaliador_id=avaliador_id)

        resultados = query.group_by('mes').order_by('mes').all()

        if not resultados:
            return None

        meses = [r.mes.strftime('%b/%Y') for r in resultados]
        valores = [r.total for r in resultados]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=meses,
            y=valores,
            mode='lines+markers',
            name='Avaliações',
            line=dict(color='#0d6efd', width=3),
            marker=dict(size=10, color='#0d6efd'),
            fill='tozeroy',
            fillcolor='rgba(13, 110, 253, 0.1)'
        ))

        fig.update_layout(
            title='Avaliações Realizadas por Mês',
            xaxis_title='Mês',
            yaxis_title='Número de Avaliações',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig.to_html(include_plotlyjs=False, div_id='grafico_mes')

    @staticmethod
    def grafico_distribuicao_classificacao(data_inicio=None, data_fim=None, avaliador_id=None):
        """
        Gráfico de pizza: distribuição por classificação
        """
        query = Avaliacao.query.filter_by(status='concluida')

        if data_inicio:
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio)
        if data_fim:
            query = query.filter(Avaliacao.data_avaliacao <= data_fim)
        if avaliador_id:
            query = query.filter_by(avaliador_id=avaliador_id)

        avaliacoes = query.all()

        if not avaliacoes:
            return None

        # Contar classificações do domínio TOT (total)
        classificacoes = defaultdict(int)

        for av in avaliacoes:
            if av.classificacao_tot:
                classificacoes[av.classificacao_tot] += 1

        if not classificacoes:
            return None

        # Mapear nomes
        nomes_map = {
            'TIPICO': 'Típico',
            'PROVAVEL_DISFUNCAO': 'Provável Disfunção',
            'DISFUNCAO_DEFINITIVA': 'Disfunção Definitiva'
        }

        cores_map = {
            'TIPICO': '#198754',  # verde
            'PROVAVEL_DISFUNCAO': '#ffc107',  # amarelo
            'DISFUNCAO_DEFINITIVA': '#dc3545'  # vermelho
        }

        labels = [nomes_map.get(k, k) for k in classificacoes.keys()]
        values = list(classificacoes.values())
        colors = [cores_map.get(k, '#6c757d') for k in classificacoes.keys()]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent',
            textposition='auto'
        )])

        fig.update_layout(
            title='Distribuição por Classificação (Total)',
            template='plotly_white',
            height=400
        )

        return fig.to_html(include_plotlyjs=False, div_id='grafico_classificacao')

    @staticmethod
    def grafico_dominios_afetados(data_inicio=None, data_fim=None, avaliador_id=None):
        """
        Gráfico de barras: domínios mais afetados (com disfunção)
        """
        query = Avaliacao.query.filter_by(status='concluida')

        if data_inicio:
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio)
        if data_fim:
            query = query.filter(Avaliacao.data_avaliacao <= data_fim)
        if avaliador_id:
            query = query.filter_by(avaliador_id=avaliador_id)

        avaliacoes = query.all()

        if not avaliacoes:
            return None

        # Contar disfunções por domínio
        dominios = {
            'SOC': {'nome': 'Participação Social', 'disfuncoes': 0, 'total': 0},
            'VIS': {'nome': 'Visão', 'disfuncoes': 0, 'total': 0},
            'HEA': {'nome': 'Audição', 'disfuncoes': 0, 'total': 0},
            'TOU': {'nome': 'Tato', 'disfuncoes': 0, 'total': 0},
            'BOD': {'nome': 'Consciência Corporal', 'disfuncoes': 0, 'total': 0},
            'BAL': {'nome': 'Equilíbrio', 'disfuncoes': 0, 'total': 0},
            'PLA': {'nome': 'Planejamento', 'disfuncoes': 0, 'total': 0},
            'OLF': {'nome': 'Olfato/Paladar', 'disfuncoes': 0, 'total': 0}
        }

        for av in avaliacoes:
            for codigo, info in dominios.items():
                classificacao = getattr(av, f'classificacao_{codigo.lower()}', None)
                if classificacao:
                    info['total'] += 1
                    if classificacao in ['PROVAVEL_DISFUNCAO', 'DISFUNCAO_DEFINITIVA']:
                        info['disfuncoes'] += 1

        # Calcular percentuais
        dados = []
        for codigo, info in dominios.items():
            if info['total'] > 0:
                percentual = (info['disfuncoes'] / info['total']) * 100
                dados.append({
                    'dominio': info['nome'],
                    'percentual': percentual,
                    'total': info['disfuncoes']
                })

        if not dados:
            return None

        # Ordenar por percentual
        dados.sort(key=lambda x: x['percentual'], reverse=True)

        dominios_nomes = [d['dominio'] for d in dados]
        percentuais = [d['percentual'] for d in dados]
        totais = [d['total'] for d in dados]

        fig = go.Figure(data=[
            go.Bar(
                x=dominios_nomes,
                y=percentuais,
                text=[f"{p:.1f}%<br>({t} casos)" for p, t in zip(percentuais, totais)],
                textposition='auto',
                marker=dict(
                    color=percentuais,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="% Afetado")
                )
            )
        ])

        fig.update_layout(
            title='Domínios Mais Afetados (% com Disfunção)',
            xaxis_title='Domínio',
            yaxis_title='Percentual com Disfunção (%)',
            template='plotly_white',
            height=400,
            xaxis_tickangle=-45
        )

        return fig.to_html(include_plotlyjs=False, div_id='grafico_dominios')

    @staticmethod
    def ranking_terapeutas(data_inicio=None, data_fim=None, limite=5):
        """
        Ranking de terapeutas por número de avaliações
        """
        query = db.session.query(
            User.nome_completo,
            func.count(Avaliacao.id).label('total'),
            func.count(case((Avaliacao.status == 'concluida', 1))).label('concluidas')
        ).join(Avaliacao, User.id == Avaliacao.avaliador_id)

        if data_inicio:
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio)
        if data_fim:
            query = query.filter(Avaliacao.data_avaliacao <= data_fim)

        ranking = query.group_by(User.nome_completo)\
                      .order_by(func.count(Avaliacao.id).desc())\
                      .limit(limite)\
                      .all()

        return [
            {
                'nome': r.nome_completo,
                'total': r.total,
                'concluidas': r.concluidas,
                'taxa': round((r.concluidas / r.total * 100) if r.total > 0 else 0, 1)
            }
            for r in ranking
        ]

    @staticmethod
    def avaliacoes_pendentes(limite=10):
        """
        Lista de avaliações pendentes mais antigas
        """
        avaliacoes = Avaliacao.query.filter_by(status='em_andamento')\
                                   .order_by(Avaliacao.data_avaliacao)\
                                   .limit(limite)\
                                   .all()

        return [
            {
                'id': av.id,
                'paciente': av.paciente.nome,
                'data': av.data_avaliacao,
                'dias': (datetime.now().date() - av.data_avaliacao).days,
                'avaliador': av.avaliador.nome_completo,
                'instrumento': av.instrumento.nome
            }
            for av in avaliacoes
        ]

    @staticmethod
    def grafico_heatmap_dominios(data_inicio=None, data_fim=None, avaliador_id=None):
        """
        Heatmap de classificações por domínio
        """
        query = Avaliacao.query.filter_by(status='concluida')

        if data_inicio:
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio)
        if data_fim:
            query = query.filter(Avaliacao.data_avaliacao <= data_fim)
        if avaliador_id:
            query = query.filter_by(avaliador_id=avaliador_id)

        avaliacoes = query.all()

        if not avaliacoes:
            return None

        dominios_cod = ['SOC', 'VIS', 'HEA', 'TOU', 'BOD', 'BAL', 'PLA', 'OLF']
        dominios_nome = {
            'SOC': 'Participação Social',
            'VIS': 'Visão',
            'HEA': 'Audição',
            'TOU': 'Tato',
            'BOD': 'Consciência Corporal',
            'BAL': 'Equilíbrio',
            'PLA': 'Planejamento',
            'OLF': 'Olfato/Paladar'
        }

        classificacoes_ordem = ['TIPICO', 'PROVAVEL_DISFUNCAO', 'DISFUNCAO_DEFINITIVA']
        classificacoes_nome = {
            'TIPICO': 'Típico',
            'PROVAVEL_DISFUNCAO': 'Provável Disfunção',
            'DISFUNCAO_DEFINITIVA': 'Disfunção Definitiva'
        }

        # Matriz de contagens
        matriz = []
        for classif in classificacoes_ordem:
            linha = []
            for dom_cod in dominios_cod:
                count = sum(1 for av in avaliacoes
                          if getattr(av, f'classificacao_{dom_cod.lower()}', None) == classif)
                linha.append(count)
            matriz.append(linha)

        fig = go.Figure(data=go.Heatmap(
            z=matriz,
            x=[dominios_nome.get(d, d) for d in dominios_cod],
            y=[classificacoes_nome.get(c, c) for c in classificacoes_ordem],
            colorscale='RdYlGn_r',
            text=matriz,
            texttemplate='%{text}',
            textfont={"size": 14},
            colorbar=dict(title="Quantidade")
        ))

        fig.update_layout(
            title='Mapa de Calor: Classificações por Domínio',
            xaxis_title='Domínio',
            yaxis_title='Classificação',
            template='plotly_white',
            height=300,
            xaxis_tickangle=-45
        )

        return fig.to_html(include_plotlyjs=False, div_id='grafico_heatmap')

    @staticmethod
    def evolucao_pacientes_destaque(limite=5):
        """
        Pacientes com melhor evolução (maior aumento no T-score total)
        """
        # Buscar pacientes com pelo menos 2 avaliações concluídas
        pacientes = db.session.query(Paciente)\
            .join(Avaliacao)\
            .filter(Avaliacao.status == 'concluida')\
            .group_by(Paciente.id)\
            .having(func.count(Avaliacao.id) >= 2)\
            .all()

        evolucoes = []

        for paciente in pacientes:
            avaliacoes = sorted(
                [av for av in paciente.avaliacoes if av.status == 'concluida' and av.t_score_tot],
                key=lambda x: x.data_avaliacao
            )

            if len(avaliacoes) >= 2:
                primeira = avaliacoes[0]
                ultima = avaliacoes[-1]

                delta = ultima.t_score_tot - primeira.t_score_tot

                evolucoes.append({
                    'paciente_id': paciente.id,
                    'paciente': paciente.nome,
                    'idade': paciente.calcular_idade()[0],
                    'primeira_data': primeira.data_avaliacao,
                    'ultima_data': ultima.data_avaliacao,
                    't_score_inicial': primeira.t_score_tot,
                    't_score_final': ultima.t_score_tot,
                    'delta': delta,
                    'num_avaliacoes': len(avaliacoes)
                })

        # Ordenar por delta (maiores melhorias primeiro)
        evolucoes.sort(key=lambda x: x['delta'], reverse=True)

        return evolucoes[:limite]
