"""Serviço de geração de gráficos usando Plotly."""
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class GraficoService:
    """Serviço para geração de gráficos"""

    # Cores para cada domínio
    CORES_DOMINIOS = {
        'SOC': '#3498db',  # Azul
        'VIS': '#9b59b6',  # Roxo
        'HEA': '#e74c3c',  # Vermelho
        'TOU': '#f39c12',  # Laranja
        'BOD': '#1abc9c',  # Verde-água
        'BAL': '#2ecc71',  # Verde
        'PLA': '#34495e',  # Cinza escuro
        'OLF': '#e67e22'   # Laranja escuro
    }

    @staticmethod
    def criar_grafico_evolucao(avaliacoes):
        """
        Cria gráfico de evolução temporal dos escores

        Args:
            avaliacoes: Lista de avaliações do paciente (ordenadas por data)

        Returns:
            str: HTML do gráfico Plotly
        """
        if not avaliacoes:
            return None

        # Preparar dados
        datas = [av.data_avaliacao for av in avaliacoes]
        data_labels = [av.data_avaliacao.strftime('%d/%m/%Y') for av in avaliacoes]

        # Criar figura com subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Escores por Domínio', 'Escore Total'),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3]
        )

        # Adicionar traços para cada domínio
        dominios = [
            ('SOC', 'Participação Social'),
            ('VIS', 'Visão'),
            ('HEA', 'Audição'),
            ('TOU', 'Tato'),
            ('BOD', 'Consciência Corporal'),
            ('BAL', 'Equilíbrio e Movimento'),
            ('PLA', 'Planejamento e Ideação'),
            ('OLF', 'Olfato e Paladar')
        ]

        for codigo, nome in dominios:
            # Obter escores
            escores = []
            for av in avaliacoes:
                escore = getattr(av, f'escore_{codigo.lower()}', None)
                if escore is not None:
                    escores.append(escore)
                else:
                    escores.append(None)

            # Se tem dados, adicionar ao gráfico
            if any(e is not None for e in escores):
                fig.add_trace(
                    go.Scatter(
                        x=data_labels,
                        y=escores,
                        name=nome,
                        mode='lines+markers',
                        line=dict(color=GraficoService.CORES_DOMINIOS.get(codigo, '#000000'), width=2),
                        marker=dict(size=8)
                    ),
                    row=1, col=1
                )

        # Adicionar escore total
        escores_totais = [av.escore_total for av in avaliacoes if av.escore_total]
        if escores_totais:
            fig.add_trace(
                go.Scatter(
                    x=data_labels,
                    y=escores_totais,
                    name='Total',
                    mode='lines+markers',
                    line=dict(color='#e74c3c', width=3),
                    marker=dict(size=10),
                    fill='tozeroy'
                ),
                row=2, col=1
            )

        # Atualizar layout
        fig.update_xaxes(title_text="Data da Avaliação", row=2, col=1)
        fig.update_yaxes(title_text="Escore", row=1, col=1)
        fig.update_yaxes(title_text="Escore Total", row=2, col=1)

        fig.update_layout(
            height=700,
            title_text="Evolução dos Escores SPM",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    @staticmethod
    def _montar_figura_radar(avaliacao):
        """Cria o objeto Figure do gráfico radar."""
        dominios_info = [
            ('SOC', 'Participação Social', avaliacao.escore_soc),
            ('VIS', 'Visão', avaliacao.escore_vis),
            ('HEA', 'Audição', avaliacao.escore_hea),
            ('TOU', 'Tato', avaliacao.escore_tou),
            ('BOD', 'Consciência Corporal', avaliacao.escore_bod),
            ('BAL', 'Equilíbrio e Movimento', avaliacao.escore_bal),
            ('PLA', 'Planejamento e Ideação', avaliacao.escore_pla),
            ('OLF', 'Olfato e Paladar', avaliacao.escore_olf)
        ]

        categorias = []
        valores = []

        for _, nome, escore in dominios_info:
            if escore is not None:
                categorias.append(nome)
                valores.append(escore)

        if not valores:
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name='Escores',
            line=dict(color='#3498db', width=2),
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(valores) + 5]
                )
            ),
            showlegend=False,
            title=f"Perfil Sensorial - {avaliacao.paciente.nome}",
            height=500
        )
        return fig

    @staticmethod
    def _montar_figura_barras(avaliacao):
        """Cria o objeto Figure para o gráfico de barras comparativo."""
        dominios_info = [
            ('Participação Social', avaliacao.escore_soc, avaliacao.classificacao_soc),
            ('Visão', avaliacao.escore_vis, avaliacao.classificacao_vis),
            ('Audição', avaliacao.escore_hea, avaliacao.classificacao_hea),
            ('Tato', avaliacao.escore_tou, avaliacao.classificacao_tou),
            ('Consciência Corporal', avaliacao.escore_bod, avaliacao.classificacao_bod),
            ('Equilíbrio e Movimento', avaliacao.escore_bal, avaliacao.classificacao_bal),
            ('Planejamento e Ideação', avaliacao.escore_pla, avaliacao.classificacao_pla)
        ]

        if avaliacao.escore_olf is not None:
            dominios_info.insert(3, ('Olfato e Paladar', avaliacao.escore_olf, avaliacao.classificacao_olf))

        categorias = []
        valores = []
        cores = []

        for nome, escore, classificacao in dominios_info:
            if escore is not None:
                categorias.append(nome)
                valores.append(escore)
                if classificacao == 'TIPICO':
                    cores.append('#2ecc71')
                elif classificacao == 'PROVAVEL_DISFUNCAO':
                    cores.append('#f39c12')
                elif classificacao == 'DISFUNCAO_DEFINITIVA':
                    cores.append('#e74c3c')
                else:
                    cores.append('#95a5a6')

        if not valores:
            return None

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker=dict(
                color=cores,
                line=dict(color='#2c3e50', width=1)
            ),
            text=valores,
            textposition='outside'
        ))

        fig.update_layout(
            title="Escores por Domínio",
            xaxis_title="Domínios",
            yaxis_title="Escore Bruto",
            height=500,
            showlegend=False,
            margin=dict(l=40, r=40, t=70, b=120)
        )
        return fig

    @staticmethod
    def _gerar_dados_figura(figura, incluir_html=True, incluir_png=True):
        """Converte uma figura plotly em representações reutilizáveis."""
        if figura is None:
            return {}

        dados = {}
        if incluir_html:
            dados['html'] = figura.to_html(full_html=False, include_plotlyjs='cdn')

        if incluir_png:
            png_bytes = figura.to_image(format='png', scale=2)
            dados['png_bytes'] = png_bytes
            dados['png_base64'] = base64.b64encode(png_bytes).decode('utf-8')

        return dados

    @staticmethod
    def obter_grafico_radar(avaliacao, incluir_html=True, incluir_png=True):
        """Retorna diferentes formatos do gráfico radar."""
        figura = GraficoService._montar_figura_radar(avaliacao)
        return GraficoService._gerar_dados_figura(figura, incluir_html, incluir_png)

    @staticmethod
    def obter_grafico_barras(avaliacao, incluir_html=True, incluir_png=True):
        """Retorna diferentes formatos do gráfico de barras comparativo."""
        figura = GraficoService._montar_figura_barras(avaliacao)
        return GraficoService._gerar_dados_figura(figura, incluir_html, incluir_png)

    @staticmethod
    def criar_grafico_radar(avaliacao):
        """Mantém compatibilidade retornando apenas o HTML do gráfico radar."""
        dados = GraficoService.obter_grafico_radar(avaliacao, incluir_html=True, incluir_png=False)
        return dados.get('html')

    @staticmethod
    def criar_grafico_barras_comparativo(avaliacao):
        """Mantém compatibilidade retornando apenas o HTML do gráfico de barras."""
        dados = GraficoService.obter_grafico_barras(avaliacao, incluir_html=True, incluir_png=False)
        return dados.get('html')
