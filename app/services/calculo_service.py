"""
Serviço de Cálculo de Escores
Implementa a lógica de cálculo dos escores brutos por domínio
"""


class CalculoService:
    """Serviço para cálculo de escores"""

    # Mapeamento de valores para pontuações
    ESCALA_NORMAL = {
        'NUNCA': 4,
        'OCASIONAL': 3,
        'FREQUENTE': 2,
        'SEMPRE': 1
    }

    ESCALA_INVERTIDA = {
        'NUNCA': 1,
        'OCASIONAL': 2,
        'FREQUENTE': 3,
        'SEMPRE': 4
    }

    @staticmethod
    def calcular_pontuacao_resposta(valor, escala_invertida=False):
        """
        Calcula a pontuação de uma resposta

        Args:
            valor: Valor da resposta ('NUNCA', 'OCASIONAL', 'FREQUENTE', 'SEMPRE')
            escala_invertida: Se True, usa escala invertida

        Returns:
            int: Pontuação (1-4)
        """
        if not valor:
            return 0

        valor_upper = valor.upper()
        escala = CalculoService.ESCALA_INVERTIDA if escala_invertida else CalculoService.ESCALA_NORMAL
        if valor_upper in escala:
            return escala.get(valor_upper, 0)

        # Suporte para instrumentos com escala expandida (ex: Perfil Sensorial 2)
        try:
            from app.services.modulos_service import ModulosService
            return ModulosService.ESCALA_PERFIL_SENSORIAL.get(valor_upper, 0)
        except Exception:
            return 0

    @staticmethod
    def calcular_escores(avaliacao):
        """
        Calcula os escores brutos por domínio para uma avaliação

        Args:
            avaliacao: Instância de Avaliacao

        Returns:
            dict: Escores por domínio
        """
        escores = {}

        # Percorrer domínios do instrumento
        for dominio in avaliacao.instrumento.dominios:
            escore_dominio = 0

            # Obter questões do domínio
            questoes = dominio.questoes.filter_by(ativo=True).all()

            for questao in questoes:
                # Buscar resposta para esta questão nesta avaliação
                resposta = avaliacao.respostas.filter_by(questao_id=questao.id).first()

                if resposta:
                    escore_dominio += resposta.pontuacao

            escores[dominio.codigo] = escore_dominio

        # Calcular escore total (soma de todos os domínios)
        escores['TOTAL'] = sum(escores.values())

        return escores

    @staticmethod
    def atualizar_escores_avaliacao(avaliacao):
        """
        Atualiza os escores da avaliação no banco de dados

        Args:
            avaliacao: Instância de Avaliacao

        Returns:
            dict: Escores calculados
        """
        from app import db

        escores = CalculoService.calcular_escores(avaliacao)

        # Atualizar campos de escore na avaliação
        avaliacao.escore_soc = escores.get('SOC', 0)
        avaliacao.escore_vis = escores.get('VIS', 0)
        avaliacao.escore_hea = escores.get('HEA', 0)
        avaliacao.escore_tou = escores.get('TOU', 0)
        avaliacao.escore_bod = escores.get('BOD', 0)
        avaliacao.escore_bal = escores.get('BAL', 0)
        avaliacao.escore_pla = escores.get('PLA', 0)
        avaliacao.escore_olf = escores.get('OLF', 0)  # Apenas SPM-P
        avaliacao.escore_total = escores.get('TOTAL', 0)

        db.session.commit()

        return escores

    @staticmethod
    def validar_resposta(valor):
        """
        Valida se o valor da resposta é válido

        Args:
            valor: Valor a validar

        Returns:
            bool: True se válido
        """
        valores_validos = ['NUNCA', 'OCASIONAL', 'FREQUENTE', 'SEMPRE']
        return valor.upper() in valores_validos
