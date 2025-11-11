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

    ESCALA_PERFIL_SENSORIAL = {
        'QUASE_NUNCA': 1,        # 10% ou menos
        'OCASIONALMENTE': 2,     # 25%
        'METADE_TEMPO': 3,       # 50%
        'FREQUENTEMENTE': 4,     # 75%
        'QUASE_SEMPRE': 5,       # 90% ou mais
        'NAO_APLICA': 0          # Não se aplica
    }

    # Mapeamento de questões para quadrantes (baseado no PDF página 7)
    QUADRANTES_PERFIL_SENSORIAL = {
        'EXPLORACAO': [14, 21, 22, 25, 27, 28, 30, 31, 32, 41, 48, 49, 50, 51, 55, 56, 60, 82, 83],
        'ESQUIVA': [1, 2, 5, 15, 18, 58, 59, 61, 63, 64, 65, 66, 67, 68, 70, 71, 72, 74, 75, 81],
        'SENSIBILIDADE': [3, 4, 6, 7, 9, 13, 16, 19, 20, 44, 45, 46, 47, 52, 69, 73, 77, 78, 84],
        'OBSERVACAO': [8, 12, 23, 24, 26, 33, 34, 35, 36, 37, 38, 39, 40, 53, 54, 57, 62, 76, 79, 80, 85, 86]
    }

    # Seções sensoriais e suas questões
    SECOES_PERFIL_SENSORIAL = {
        'AUDITIVO': {'questoes': list(range(1, 9)), 'max_pontos': 40},
        'VISUAL': {'questoes': list(range(9, 16)), 'max_pontos': 30},
        'TATO': {'questoes': list(range(16, 27)), 'max_pontos': 55},
        'MOVIMENTOS': {'questoes': list(range(27, 35)), 'max_pontos': 40},
        'POSICAO_CORPO': {'questoes': list(range(35, 43)), 'max_pontos': 40},
        'ORAL': {'questoes': list(range(43, 53)), 'max_pontos': 50},
        'CONDUTA': {'questoes': list(range(53, 62)), 'max_pontos': 45},
        'SOCIOEMOCIONAL': {'questoes': list(range(62, 76)), 'max_pontos': 70},
        'ATENCAO': {'questoes': list(range(76, 87)), 'max_pontos': 50}
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

    @staticmethod
    def calcular_perfil_sensorial(avaliacao_id):
        """
        Calcula escores do Perfil Sensorial 2

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores por seção sensorial e quadrantes
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('PERFIL_SENS'):
            return None

        resultado = {
            'secoes': {},
            'quadrantes': {},
            'respostas_por_numero': {}  # Mapeia número da questão para resposta
        }

        # Primeiro, mapear todas as respostas por número de questão
        for resposta in avaliacao.respostas:
            # Assumindo que o código da questão contém o número (ex: "PS_001", "PS_086")
            numero_questao = int(resposta.questao.codigo.split('_')[-1])
            pontos = ModulosService.ESCALA_PERFIL_SENSORIAL.get(resposta.valor, 0)
            resultado['respostas_por_numero'][numero_questao] = pontos

        # Calcular escores por seção sensorial
        for secao_codigo, secao_info in ModulosService.SECOES_PERFIL_SENSORIAL.items():
            escore_bruto = 0
            questoes_respondidas = 0

            for num_questao in secao_info['questoes']:
                if num_questao in resultado['respostas_por_numero']:
                    pontos = resultado['respostas_por_numero'][num_questao]
                    if pontos > 0:  # Não conta "Não se aplica"
                        escore_bruto += pontos
                        questoes_respondidas += 1

            resultado['secoes'][secao_codigo] = {
                'escore_bruto': escore_bruto,
                'questoes_respondidas': questoes_respondidas,
                'classificacao': ModulosService._classificar_perfil_sensorial_secao(
                    secao_codigo, escore_bruto
                )
            }

        # Calcular escores por quadrante
        for quadrante, questoes in ModulosService.QUADRANTES_PERFIL_SENSORIAL.items():
            escore_bruto = 0
            questoes_respondidas = 0

            for num_questao in questoes:
                if num_questao in resultado['respostas_por_numero']:
                    pontos = resultado['respostas_por_numero'][num_questao]
                    if pontos > 0:
                        escore_bruto += pontos
                        questoes_respondidas += 1

            max_possivel = len(questoes) * 5  # Máximo de 5 pontos por questão

            resultado['quadrantes'][quadrante] = {
                'escore_bruto': escore_bruto,
                'escore_maximo': max_possivel,
                'questoes_respondidas': questoes_respondidas,
                'classificacao': ModulosService._classificar_perfil_sensorial_quadrante(
                    quadrante, escore_bruto, max_possivel
                )
            }

        return resultado

    @staticmethod
    def _classificar_perfil_sensorial_secao(secao, escore):
        """
        Classifica o escore de uma seção sensorial usando tabela de percentis
        Baseado na tabela da página 8 do PDF

        Args:
            secao: Código da seção (AUDITIVO, VISUAL, etc.)
            escore: Escore bruto obtido

        Returns:
            dict: Classificação e interpretação
        """
        # Tabelas de classificação por seção (baseadas no PDF página 8)
        tabelas = {
            'AUDITIVO': {
                'MUITO_MENOS': (0, 2),
                'MENOS': (3, 9),
                'TIPICO': (10, 24),
                'MAIS': (25, 31),
                'MUITO_MAIS': (32, 40)
            },
            'VISUAL': {
                'MUITO_MENOS': (0, 4),
                'MENOS': (5, 8),
                'TIPICO': (9, 17),
                'MAIS': (18, 21),
                'MUITO_MAIS': (22, 30)
            },
            'TATO': {
                'MUITO_MENOS': (0, 0),
                'MENOS': (1, 7),
                'TIPICO': (8, 21),
                'MAIS': (22, 28),
                'MUITO_MAIS': (29, 55)
            },
            'MOVIMENTOS': {
                'MUITO_MENOS': (0, 1),
                'MENOS': (2, 6),
                'TIPICO': (7, 18),
                'MAIS': (19, 24),
                'MUITO_MAIS': (25, 40)
            },
            'POSICAO_CORPO': {
                'MUITO_MENOS': (0, 0),
                'MENOS': (1, 4),
                'TIPICO': (5, 15),
                'MAIS': (16, 19),
                'MUITO_MAIS': (20, 40)
            },
            'ORAL': {
                'MUITO_MENOS': (0, 0),
                'MENOS': (0, 7),
                'TIPICO': (8, 24),
                'MAIS': (25, 32),
                'MUITO_MAIS': (33, 50)
            },
            'CONDUTA': {
                'MUITO_MENOS': (0, 1),
                'MENOS': (2, 8),
                'TIPICO': (9, 22),
                'MAIS': (23, 29),
                'MUITO_MAIS': (30, 45)
            },
            'SOCIOEMOCIONAL': {
                'MUITO_MENOS': (0, 2),
                'MENOS': (3, 12),
                'TIPICO': (13, 31),
                'MAIS': (32, 41),
                'MUITO_MAIS': (42, 70)
            },
            'ATENCAO': {
                'MUITO_MENOS': (0, 0),
                'MENOS': (1, 8),
                'TIPICO': (9, 24),
                'MAIS': (25, 31),
                'MUITO_MAIS': (32, 50)
            }
        }

        if secao not in tabelas:
            return {'nivel': 'NAO_CLASSIFICADO', 'descricao': 'Seção não encontrada'}

        tabela = tabelas[secao]

        for nivel, (min_val, max_val) in tabela.items():
            if min_val <= escore <= max_val:
                descricoes = {
                    'MUITO_MENOS': 'Muito menos que outros(as) - Busca muito menos estímulos sensoriais',
                    'MENOS': 'Menos que outros(as) - Busca menos estímulos sensoriais',
                    'TIPICO': 'Exatamente como a maioria - Padrão típico de processamento',
                    'MAIS': 'Mais que outros(as) - Busca mais estímulos sensoriais',
                    'MUITO_MAIS': 'Muito mais que outros(as) - Busca muito mais estímulos sensoriais'
                }

                return {
                    'nivel': nivel,
                    'descricao': descricoes.get(nivel, ''),
                    'escore': escore
                }

        return {'nivel': 'NAO_CLASSIFICADO', 'descricao': 'Escore fora dos limites', 'escore': escore}

    @staticmethod
    def _classificar_perfil_sensorial_quadrante(quadrante, escore, maximo):
        """
        Classifica o padrão de processamento sensorial por quadrante

        Args:
            quadrante: Nome do quadrante (EXPLORACAO, ESQUIVA, etc.)
            escore: Escore bruto
            maximo: Escore máximo possível

        Returns:
            dict: Classificação do padrão
        """
        # Tabelas de percentis por quadrante (baseado na página 8 do PDF)
        tabelas_quadrantes = {
            'EXPLORACAO': {
                'max': 95,
                'MUITO_MENOS': (0, 6),
                'MENOS': (7, 19),
                'TIPICO': (20, 47),
                'MAIS': (48, 60),
                'MUITO_MAIS': (61, 95)
            },
            'ESQUIVA': {
                'max': 100,
                'MUITO_MENOS': (0, 7),
                'MENOS': (8, 20),
                'TIPICO': (21, 46),
                'MAIS': (47, 59),
                'MUITO_MAIS': (60, 100)
            },
            'SENSIBILIDADE': {
                'max': 95,
                'MUITO_MENOS': (0, 6),
                'MENOS': (7, 17),
                'TIPICO': (18, 42),
                'MAIS': (43, 53),
                'MUITO_MAIS': (54, 95)
            },
            'OBSERVACAO': {
                'max': 110,
                'MUITO_MENOS': (0, 6),
                'MENOS': (7, 18),
                'TIPICO': (19, 43),
                'MAIS': (44, 55),
                'MUITO_MAIS': (56, 110)
            }
        }

        if quadrante not in tabelas_quadrantes:
            return {'nivel': 'NAO_CLASSIFICADO', 'descricao': 'Quadrante não encontrado'}

        tabela = tabelas_quadrantes[quadrante]

        for nivel, limites in tabela.items():
            if nivel == 'max':
                continue
            min_val, max_val = limites
            if min_val <= escore <= max_val:
                descricoes_quadrante = {
                    'EXPLORACAO': {
                        'titulo': 'Exploração/Criança exploradora',
                        'descricao': 'obtém estímulo sensorial - busca estímulos sensoriais em uma taxa elevada',
                        'cor': 'warning'
                    },
                    'ESQUIVA': {
                        'titulo': 'Esquiva/Criança que se esquiva',
                        'descricao': 'fica incomodada por estímulos sensoriais - se afasta de estímulos sensoriais em uma taxa mais elevada',
                        'cor': 'primary'
                    },
                    'SENSIBILIDADE': {
                        'titulo': 'Sensibilidade/Criança sensível',
                        'descricao': 'detecta estímulos sensoriais - percebe estímulos sensoriais em uma taxa mais elevada',
                        'cor': 'success'
                    },
                    'OBSERVACAO': {
                        'titulo': 'Observação/Criança observadora',
                        'descricao': 'não percebe estímulos sensoriais - não percebe estímulos sensoriais em uma taxa mais elevada',
                        'cor': 'secondary'
                    }
                }

                interpretacoes_nivel = {
                    'MUITO_MENOS': 'Muito menos que outros(as)',
                    'MENOS': 'Menos que outros(as)',
                    'TIPICO': 'Exatamente como a maioria dos(as) outros(as)',
                    'MAIS': 'Mais que outros(as)',
                    'MUITO_MAIS': 'Muito mais que outros(as)'
                }

                return {
                    'nivel': nivel,
                    'nivel_descricao': interpretacoes_nivel.get(nivel, ''),
                    'quadrante_info': descricoes_quadrante.get(quadrante, {}),
                    'escore': escore,
                    'escore_maximo': tabela['max']
                }

        return {'nivel': 'NAO_CLASSIFICADO', 'descricao': 'Escore fora dos limites'}

    @staticmethod
    def gerar_relatorio_perfil_sensorial(avaliacao_id):
        """
        Gera relatório interpretativo do Perfil Sensorial 2

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Relatório completo com interpretações
        """
        resultado = ModulosService.calcular_perfil_sensorial(avaliacao_id)
        if not resultado:
            return None

        relatorio = {
            'titulo': 'Relatório Perfil Sensorial 2 - Criança (3-14 anos)',
            'secoes': [],
            'quadrantes': [],
            'interpretacao_geral': ''
        }

        # Interpretação por seção sensorial
        nomes_secoes = {
            'AUDITIVO': 'Processamento Auditivo',
            'VISUAL': 'Processamento Visual',
            'TATO': 'Processamento do Tato',
            'MOVIMENTOS': 'Processamento de Movimentos',
            'POSICAO_CORPO': 'Processamento da Posição do Corpo',
            'ORAL': 'Processamento de Sensibilidade Oral',
            'CONDUTA': 'Conduta associada ao processamento sensorial',
            'SOCIOEMOCIONAL': 'Respostas Socioemocionais',
            'ATENCAO': 'Respostas de Atenção'
        }

        for codigo, nome in nomes_secoes.items():
            if codigo in resultado['secoes']:
                secao_data = resultado['secoes'][codigo]
                relatorio['secoes'].append({
                    'codigo': codigo,
                    'nome': nome,
                    'escore': secao_data['escore_bruto'],
                    'classificacao': secao_data['classificacao']
                })

        # Interpretação por quadrante
        for quadrante, dados in resultado['quadrantes'].items():
            if 'classificacao' in dados and 'quadrante_info' in dados['classificacao']:
                relatorio['quadrantes'].append({
                    'quadrante': quadrante,
                    'dados': dados
                })

        # Interpretação geral
        relatorio['interpretacao_geral'] = ModulosService._interpretar_perfil_sensorial_geral(
            resultado['quadrantes']
        )

        return relatorio

    @staticmethod
    def _interpretar_perfil_sensorial_geral(quadrantes):
        """
        Gera interpretação geral baseada nos padrões dos quadrantes

        Args:
            quadrantes: Dict com escores dos quadrantes

        Returns:
            str: Texto interpretativo geral
        """
        interpretacao = []

        # Identificar quadrantes predominantes (escore alto)
        quadrantes_altos = []
        quadrantes_baixos = []

        for quadrante, dados in quadrantes.items():
            if 'classificacao' in dados:
                nivel = dados['classificacao'].get('nivel', '')
                if nivel in ['MAIS', 'MUITO_MAIS']:
                    quadrantes_altos.append(quadrante)
                elif nivel in ['MENOS', 'MUITO_MENOS']:
                    quadrantes_baixos.append(quadrante)

        if 'EXPLORACAO' in quadrantes_altos:
            interpretacao.append(
                "A criança demonstra um padrão de BUSCA SENSORIAL elevado, procurando ativamente "
                "por experiências sensoriais no ambiente."
            )

        if 'ESQUIVA' in quadrantes_altos:
            interpretacao.append(
                "A criança apresenta padrão de ESQUIVA SENSORIAL, evitando ou se afastando de "
                "certos estímulos sensoriais que podem ser desconfortáveis."
            )

        if 'SENSIBILIDADE' in quadrantes_altos:
            interpretacao.append(
                "A criança demonstra SENSIBILIDADE SENSORIAL aumentada, percebendo estímulos "
                "que outras crianças da mesma idade podem não notar."
            )

        if 'OBSERVACAO' in quadrantes_altos:
            interpretacao.append(
                "A criança apresenta padrão de BAIXO REGISTRO SENSORIAL, podendo não perceber "
                "ou responder a estímulos sensoriais do ambiente."
            )

        if not interpretacao:
            interpretacao.append(
                "A criança apresenta padrões de processamento sensorial dentro da faixa típica "
                "para a maioria dos quadrantes avaliados."
            )

        return " ".join(interpretacao)

    # ==================== NOVOS MÓDULOS ====================

    @staticmethod
    def calcular_escores_copm(avaliacao_id):
        """
        Calcula escores do COPM

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores de desempenho e satisfação, mudança clínica
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('COPM'):
            return None

        escores = {
            'problemas': [],
            'desempenho_medio': 0,
            'satisfacao_media': 0
        }

        # Identificar até 5 problemas e seus escores
        for i in range(1, 6):
            # Buscar respostas de desempenho e satisfação para cada problema
            resp_desemp = Resposta.query.join(Questao).filter(
                Resposta.avaliacao_id == avaliacao_id,
                Questao.codigo == f'COPM_DESEMP_{i}'
            ).first()

            resp_satis = Resposta.query.join(Questao).filter(
                Resposta.avaliacao_id == avaliacao_id,
                Questao.codigo == f'COPM_SATIS_{i}'
            ).first()

            if resp_desemp and resp_satis:
                try:
                    desemp_valor = int(resp_desemp.valor)
                    satis_valor = int(resp_satis.valor)

                    escores['problemas'].append({
                        'numero': i,
                        'desempenho': desemp_valor,
                        'satisfacao': satis_valor
                    })
                except (ValueError, TypeError):
                    continue

        # Calcular médias
        if escores['problemas']:
            escores['desempenho_medio'] = sum(p['desempenho'] for p in escores['problemas']) / len(escores['problemas'])
            escores['satisfacao_media'] = sum(p['satisfacao'] for p in escores['problemas']) / len(escores['problemas'])

        return escores

    @staticmethod
    def calcular_escores_abc(avaliacao_id):
        """
        Calcula escores da ABC Scale

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escore total e classificação de risco
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('ABC'):
            return None

        total = 0
        count = 0

        for resposta in avaliacao.respostas:
            try:
                # Valor é a porcentagem de confiança (0-100)
                valor = int(resposta.valor)
                total += valor
                count += 1
            except (ValueError, TypeError):
                continue

        media = (total / count) if count > 0 else 0

        # Classificação de risco de queda
        if media > 80:
            risco = 'BAIXO'
            descricao = 'Alta confiança no equilíbrio - Baixo risco de queda'
        elif media >= 50:
            risco = 'MODERADO'
            descricao = 'Confiança moderada - Risco moderado de queda'
        else:
            risco = 'ALTO'
            descricao = 'Baixa confiança - Alto risco de queda'

        return {
            'escore_total': round(media, 1),
            'itens_respondidos': count,
            'risco_queda': risco,
            'descricao': descricao
        }

    ESCALA_FIM = {
        '1': 1,  # Ajuda total
        '2': 2,  # Ajuda máxima
        '3': 3,  # Ajuda moderada
        '4': 4,  # Ajuda mínima
        '5': 5,  # Supervisão
        '6': 6,  # Independência modificada
        '7': 7   # Independência completa
    }

    @staticmethod
    def calcular_escores_fim(avaliacao_id):
        """
        Calcula escores do FIM

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores motor, cognitivo e total
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('FIM'):
            return None

        escore_motor = 0
        escore_cognitivo = 0

        for resposta in avaliacao.respostas:
            # Verificar metadados da questão para categoria
            categoria = resposta.questao.metadados.get('categoria', 'MOTOR') if resposta.questao.metadados else 'MOTOR'
            pontos = ModulosService.ESCALA_FIM.get(resposta.valor, 0)

            if categoria == 'MOTOR':
                escore_motor += pontos
            else:
                escore_cognitivo += pontos

        escore_total = escore_motor + escore_cognitivo

        return {
            'motor': {
                'escore': escore_motor,
                'maximo': 91,
                'nivel': ModulosService._classificar_fim(escore_motor, 91)
            },
            'cognitivo': {
                'escore': escore_cognitivo,
                'maximo': 35,
                'nivel': ModulosService._classificar_fim(escore_cognitivo, 35)
            },
            'total': {
                'escore': escore_total,
                'maximo': 126,
                'nivel': ModulosService._classificar_fim(escore_total, 126)
            }
        }

    @staticmethod
    def calcular_escores_weefim(avaliacao_id):
        """
        Calcula escores do WeeFIM (estrutura idêntica ao FIM)

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores motor, cognitivo e total
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('WEEFIM'):
            return None

        # Usar mesma lógica do FIM
        escore_motor = 0
        escore_cognitivo = 0

        for resposta in avaliacao.respostas:
            categoria = resposta.questao.metadados.get('categoria', 'MOTOR') if resposta.questao.metadados else 'MOTOR'
            pontos = ModulosService.ESCALA_FIM.get(resposta.valor, 0)

            if categoria == 'MOTOR':
                escore_motor += pontos
            else:
                escore_cognitivo += pontos

        escore_total = escore_motor + escore_cognitivo

        return {
            'motor': {
                'escore': escore_motor,
                'maximo': 91,
                'nivel': ModulosService._classificar_fim(escore_motor, 91)
            },
            'cognitivo': {
                'escore': escore_cognitivo,
                'maximo': 35,
                'nivel': ModulosService._classificar_fim(escore_cognitivo, 35)
            },
            'total': {
                'escore': escore_total,
                'maximo': 126,
                'nivel': ModulosService._classificar_fim(escore_total, 126)
            }
        }

    ESCALA_GMFM = {
        '0': 0,  # Não inicia
        '1': 1,  # Inicia
        '2': 2,  # Completa parcialmente
        '3': 3   # Completa
    }

    @staticmethod
    def calcular_escores_gmfm(avaliacao_id):
        """
        Calcula escores do GMFM-88

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            dict: Escores por dimensão e total
        """
        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao or not avaliacao.instrumento.codigo.startswith('GMFM'):
            return None

        escores = {}
        total_geral = 0
        num_dimensoes = 0

        # Calcular por dimensão
        for dominio in avaliacao.instrumento.dominios:
            escore_dimensao = 0
            questoes_dimensao = dominio.questoes.all()

            for questao in questoes_dimensao:
                resposta = Resposta.query.filter_by(
                    avaliacao_id=avaliacao_id,
                    questao_id=questao.id
                ).first()

                if resposta:
                    pontos = ModulosService.ESCALA_GMFM.get(resposta.valor, 0)
                    escore_dimensao += pontos

            # Calcular porcentagem para a dimensão
            max_possivel = len(questoes_dimensao) * 3
            porcentagem = (escore_dimensao / max_possivel * 100) if max_possivel > 0 else 0

            escores[dominio.codigo] = {
                'nome': dominio.nome,
                'escore_bruto': escore_dimensao,
                'escore_maximo': max_possivel,
                'porcentagem': round(porcentagem, 1),
                'itens': len(questoes_dimensao)
            }

            total_geral += porcentagem
            num_dimensoes += 1

        # Escore total GMFM = média das 5 dimensões
        gmfm_total = (total_geral / num_dimensoes) if num_dimensoes > 0 else 0

        escores['TOTAL'] = {
            'escore_gmfm': round(gmfm_total, 1),
            'interpretacao': ModulosService._classificar_gmfm(gmfm_total)
        }

        return escores

    @staticmethod
    def _classificar_fim(escore, maximo):
        """
        Classifica nível de independência no FIM/WeeFIM

        Args:
            escore: Escore obtido
            maximo: Escore máximo possível

        Returns:
            dict: Classificação
        """
        porcentagem = (escore / maximo * 100) if maximo > 0 else 0

        if escore == maximo:
            return {
                'nivel': 'INDEPENDENCIA_COMPLETA',
                'descricao': 'Independência completa em todas as atividades',
                'cor': 'success'
            }
        elif porcentagem >= 80:
            return {
                'nivel': 'INDEPENDENCIA_MODIFICADA',
                'descricao': 'Independente com modificações ou ajudas técnicas',
                'cor': 'info'
            }
        elif porcentagem >= 50:
            return {
                'nivel': 'DEPENDENCIA_MODERADA',
                'descricao': 'Necessita assistência moderada',
                'cor': 'warning'
            }
        else:
            return {
                'nivel': 'DEPENDENCIA_COMPLETA',
                'descricao': 'Necessita assistência substancial ou total',
                'cor': 'danger'
            }

    @staticmethod
    def _classificar_gmfm(porcentagem):
        """
        Classifica função motora grossa no GMFM

        Args:
            porcentagem: Porcentagem GMFM total (0-100)

        Returns:
            str: Interpretação do nível funcional
        """
        if porcentagem >= 90:
            return 'Função motora grossa excelente - próximo ao desenvolvimento típico'
        elif porcentagem >= 70:
            return 'Função motora grossa boa - dificuldades leves'
        elif porcentagem >= 50:
            return 'Função motora grossa moderada - dificuldades moderadas'
        elif porcentagem >= 30:
            return 'Função motora grossa limitada - dificuldades importantes'
        else:
            return 'Função motora grossa severamente limitada'
