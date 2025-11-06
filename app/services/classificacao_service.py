"""
Serviço de Classificação de Resultados
Implementa a lógica de classificação baseada em T-scores e percentis
"""
from app.models.instrumento import TabelaReferencia


class ClassificacaoService:
    """Serviço para classificação de resultados"""

    # Categorias de classificação
    DISFUNCAO_DEFINITIVA = 'DISFUNCAO_DEFINITIVA'
    PROVAVEL_DISFUNCAO = 'PROVAVEL_DISFUNCAO'
    TIPICO = 'TIPICO'

    @staticmethod
    def obter_classificacao(instrumento_id, dominio_codigo, escore_bruto):
        """
        Obtém a classificação e T-score baseado no escore bruto

        Args:
            instrumento_id: ID do instrumento
            dominio_codigo: Código do domínio (SOC, VIS, HEA, etc.)
            escore_bruto: Escore bruto calculado

        Returns:
            dict: {
                't_score': int,
                'percentil': tuple (min, max),
                'classificacao': str
            }
        """
        # Buscar na tabela de referência
        ref = TabelaReferencia.query.filter_by(
            instrumento_id=instrumento_id,
            dominio_codigo=dominio_codigo
        ).filter(
            TabelaReferencia.escore_min <= escore_bruto,
            TabelaReferencia.escore_max >= escore_bruto
        ).first()

        if ref:
            return {
                't_score': ref.t_score,
                'percentil': (ref.percentil_min, ref.percentil_max),
                'classificacao': ref.classificacao,
                'classificacao_texto': ClassificacaoService._get_classificacao_texto(ref.classificacao)
            }

        # Se não encontrar, retornar valores padrão
        return {
            't_score': None,
            'percentil': (None, None),
            'classificacao': None,
            'classificacao_texto': 'Não classificado'
        }

    @staticmethod
    def classificar_avaliacao(avaliacao):
        """
        Classifica todos os domínios de uma avaliação

        Args:
            avaliacao: Instância de Avaliacao

        Returns:
            dict: Classificações por domínio
        """
        from app import db

        classificacoes = {}
        dominios_map = {
            'SOC': avaliacao.escore_soc,
            'VIS': avaliacao.escore_vis,
            'HEA': avaliacao.escore_hea,
            'TOU': avaliacao.escore_tou,
            'BOD': avaliacao.escore_bod,
            'BAL': avaliacao.escore_bal,
            'PLA': avaliacao.escore_pla,
            'OLF': avaliacao.escore_olf
        }

        for dominio_codigo, escore in dominios_map.items():
            if escore is not None:
                classificacao = ClassificacaoService.obter_classificacao(
                    avaliacao.instrumento_id,
                    dominio_codigo,
                    escore
                )
                classificacoes[dominio_codigo] = classificacao

                # Atualizar T-scores e classificações na avaliação
                setattr(avaliacao, f't_score_{dominio_codigo.lower()}',
                       classificacao['t_score'])
                setattr(avaliacao, f'classificacao_{dominio_codigo.lower()}',
                       classificacao['classificacao'])

        db.session.commit()

        return classificacoes

    @staticmethod
    def _get_classificacao_texto(classificacao):
        """
        Retorna o texto descritivo da classificação

        Args:
            classificacao: Código da classificação

        Returns:
            str: Texto descritivo
        """
        textos = {
            ClassificacaoService.DISFUNCAO_DEFINITIVA: 'Disfunção Definitiva',
            ClassificacaoService.PROVAVEL_DISFUNCAO: 'Provável Disfunção',
            ClassificacaoService.TIPICO: 'Típico'
        }
        return textos.get(classificacao, 'Não classificado')

    @staticmethod
    def interpretar_resultado(classificacao):
        """
        Retorna interpretação detalhada do resultado

        Args:
            classificacao: Código da classificação

        Returns:
            str: Interpretação detalhada
        """
        interpretacoes = {
            ClassificacaoService.DISFUNCAO_DEFINITIVA:
                'Os resultados indicam uma disfunção definitiva no processamento sensorial. '
                'É altamente recomendado buscar avaliação e intervenção especializada.',

            ClassificacaoService.PROVAVEL_DISFUNCAO:
                'Os resultados sugerem uma provável disfunção no processamento sensorial. '
                'É recomendado monitoramento próximo e consideração de avaliação especializada.',

            ClassificacaoService.TIPICO:
                'Os resultados estão dentro da faixa típica de processamento sensorial.'
        }
        return interpretacoes.get(classificacao, '')
