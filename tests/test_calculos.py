"""
Testes para os serviços de cálculo e classificação de escores
"""
import pytest
from datetime import date
from app.models import Avaliacao, Resposta, Questao, Dominio, TabelaReferencia
from app.services.calculo_service import CalculoService
from app.services.classificacao_service import ClassificacaoService


@pytest.mark.unit
class TestCalculoService:
    """Testes unitários do CalculoService"""

    def test_escala_normal_nunca(self):
        """NUNCA deve valer 4 pontos na escala normal"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('NUNCA', escala_invertida=False)
        assert pontuacao == 4

    def test_escala_normal_ocasional(self):
        """OCASIONAL deve valer 3 pontos na escala normal"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('OCASIONAL', escala_invertida=False)
        assert pontuacao == 3

    def test_escala_normal_frequente(self):
        """FREQUENTE deve valer 2 pontos na escala normal"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('FREQUENTE', escala_invertida=False)
        assert pontuacao == 2

    def test_escala_normal_sempre(self):
        """SEMPRE deve valer 1 ponto na escala normal"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('SEMPRE', escala_invertida=False)
        assert pontuacao == 1

    def test_escala_invertida_nunca(self):
        """NUNCA deve valer 1 ponto na escala invertida"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('NUNCA', escala_invertida=True)
        assert pontuacao == 1

    def test_escala_invertida_sempre(self):
        """SEMPRE deve valer 4 pontos na escala invertida"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('SEMPRE', escala_invertida=True)
        assert pontuacao == 4

    def test_valor_minusculo_funciona(self):
        """Deve aceitar valores em minúsculo"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('nunca', escala_invertida=False)
        assert pontuacao == 4

    def test_valor_invalido_retorna_zero(self):
        """Valor inválido deve retornar 0"""
        pontuacao = CalculoService.calcular_pontuacao_resposta('INVALIDO', escala_invertida=False)
        assert pontuacao == 0

    def test_validar_resposta_valida(self):
        """Deve validar respostas válidas"""
        assert CalculoService.validar_resposta('NUNCA') is True
        assert CalculoService.validar_resposta('OCASIONAL') is True
        assert CalculoService.validar_resposta('FREQUENTE') is True
        assert CalculoService.validar_resposta('SEMPRE') is True

    def test_validar_resposta_invalida(self):
        """Deve rejeitar respostas inválidas"""
        assert CalculoService.validar_resposta('INVALIDO') is False
        assert CalculoService.validar_resposta('') is False
        assert CalculoService.validar_resposta('12345') is False

    def test_validar_resposta_case_insensitive(self):
        """Validação deve ser case-insensitive"""
        assert CalculoService.validar_resposta('nunca') is True
        assert CalculoService.validar_resposta('Sempre') is True
        assert CalculoService.validar_resposta('OCASIONAL') is True


@pytest.mark.integration
class TestCalculoIntegration:
    """Testes de integração dos cálculos com banco de dados"""

    def test_calcular_escores_dominio_unico(self, db_session, avaliacao, dominio, questoes):
        """Deve calcular escore corretamente para um domínio"""
        # Responder todas as 5 questões com "SEMPRE" (pontuação 1 cada)
        for questao in questoes:
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor='SEMPRE',
                pontuacao=1
            )
            db_session.add(resposta)

        db_session.commit()

        # Calcular escores
        escores = CalculoService.calcular_escores(avaliacao)

        # Com 5 questões respondidas com "SEMPRE" (pontuação 1), escore SOC = 5
        assert escores['SOC'] == 5
        assert escores['TOTAL'] == 5

    def test_calcular_escores_diferentes_valores(self, db_session, avaliacao, dominio, questoes):
        """Deve calcular escore com diferentes valores de resposta"""
        # Responder com valores variados
        valores = ['NUNCA', 'OCASIONAL', 'FREQUENTE', 'SEMPRE', 'NUNCA']
        pontuacoes = [4, 3, 2, 1, 4]  # Escala normal

        for questao, valor, pontuacao in zip(questoes, valores, pontuacoes):
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor=valor,
                pontuacao=pontuacao
            )
            db_session.add(resposta)

        db_session.commit()

        escores = CalculoService.calcular_escores(avaliacao)

        # Soma: 4 + 3 + 2 + 1 + 4 = 14
        assert escores['SOC'] == 14
        assert escores['TOTAL'] == 14

    def test_calcular_escores_com_escala_invertida(self, db_session, avaliacao, instrumento):
        """Deve calcular corretamente com escala invertida"""
        # Criar domínio com escala invertida
        dominio_inv = Dominio(
            instrumento_id=instrumento.id,
            codigo='BAL',
            nome='Equilíbrio',
            ordem=2,
            escala_invertida=True
        )
        db_session.add(dominio_inv)
        db_session.commit()

        # Criar questões
        questao1 = Questao(dominio_id=dominio_inv.id, numero=1, texto='Q1', ativo=True)
        questao2 = Questao(dominio_id=dominio_inv.id, numero=2, texto='Q2', ativo=True)
        db_session.add_all([questao1, questao2])
        db_session.commit()

        # Responder com "SEMPRE" (pontuação 4 na escala invertida)
        resposta1 = Resposta(avaliacao_id=avaliacao.id, questao_id=questao1.id,
                            valor='SEMPRE', pontuacao=4)
        resposta2 = Resposta(avaliacao_id=avaliacao.id, questao_id=questao2.id,
                            valor='SEMPRE', pontuacao=4)
        db_session.add_all([resposta1, resposta2])
        db_session.commit()

        escores = CalculoService.calcular_escores(avaliacao)

        # Com escala invertida, SEMPRE vale 4
        assert escores['BAL'] == 8

    def test_atualizar_escores_avaliacao(self, db_session, avaliacao, dominio, questoes):
        """Deve atualizar escores no banco de dados"""
        # Responder questões
        for questao in questoes:
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor='NUNCA',
                pontuacao=4
            )
            db_session.add(resposta)

        db_session.commit()

        # Atualizar escores
        escores = CalculoService.atualizar_escores_avaliacao(avaliacao)

        # Verificar que os campos foram atualizados
        db_session.refresh(avaliacao)
        assert avaliacao.escore_soc == 20  # 5 questões x 4 pontos
        assert avaliacao.escore_total == 20

    def test_calcular_escores_questoes_nao_respondidas(self, db_session, avaliacao, dominio, questoes):
        """Deve calcular 0 para questões não respondidas"""
        # Responder apenas a primeira questão
        resposta = Resposta(
            avaliacao_id=avaliacao.id,
            questao_id=questoes[0].id,
            valor='SEMPRE',
            pontuacao=1
        )
        db_session.add(resposta)
        db_session.commit()

        escores = CalculoService.calcular_escores(avaliacao)

        # Apenas 1 questão respondida
        assert escores['SOC'] == 1


@pytest.mark.unit
class TestClassificacaoService:
    """Testes unitários do ClassificacaoService"""

    def test_get_classificacao_texto_disfuncao_definitiva(self):
        """Deve retornar texto correto para disfunção definitiva"""
        texto = ClassificacaoService._get_classificacao_texto(
            ClassificacaoService.DISFUNCAO_DEFINITIVA
        )
        assert 'Disfunção Definitiva' in texto

    def test_get_classificacao_texto_provavel_disfuncao(self):
        """Deve retornar texto correto para provável disfunção"""
        texto = ClassificacaoService._get_classificacao_texto(
            ClassificacaoService.PROVAVEL_DISFUNCAO
        )
        assert 'Provável Disfunção' in texto

    def test_get_classificacao_texto_tipico(self):
        """Deve retornar texto correto para típico"""
        texto = ClassificacaoService._get_classificacao_texto(
            ClassificacaoService.TIPICO
        )
        assert 'Típico' in texto

    def test_get_classificacao_texto_invalido(self):
        """Deve retornar 'Não classificado' para valor inválido"""
        texto = ClassificacaoService._get_classificacao_texto('INVALIDO')
        assert 'Não classificado' in texto

    def test_interpretar_resultado_disfuncao_definitiva(self):
        """Deve retornar interpretação para disfunção definitiva"""
        interpretacao = ClassificacaoService.interpretar_resultado(
            ClassificacaoService.DISFUNCAO_DEFINITIVA
        )
        assert 'disfunção definitiva' in interpretacao.lower()
        assert 'especializada' in interpretacao.lower()

    def test_interpretar_resultado_provavel_disfuncao(self):
        """Deve retornar interpretação para provável disfunção"""
        interpretacao = ClassificacaoService.interpretar_resultado(
            ClassificacaoService.PROVAVEL_DISFUNCAO
        )
        assert 'provável disfunção' in interpretacao.lower()

    def test_interpretar_resultado_tipico(self):
        """Deve retornar interpretação para típico"""
        interpretacao = ClassificacaoService.interpretar_resultado(
            ClassificacaoService.TIPICO
        )
        assert 'típico' in interpretacao.lower()


@pytest.mark.integration
class TestClassificacaoIntegration:
    """Testes de integração da classificação"""

    def test_obter_classificacao_com_tabela_referencia(self, db_session, instrumento, dominio):
        """Deve obter classificação da tabela de referência"""
        # Criar tabela de referência
        tabela = TabelaReferencia(
            instrumento_id=instrumento.id,
            dominio_codigo='SOC',
            escore_min=20,
            escore_max=25,
            t_score=60,
            percentil_min=75,
            percentil_max=84,
            classificacao='TIPICO'
        )
        db_session.add(tabela)
        db_session.commit()

        # Obter classificação para escore 22
        classificacao = ClassificacaoService.obter_classificacao(
            instrumento.id, 'SOC', 22
        )

        assert classificacao['t_score'] == 60
        assert classificacao['percentil'] == (75, 84)
        assert classificacao['classificacao'] == 'TIPICO'

    def test_obter_classificacao_sem_tabela(self, db_session, instrumento):
        """Deve retornar None quando não encontrar tabela de referência"""
        classificacao = ClassificacaoService.obter_classificacao(
            instrumento.id, 'SOC', 100
        )

        assert classificacao['t_score'] is None
        assert classificacao['percentil'] == (None, None)
        assert classificacao['classificacao'] is None

    def test_classificar_avaliacao_completa(self, db_session, avaliacao, dominio, questoes, instrumento):
        """Deve classificar todos os domínios de uma avaliação"""
        # Responder questões
        for questao in questoes:
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor='NUNCA',
                pontuacao=4
            )
            db_session.add(resposta)

        db_session.commit()

        # Calcular escores primeiro
        CalculoService.atualizar_escores_avaliacao(avaliacao)
        db_session.refresh(avaliacao)

        # Criar tabela de referência para o escore calculado
        escore_soc = avaliacao.escore_soc
        tabela = TabelaReferencia(
            instrumento_id=instrumento.id,
            dominio_codigo='SOC',
            escore_min=escore_soc - 2,
            escore_max=escore_soc + 2,
            t_score=55,
            percentil_min=70,
            percentil_max=75,
            classificacao='TIPICO'
        )
        db_session.add(tabela)
        db_session.commit()

        # Classificar
        classificacoes = ClassificacaoService.classificar_avaliacao(avaliacao)

        # Verificar que classificação foi aplicada
        db_session.refresh(avaliacao)
        assert avaliacao.t_score_soc == 55
        assert avaliacao.classificacao_soc == 'TIPICO'

    def test_classificacao_multiplos_dominios(self, db_session, avaliacao, instrumento):
        """Deve classificar múltiplos domínios"""
        # Criar dois domínios
        dom1 = Dominio(instrumento_id=instrumento.id, codigo='SOC', nome='Social', ordem=1)
        dom2 = Dominio(instrumento_id=instrumento.id, codigo='VIS', nome='Visual', ordem=2)
        db_session.add_all([dom1, dom2])
        db_session.commit()

        # Criar questões para cada domínio
        q1 = Questao(dominio_id=dom1.id, numero=1, texto='Q1', ativo=True)
        q2 = Questao(dominio_id=dom2.id, numero=1, texto='Q2', ativo=True)
        db_session.add_all([q1, q2])
        db_session.commit()

        # Responder
        r1 = Resposta(avaliacao_id=avaliacao.id, questao_id=q1.id, valor='NUNCA', pontuacao=4)
        r2 = Resposta(avaliacao_id=avaliacao.id, questao_id=q2.id, valor='SEMPRE', pontuacao=1)
        db_session.add_all([r1, r2])
        db_session.commit()

        # Calcular escores
        CalculoService.atualizar_escores_avaliacao(avaliacao)
        db_session.refresh(avaliacao)

        # Criar tabelas de referência
        t1 = TabelaReferencia(
            instrumento_id=instrumento.id, dominio_codigo='SOC',
            escore_min=0, escore_max=10, t_score=50, percentil_min=50, percentil_max=60,
            classificacao='TIPICO'
        )
        t2 = TabelaReferencia(
            instrumento_id=instrumento.id, dominio_codigo='VIS',
            escore_min=0, escore_max=10, t_score=45, percentil_min=40, percentil_max=50,
            classificacao='PROVAVEL_DISFUNCAO'
        )
        db_session.add_all([t1, t2])
        db_session.commit()

        # Classificar
        classificacoes = ClassificacaoService.classificar_avaliacao(avaliacao)

        # Verificar
        db_session.refresh(avaliacao)
        assert avaliacao.t_score_soc == 50
        assert avaliacao.t_score_vis == 45
        assert avaliacao.classificacao_soc == 'TIPICO'
        assert avaliacao.classificacao_vis == 'PROVAVEL_DISFUNCAO'


@pytest.mark.integration
class TestWorkflowCompleto:
    """Testes do workflow completo: responder -> calcular -> classificar"""

    def test_workflow_completo_calculo_classificacao(self, db_session, avaliacao, dominio, questoes, instrumento):
        """Teste end-to-end do workflow completo"""
        # 1. Responder todas as questões
        valores = ['NUNCA', 'OCASIONAL', 'FREQUENTE', 'SEMPRE', 'NUNCA']
        pontuacoes = [4, 3, 2, 1, 4]

        for questao, valor, pontuacao in zip(questoes, valores, pontuacoes):
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor=valor,
                pontuacao=pontuacao
            )
            db_session.add(resposta)

        db_session.commit()

        # 2. Calcular escores
        escores = CalculoService.atualizar_escores_avaliacao(avaliacao)
        db_session.refresh(avaliacao)

        # Verificar escore calculado: 4 + 3 + 2 + 1 + 4 = 14
        assert avaliacao.escore_soc == 14
        assert escores['SOC'] == 14

        # 3. Criar tabela de referência para este escore
        tabela = TabelaReferencia(
            instrumento_id=instrumento.id,
            dominio_codigo='SOC',
            escore_min=12,
            escore_max=16,
            t_score=48,
            percentil_min=30,
            percentil_max=40,
            classificacao='PROVAVEL_DISFUNCAO'
        )
        db_session.add(tabela)
        db_session.commit()

        # 4. Classificar
        classificacoes = ClassificacaoService.classificar_avaliacao(avaliacao)
        db_session.refresh(avaliacao)

        # Verificar classificação
        assert avaliacao.t_score_soc == 48
        assert avaliacao.classificacao_soc == 'PROVAVEL_DISFUNCAO'
        assert classificacoes['SOC']['t_score'] == 48
        assert classificacoes['SOC']['classificacao'] == 'PROVAVEL_DISFUNCAO'

    def test_recalcular_apos_modificar_resposta(self, db_session, avaliacao, dominio, questoes):
        """Deve recalcular corretamente após modificar resposta"""
        # Primeira rodada de respostas
        for questao in questoes:
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor='SEMPRE',
                pontuacao=1
            )
            db_session.add(resposta)

        db_session.commit()

        # Calcular
        CalculoService.atualizar_escores_avaliacao(avaliacao)
        db_session.refresh(avaliacao)
        escore_inicial = avaliacao.escore_soc

        # Modificar uma resposta
        resposta = Resposta.query.filter_by(
            avaliacao_id=avaliacao.id,
            questao_id=questoes[0].id
        ).first()
        resposta.valor = 'NUNCA'
        resposta.pontuacao = 4
        db_session.commit()

        # Recalcular
        CalculoService.atualizar_escores_avaliacao(avaliacao)
        db_session.refresh(avaliacao)
        escore_final = avaliacao.escore_soc

        # Escore deve ter aumentado em 3 (de 1 para 4)
        assert escore_final == escore_inicial + 3
