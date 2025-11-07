"""
Service para cálculo de escores dos novos módulos (PEDI, Cognitiva, AVD)
"""
from app.models import Avaliacao, Resposta, Dominio, Questao


class ModulosService:
    """Service para processar avaliações dos módulos PEDI, Cognitiva e AVD"""

    # Mapeamento de respostas para pontos
    ESCALA_PEDI = {
        'NUNCA': 0,           # Incapaz
        'OCASIONAL': 1,       # Com ajuda máxima
        'FREQUENTE': 2,       # Com ajuda moderada
        'SEMPRE': 3           # Independente
    }

    ESCALA_COGNITIVA = {
        'NUNCA': 0,           # Nunca consegue
        'OCASIONAL': 1,       # Raramente consegue
        'FREQUENTE': 2,       # Frequentemente consegue
        'SEMPRE': 3           # Sempre consegue
    }

    ESCALA_AVD = {
        'NUNCA': 0,           # Dependente total
        'OCASIONAL': 1,       # Necessita assistência
        'FREQUENTE': 2,       # Independente com adaptações
        'SEMPRE': 3           # Totalmente independente
    }

    @staticmethod
    def calcular_escores_pedi(avaliacao_id):
        """
        Calcula escores do PEDI

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores por domínio e total
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao:
            return None

        # Verificar se é PEDI
        if not avaliacao.instrumento.codigo.startswith('PEDI'):
            return None

        escores = {}
        total_geral = 0
        total_maximo = 0

        # Calcular por domínio
        for dominio in avaliacao.instrumento.dominios:
            escore_dominio = 0
            questoes_dominio = dominio.questoes.all()

            for questao in questoes_dominio:
                resposta = Resposta.query.filter_by(
                    avaliacao_id=avaliacao_id,
                    questao_id=questao.id
                ).first()

                if resposta:
                    pontos = ModulosService.ESCALA_PEDI.get(resposta.valor, 0)
                    escore_dominio += pontos

            # Calcular porcentagem de independência
            max_possivel = len(questoes_dominio) * 3  # 3 = máximo (SEMPRE/Independente)
            porcentagem = (escore_dominio / max_possivel * 100) if max_possivel > 0 else 0

            escores[dominio.codigo] = {
                'escore_bruto': escore_dominio,
                'escore_maximo': max_possivel,
                'porcentagem': round(porcentagem, 1),
                'classificacao': ModulosService._classificar_pedi(porcentagem)
            }

            total_geral += escore_dominio
            total_maximo += max_possivel

        # Escore total
        porcentagem_total = (total_geral / total_maximo * 100) if total_maximo > 0 else 0
        escores['TOTAL'] = {
            'escore_bruto': total_geral,
            'escore_maximo': total_maximo,
            'porcentagem': round(porcentagem_total, 1),
            'classificacao': ModulosService._classificar_pedi(porcentagem_total)
        }

        return escores

    @staticmethod
    def calcular_escores_cognitiva(avaliacao_id):
        """
        Calcula escores da Avaliação Cognitiva

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores por domínio cognitivo
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('COG'):
            return None

        escores = {}
        total_geral = 0
        total_maximo = 0

        for dominio in avaliacao.instrumento.dominios:
            escore_dominio = 0
            questoes_dominio = dominio.questoes.all()

            for questao in questoes_dominio:
                resposta = Resposta.query.filter_by(
                    avaliacao_id=avaliacao_id,
                    questao_id=questao.id
                ).first()

                if resposta:
                    pontos = ModulosService.ESCALA_COGNITIVA.get(resposta.valor, 0)
                    escore_dominio += pontos

            max_possivel = len(questoes_dominio) * 3
            porcentagem = (escore_dominio / max_possivel * 100) if max_possivel > 0 else 0

            escores[dominio.codigo] = {
                'escore_bruto': escore_dominio,
                'escore_maximo': max_possivel,
                'porcentagem': round(porcentagem, 1),
                'classificacao': ModulosService._classificar_cognitiva(porcentagem)
            }

            total_geral += escore_dominio
            total_maximo += max_possivel

        porcentagem_total = (total_geral / total_maximo * 100) if total_maximo > 0 else 0
        escores['TOTAL'] = {
            'escore_bruto': total_geral,
            'escore_maximo': total_maximo,
            'porcentagem': round(porcentagem_total, 1),
            'classificacao': ModulosService._classificar_cognitiva(porcentagem_total)
        }

        return escores

    @staticmethod
    def calcular_escores_avd(avaliacao_id):
        """
        Calcula escores de AVD (Atividades de Vida Diária)

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Níveis de independência por área
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('AVD'):
            return None

        escores = {}
        total_geral = 0
        total_maximo = 0

        for dominio in avaliacao.instrumento.dominios:
            escore_dominio = 0
            questoes_dominio = dominio.questoes.all()

            for questao in questoes_dominio:
                resposta = Resposta.query.filter_by(
                    avaliacao_id=avaliacao_id,
                    questao_id=questao.id
                ).first()

                if resposta:
                    pontos = ModulosService.ESCALA_AVD.get(resposta.valor, 0)
                    escore_dominio += pontos

            max_possivel = len(questoes_dominio) * 3
            porcentagem = (escore_dominio / max_possivel * 100) if max_possivel > 0 else 0

            escores[dominio.codigo] = {
                'escore_bruto': escore_dominio,
                'escore_maximo': max_possivel,
                'porcentagem': round(porcentagem, 1),
                'nivel_independencia': ModulosService._classificar_avd(escore_dominio, max_possivel)
            }

            total_geral += escore_dominio
            total_maximo += max_possivel

        porcentagem_total = (total_geral / total_maximo * 100) if total_maximo > 0 else 0
        escores['TOTAL'] = {
            'escore_bruto': total_geral,
            'escore_maximo': total_maximo,
            'porcentagem': round(porcentagem_total, 1),
            'nivel_independencia': ModulosService._classificar_avd(total_geral, total_maximo)
        }

        return escores

    @staticmethod
    def _classificar_pedi(porcentagem):
        """
        Classifica nível funcional do PEDI

        Args:
            porcentagem: Porcentagem de independência (0-100)

        Returns:
            str: Classificação funcional
        """
        if porcentagem >= 80:
            return 'FUNCIONAL'
        elif porcentagem >= 60:
            return 'MODERADAMENTE_FUNCIONAL'
        elif porcentagem >= 40:
            return 'DEPENDENCIA_MODERADA'
        elif porcentagem >= 20:
            return 'DEPENDENCIA_SEVERA'
        else:
            return 'DEPENDENCIA_TOTAL'

    @staticmethod
    def _classificar_cognitiva(porcentagem):
        """
        Classifica desempenho cognitivo

        Args:
            porcentagem: Porcentagem de acertos (0-100)

        Returns:
            str: Classificação cognitiva
        """
        if porcentagem >= 90:
            return 'SUPERIOR'
        elif porcentagem >= 75:
            return 'ADEQUADO'
        elif porcentagem >= 50:
            return 'ABAIXO_DA_MEDIA'
        elif porcentagem >= 25:
            return 'SIGNIFICATIVAMENTE_ABAIXO'
        else:
            return 'DEFICITARIO'

    @staticmethod
    def _classificar_avd(escore, maximo):
        """
        Classifica nível de independência em AVD

        Args:
            escore: Escore obtido
            maximo: Escore máximo possível

        Returns:
            dict: Nível e descrição de independência
        """
        porcentagem = (escore / maximo * 100) if maximo > 0 else 0
        media_por_questao = escore / (maximo / 3) if maximo > 0 else 0

        if media_por_questao >= 2.5:  # Média próxima de 3 (independente)
            return {
                'nivel': 'INDEPENDENTE',
                'descricao': 'Realiza atividades de forma independente',
                'cor': 'success'
            }
        elif media_por_questao >= 1.5:  # Média entre 1.5 e 2.5
            return {
                'nivel': 'INDEPENDENCIA_MODIFICADA',
                'descricao': 'Independente com adaptações ou dispositivos',
                'cor': 'info'
            }
        elif media_por_questao >= 0.5:  # Média entre 0.5 e 1.5
            return {
                'nivel': 'DEPENDENCIA_PARCIAL',
                'descricao': 'Requer assistência em algumas atividades',
                'cor': 'warning'
            }
        else:  # Média abaixo de 0.5
            return {
                'nivel': 'DEPENDENCIA_TOTAL',
                'descricao': 'Requer assistência em quase todas atividades',
                'cor': 'danger'
            }

    @staticmethod
    def gerar_relatorio_pedi(avaliacao_id):
        """
        Gera relatório interpretativo do PEDI

        Returns:
            dict: Relatório com interpretações
        """
        escores = ModulosService.calcular_escores_pedi(avaliacao_id)
        if not escores:
            return None

        relatorio = {
            'titulo': 'Relatório PEDI - Avaliação de Incapacidade Funcional',
            'escores': escores,
            'interpretacao': []
        }

        # Interpretação por domínio
        dominios_nomes = {
            'AUTO': 'Autocuidado',
            'MOB': 'Mobilidade',
            'SOC': 'Função Social'
        }

        for codigo, nome in dominios_nomes.items():
            if codigo in escores:
                escore_dom = escores[codigo]
                relatorio['interpretacao'].append({
                    'dominio': nome,
                    'porcentagem': escore_dom['porcentagem'],
                    'classificacao': escore_dom['classificacao'],
                    'descricao': ModulosService._interpretar_pedi_dominio(
                        nome, escore_dom['classificacao']
                    )
                })

        return relatorio

    @staticmethod
    def _interpretar_pedi_dominio(dominio, classificacao):
        """Gera texto interpretativo para domínio do PEDI"""
        interpretacoes = {
            'FUNCIONAL': f'A criança demonstra bom desempenho funcional em {dominio}, realizando a maioria das atividades de forma independente.',
            'MODERADAMENTE_FUNCIONAL': f'A criança apresenta desempenho funcional moderado em {dominio}, necessitando de assistência ocasional.',
            'DEPENDENCIA_MODERADA': f'A criança apresenta dependência moderada em {dominio}, necessitando de suporte frequente para realizar as atividades.',
            'DEPENDENCIA_SEVERA': f'A criança apresenta dependência severa em {dominio}, requerendo assistência substancial nas atividades.',
            'DEPENDENCIA_TOTAL': f'A criança apresenta dependência total em {dominio}, necessitando de assistência máxima para realizar as atividades.'
        }
        return interpretacoes.get(classificacao, '')
