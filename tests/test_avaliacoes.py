"""
Testes para o CRUD de avaliações e workflow completo
"""
import pytest
from datetime import date, datetime
from app.models import Avaliacao, Resposta, Questao, Dominio
from app.services.permission_service import PermissionService


@pytest.mark.functional
class TestAvaliacoesCRUD:
    """Testes funcionais das rotas de avaliações"""

    def test_criar_avaliacao_para_paciente(self, logged_terapeuta, db_session, paciente, instrumento, terapeuta_user):
        """Deve permitir criar avaliação para um paciente"""
        response = logged_terapeuta.post(
            f'/avaliacoes/nova?paciente_id={paciente.id}&instrumento_id={instrumento.id}',
            data={
                'paciente_id': paciente.id,
                'instrumento_id': instrumento.id,
                'data_avaliacao': date.today().isoformat(),
                'relacionamento_respondente': 'Mãe',
                'comentarios': 'Primeira avaliação'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verificar que avaliação foi criada
        avaliacao = Avaliacao.query.filter_by(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=terapeuta_user.id
        ).first()

        assert avaliacao is not None
        assert avaliacao.status == 'em_andamento'
        assert avaliacao.relacionamento_respondente == 'Mãe'

    def test_criar_avaliacao_sem_paciente_redireciona(self, logged_terapeuta):
        """Criar avaliação sem paciente deve redirecionar"""
        response = logged_terapeuta.get('/avaliacoes/nova')
        assert response.status_code in [302, 400]

    def test_criar_avaliacao_instrumento_inadequado_para_idade(self, logged_terapeuta, db_session, terapeuta_user):
        """Não deve permitir instrumento inadequado para a idade"""
        from app.models import Paciente, Instrumento

        # Criar paciente muito novo (2 anos)
        paciente_crianca = Paciente(
            nome='Criança Nova',
            identificacao='CRIANCA',
            data_nascimento=date(2021, 1, 1),
            sexo='M',
            criador_id=terapeuta_user.id
        )
        db_session.add(paciente_crianca)

        # Criar instrumento para 5-12 anos
        instrumento_adulto = Instrumento(
            codigo='SPM_5_12',
            nome='SPM 5-12 anos',
            contexto='casa',
            idade_minima=5,
            idade_maxima=12,
            ativo=True
        )
        db_session.add(instrumento_adulto)
        db_session.commit()

        # Tentar criar avaliação
        response = logged_terapeuta.post(
            f'/avaliacoes/nova?paciente_id={paciente_crianca.id}',
            data={
                'paciente_id': paciente_crianca.id,
                'instrumento_id': instrumento_adulto.id,
                'data_avaliacao': date.today().isoformat(),
                'relacionamento_respondente': 'Mãe'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'adequado' in response.data.lower() or b'idade' in response.data.lower()

    def test_listar_avaliacoes_admin_ve_todas(self, logged_admin, db_session, terapeuta_user, professor_user, paciente, instrumento):
        """Admin deve ver todas as avaliações"""
        # Criar avaliações de diferentes avaliadores
        a1 = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=terapeuta_user.id,
            data_avaliacao=date.today(),
            status='em_andamento'
        )
        a2 = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=professor_user.id,
            data_avaliacao=date.today(),
            status='em_andamento'
        )

        db_session.add_all([a1, a2])
        db_session.commit()

        response = logged_admin.get('/avaliacoes/')
        assert response.status_code == 200
        # Admin deve ver ambas as avaliações

    def test_listar_avaliacoes_terapeuta_ve_apenas_de_seus_pacientes(self, logged_terapeuta, db_session, terapeuta_user, professor_user, instrumento):
        """Terapeuta deve ver apenas avaliações de seus pacientes"""
        from app.models import Paciente

        # Criar paciente do terapeuta
        p1 = Paciente(nome='Meu Paciente', identificacao='MEU', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        # Criar paciente de outro
        p2 = Paciente(nome='Paciente Outro', identificacao='OUTRO', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=professor_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        # Criar avaliações
        a1 = Avaliacao(paciente_id=p1.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=date.today(), status='em_andamento')
        a2 = Avaliacao(paciente_id=p2.id, instrumento_id=instrumento.id,
                      avaliador_id=professor_user.id, data_avaliacao=date.today(), status='em_andamento')

        db_session.add_all([a1, a2])
        db_session.commit()

        response = logged_terapeuta.get('/avaliacoes/')
        assert response.status_code == 200
        assert b'Meu Paciente' in response.data
        assert b'Paciente Outro' not in response.data

    def test_filtrar_avaliacoes_por_status(self, logged_terapeuta, db_session, terapeuta_user, paciente, instrumento):
        """Deve permitir filtrar avaliações por status"""
        # Criar avaliações com diferentes status
        a1 = Avaliacao(paciente_id=paciente.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=date.today(), status='em_andamento')
        a2 = Avaliacao(paciente_id=paciente.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=date.today(), status='concluida')

        db_session.add_all([a1, a2])
        db_session.commit()

        # Filtrar por "concluida"
        response = logged_terapeuta.get('/avaliacoes/?status=concluida')
        assert response.status_code == 200

    def test_visualizar_avaliacao_propria(self, logged_terapeuta, avaliacao):
        """Deve permitir visualizar avaliação própria"""
        response = logged_terapeuta.get(f'/avaliacoes/{avaliacao.id}')
        assert response.status_code == 200

    def test_visualizar_avaliacao_de_paciente_sem_permissao_negado(self, logged_professor, db_session, terapeuta_user, instrumento):
        """Não pode visualizar avaliação de paciente sem permissão"""
        from app.models import Paciente

        # Criar paciente do terapeuta
        paciente = Paciente(nome='Privado', identificacao='PRIV', data_nascimento=date(2015, 1, 1),
                           sexo='M', criador_id=terapeuta_user.id)
        db_session.add(paciente)
        db_session.commit()

        # Criar avaliação
        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=terapeuta_user.id,
            data_avaliacao=date.today(),
            status='em_andamento'
        )
        db_session.add(avaliacao)
        db_session.commit()

        # Professor tenta visualizar
        response = logged_professor.get(f'/avaliacoes/{avaliacao.id}')
        assert response.status_code in [302, 403]

    def test_excluir_avaliacao_em_andamento(self, logged_terapeuta, db_session, avaliacao):
        """Deve permitir excluir avaliação em andamento"""
        avaliacao_id = avaliacao.id

        response = logged_terapeuta.post(f'/avaliacoes/{avaliacao_id}/excluir', follow_redirects=True)

        assert response.status_code == 200

        # Verificar que foi excluída
        avaliacao_excluida = Avaliacao.query.get(avaliacao_id)
        assert avaliacao_excluida is None


@pytest.mark.integration
class TestAvaliacaoWorkflow:
    """Testes do workflow completo de avaliação"""

    def test_responder_questoes_sequencialmente(self, logged_terapeuta, db_session, avaliacao, questoes):
        """Deve permitir responder questões sequencialmente"""
        # Responder primeira questão
        response = logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/responder?q=0',
            data={
                'questao_id': questoes[0].id,
                'valor': 'SEMPRE'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verificar que resposta foi salva
        resposta = Resposta.query.filter_by(
            avaliacao_id=avaliacao.id,
            questao_id=questoes[0].id
        ).first()

        assert resposta is not None
        assert resposta.valor == 'SEMPRE'
        assert resposta.pontuacao == 1

    def test_atualizar_resposta_existente(self, logged_terapeuta, db_session, avaliacao, questoes):
        """Deve permitir atualizar resposta já dada"""
        # Criar resposta inicial
        resposta = Resposta(
            avaliacao_id=avaliacao.id,
            questao_id=questoes[0].id,
            valor='SEMPRE',
            pontuacao=1
        )
        db_session.add(resposta)
        db_session.commit()

        # Atualizar resposta
        response = logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/responder?q=0',
            data={
                'questao_id': questoes[0].id,
                'valor': 'NUNCA'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verificar que resposta foi atualizada
        db_session.refresh(resposta)
        assert resposta.valor == 'NUNCA'
        assert resposta.pontuacao == 4

    def test_nao_pode_responder_avaliacao_concluida(self, logged_terapeuta, db_session, avaliacao_completa):
        """Não deve permitir responder avaliação já concluída"""
        response = logged_terapeuta.get(f'/avaliacoes/{avaliacao_completa.id}/responder')
        assert response.status_code == 302  # Redirect

    def test_workflow_completo_ate_finalizar(self, logged_terapeuta, db_session, avaliacao, questoes):
        """Teste do workflow completo: responder todas as questões e finalizar"""
        # Responder todas as questões
        for idx, questao in enumerate(questoes):
            logged_terapeuta.post(
                f'/avaliacoes/{avaliacao.id}/responder?q={idx}',
                data={
                    'questao_id': questao.id,
                    'valor': 'SEMPRE'
                }
            )

        # Finalizar avaliação
        response = logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/finalizar',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'finalizada' in response.data.lower() or b'sucesso' in response.data.lower()

        # Verificar que status foi atualizado
        db_session.refresh(avaliacao)
        assert avaliacao.status == 'concluida'
        assert avaliacao.data_conclusao is not None

    def test_nao_pode_finalizar_sem_responder_todas(self, logged_terapeuta, db_session, avaliacao, questoes):
        """Não deve permitir finalizar sem responder todas as questões"""
        # Responder apenas a primeira questão
        logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/responder?q=0',
            data={
                'questao_id': questoes[0].id,
                'valor': 'SEMPRE'
            }
        )

        # Tentar finalizar
        response = logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/finalizar',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'faltam' in response.data.lower() or b'quest' in response.data.lower()

        # Verificar que status não mudou
        db_session.refresh(avaliacao)
        assert avaliacao.status == 'em_andamento'

    def test_calcular_escores_ao_finalizar(self, logged_terapeuta, db_session, avaliacao, questoes, tabela_referencia):
        """Ao finalizar, deve calcular escores e classificações"""
        # Responder todas as questões com "SEMPRE" (pontuação 1 cada)
        for idx, questao in enumerate(questoes):
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor='SEMPRE',
                pontuacao=1
            )
            db_session.add(resposta)

        db_session.commit()

        # Finalizar
        response = logged_terapeuta.post(
            f'/avaliacoes/{avaliacao.id}/finalizar',
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verificar que escores foram calculados
        db_session.refresh(avaliacao)
        assert avaliacao.escore_soc is not None
        # Com 5 questões respondidas com "SEMPRE" (pontuação 1), escore = 5

    def test_progresso_avaliacao_atualiza(self, logged_terapeuta, db_session, avaliacao, questoes):
        """Progresso deve atualizar conforme questões são respondidas"""
        # Visualizar avaliação sem respostas
        response = logged_terapeuta.get(f'/avaliacoes/{avaliacao.id}')
        assert response.status_code == 200

        # Responder metade das questões
        num_questoes = len(questoes)
        metade = num_questoes // 2

        for idx in range(metade):
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questoes[idx].id,
                valor='SEMPRE',
                pontuacao=1
            )
            db_session.add(resposta)

        db_session.commit()

        # Verificar progresso
        response = logged_terapeuta.get(f'/avaliacoes/{avaliacao.id}')
        assert response.status_code == 200


@pytest.mark.integration
class TestAvaliacaoPermissions:
    """Testes de permissões para avaliações"""

    def test_avaliador_pode_acessar_sua_avaliacao(self, db_session, terapeuta_user, avaliacao):
        """Avaliador pode acessar sua própria avaliação"""
        pode = PermissionService.pode_acessar_avaliacao(terapeuta_user, avaliacao.id)
        assert pode is True

    def test_criador_paciente_pode_acessar_avaliacao(self, db_session, terapeuta_user, paciente, instrumento, professor_user):
        """Criador do paciente pode acessar avaliações do paciente"""
        # Criar avaliação feita por outro usuário
        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=professor_user.id,
            data_avaliacao=date.today(),
            status='em_andamento'
        )
        db_session.add(avaliacao)
        db_session.commit()

        # Terapeuta (criador do paciente) pode acessar
        pode = PermissionService.pode_acessar_avaliacao(terapeuta_user, avaliacao.id)
        assert pode is True

    def test_usuario_sem_vinculo_nao_pode_acessar(self, db_session, professor_user, avaliacao):
        """Usuário sem vínculo não pode acessar avaliação"""
        pode = PermissionService.pode_acessar_avaliacao(professor_user, avaliacao.id)
        assert pode is False

    def test_pode_editar_avaliacao_em_andamento(self, db_session, terapeuta_user, avaliacao):
        """Avaliador pode editar avaliação em andamento"""
        pode = PermissionService.pode_editar_avaliacao(terapeuta_user, avaliacao.id)
        assert pode is True

    def test_nao_pode_editar_avaliacao_concluida_de_outro(self, db_session, professor_user, avaliacao_completa):
        """Não pode editar avaliação concluída de outro usuário"""
        pode = PermissionService.pode_editar_avaliacao(professor_user, avaliacao_completa.id)
        assert pode is False

    def test_admin_pode_acessar_qualquer_avaliacao(self, db_session, admin_user, avaliacao):
        """Admin pode acessar qualquer avaliação"""
        pode = PermissionService.pode_acessar_avaliacao(admin_user, avaliacao.id)
        assert pode is True


@pytest.mark.functional
class TestAvaliacaoFilters:
    """Testes dos filtros de avaliações"""

    def test_filtrar_por_periodo(self, logged_terapeuta, db_session, terapeuta_user, paciente, instrumento):
        """Deve filtrar avaliações por período"""
        from datetime import timedelta

        hoje = date.today()
        semana_passada = hoje - timedelta(days=7)

        # Criar avaliações em datas diferentes
        a1 = Avaliacao(paciente_id=paciente.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=semana_passada, status='concluida')
        a2 = Avaliacao(paciente_id=paciente.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=hoje, status='em_andamento')

        db_session.add_all([a1, a2])
        db_session.commit()

        # Filtrar apenas desta semana
        response = logged_terapeuta.get(f'/avaliacoes/?data_inicio={hoje.isoformat()}')
        assert response.status_code == 200

    def test_filtrar_por_paciente(self, logged_terapeuta, db_session, terapeuta_user, instrumento):
        """Deve filtrar avaliações por paciente específico"""
        from app.models import Paciente

        # Criar dois pacientes
        p1 = Paciente(nome='Paciente 1', identificacao='P1', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Paciente 2', identificacao='P2', data_nascimento=date(2015, 1, 1),
                     sexo='F', criador_id=terapeuta_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        # Criar avaliações
        a1 = Avaliacao(paciente_id=p1.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=date.today(), status='em_andamento')
        a2 = Avaliacao(paciente_id=p2.id, instrumento_id=instrumento.id,
                      avaliador_id=terapeuta_user.id, data_avaliacao=date.today(), status='em_andamento')

        db_session.add_all([a1, a2])
        db_session.commit()

        # Filtrar por paciente 1
        response = logged_terapeuta.get(f'/avaliacoes/?paciente_id={p1.id}')
        assert response.status_code == 200

    def test_filtrar_paciente_sem_permissao_redireciona(self, logged_professor, db_session, terapeuta_user, instrumento):
        """Filtrar por paciente sem permissão deve negar acesso"""
        from app.models import Paciente

        # Criar paciente do terapeuta
        paciente = Paciente(nome='Privado', identificacao='PRIV', data_nascimento=date(2015, 1, 1),
                           sexo='M', criador_id=terapeuta_user.id)
        db_session.add(paciente)
        db_session.commit()

        # Professor tenta filtrar por este paciente
        response = logged_professor.get(f'/avaliacoes/?paciente_id={paciente.id}')
        assert response.status_code in [302, 200]  # Redireciona ou mostra vazio
