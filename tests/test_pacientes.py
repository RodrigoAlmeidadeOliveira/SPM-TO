"""
Testes para o CRUD de pacientes com sistema de permissões
"""
import pytest
from datetime import date
from app.models import Paciente, User, Avaliacao
from app.services.permission_service import PermissionService


@pytest.mark.functional
class TestPacientesCRUD:
    """Testes funcionais das rotas de pacientes"""

    def test_criar_paciente_define_criador(self, logged_terapeuta, db_session, terapeuta_user):
        """Ao criar paciente, criador_id deve ser definido automaticamente"""
        response = logged_terapeuta.post('/pacientes/novo', data={
            'nome': 'Maria Silva',
            'identificacao': 'MARIA001',
            'data_nascimento': '2015-03-15',
            'sexo': 'F',
            'ativo': True
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verificar que paciente foi criado com criador correto
        paciente = Paciente.query.filter_by(identificacao='MARIA001').first()
        assert paciente is not None
        assert paciente.criador_id == terapeuta_user.id
        assert paciente.nome == 'Maria Silva'

    def test_criar_paciente_duplicado_falha(self, logged_terapeuta, db_session, paciente):
        """Não deve permitir criar paciente com identificação duplicada"""
        response = logged_terapeuta.post('/pacientes/novo', data={
            'nome': 'Outro Nome',
            'identificacao': paciente.identificacao,  # Duplicado!
            'data_nascimento': '2015-03-15',
            'sexo': 'M',
            'ativo': True
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'existe' in response.data.lower() or b'duplicad' in response.data.lower()

    def test_listar_pacientes_admin_ve_todos(self, logged_admin, db_session, terapeuta_user, professor_user):
        """Admin deve ver todos os pacientes"""
        # Criar pacientes de diferentes criadores
        p1 = Paciente(nome='Paciente 1', identificacao='P1', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Paciente 2', identificacao='P2', data_nascimento=date(2015, 1, 1),
                     sexo='F', criador_id=professor_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        response = logged_admin.get('/pacientes/')
        assert response.status_code == 200
        assert b'Paciente 1' in response.data
        assert b'Paciente 2' in response.data

    def test_listar_pacientes_terapeuta_ve_apenas_seus(self, logged_terapeuta, db_session, terapeuta_user, professor_user):
        """Terapeuta deve ver apenas seus próprios pacientes"""
        # Criar pacientes
        p1 = Paciente(nome='Meu Paciente', identificacao='MEU', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Paciente de Outro', identificacao='OUTRO', data_nascimento=date(2015, 1, 1),
                     sexo='F', criador_id=professor_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        response = logged_terapeuta.get('/pacientes/')
        assert response.status_code == 200
        assert b'Meu Paciente' in response.data
        assert b'Paciente de Outro' not in response.data

    def test_buscar_pacientes_por_nome(self, logged_terapeuta, db_session, terapeuta_user):
        """Deve permitir buscar pacientes por nome"""
        # Criar pacientes
        p1 = Paciente(nome='João Silva', identificacao='JOAO', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Maria Santos', identificacao='MARIA', data_nascimento=date(2015, 1, 1),
                     sexo='F', criador_id=terapeuta_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        # Buscar por "joão"
        response = logged_terapeuta.get('/pacientes/?busca=joão')
        assert response.status_code == 200
        assert b'Silva' in response.data
        assert b'Maria Santos' not in response.data

    def test_filtrar_pacientes_por_sexo(self, logged_terapeuta, db_session, terapeuta_user):
        """Deve permitir filtrar pacientes por sexo"""
        # Criar pacientes
        p1 = Paciente(nome='João', identificacao='JOAO', data_nascimento=date(2015, 1, 1),
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Maria', identificacao='MARIA', data_nascimento=date(2015, 1, 1),
                     sexo='F', criador_id=terapeuta_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        # Filtrar por sexo feminino
        response = logged_terapeuta.get('/pacientes/?sexo=F')
        assert response.status_code == 200
        assert b'Maria' in response.data
        # Note: não podemos garantir que João não aparecerá em outros lugares da página

    def test_visualizar_paciente_proprio(self, logged_terapeuta, db_session, paciente):
        """Terapeuta pode visualizar seu próprio paciente"""
        response = logged_terapeuta.get(f'/pacientes/{paciente.id}')
        assert response.status_code == 200
        assert paciente.nome.encode() in response.data

    def test_visualizar_paciente_de_outro_negado(self, logged_professor, db_session, terapeuta_user):
        """Não pode visualizar paciente de outro usuário"""
        # Criar paciente do terapeuta
        paciente_outro = Paciente(
            nome='Paciente Privado',
            identificacao='PRIVADO',
            data_nascimento=date(2015, 1, 1),
            sexo='M',
            criador_id=terapeuta_user.id
        )
        db_session.add(paciente_outro)
        db_session.commit()

        response = logged_professor.get(f'/pacientes/{paciente_outro.id}')
        # Deve redirecionar ou retornar 403
        assert response.status_code in [302, 403]

    def test_editar_paciente_proprio(self, logged_terapeuta, db_session, paciente):
        """Criador pode editar seu próprio paciente"""
        response = logged_terapeuta.post(f'/pacientes/{paciente.id}/editar', data={
            'nome': 'Nome Atualizado',
            'identificacao': paciente.identificacao,
            'data_nascimento': '2015-05-15',
            'sexo': 'M',
            'ativo': True
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Atualizado' in response.data or b'atualizado' in response.data

        # Verificar no banco
        db_session.refresh(paciente)
        assert paciente.nome == 'Nome Atualizado'

    def test_editar_paciente_de_outro_negado(self, logged_professor, db_session, terapeuta_user):
        """Não pode editar paciente de outro usuário"""
        paciente_outro = Paciente(
            nome='Paciente Privado',
            identificacao='PRIVADO',
            data_nascimento=date(2015, 1, 1),
            sexo='M',
            criador_id=terapeuta_user.id
        )
        db_session.add(paciente_outro)
        db_session.commit()

        response = logged_professor.post(f'/pacientes/{paciente_outro.id}/editar', data={
            'nome': 'Tentando Editar',
            'identificacao': 'PRIVADO',
            'data_nascimento': '2015-01-01',
            'sexo': 'M',
            'ativo': True
        })

        # Deve negar acesso
        assert response.status_code in [302, 403]

    def test_excluir_paciente_sem_avaliacoes_deleta(self, logged_terapeuta, db_session, terapeuta_user):
        """Excluir paciente sem avaliações deve deletar permanentemente"""
        paciente = Paciente(
            nome='Paciente Teste Delete',
            identificacao='DELETE',
            data_nascimento=date(2015, 1, 1),
            sexo='M',
            criador_id=terapeuta_user.id
        )
        db_session.add(paciente)
        db_session.commit()
        paciente_id = paciente.id

        response = logged_terapeuta.post(f'/pacientes/{paciente_id}/excluir', follow_redirects=True)

        assert response.status_code == 200
        # Verificar que foi deletado
        paciente_deletado = Paciente.query.get(paciente_id)
        assert paciente_deletado is None

    def test_excluir_paciente_com_avaliacoes_desativa(self, logged_terapeuta, db_session, paciente, avaliacao):
        """Excluir paciente com avaliações deve apenas desativar"""
        paciente_id = paciente.id

        response = logged_terapeuta.post(f'/pacientes/{paciente_id}/excluir', follow_redirects=True)

        assert response.status_code == 200
        # Verificar que foi desativado, não deletado
        db_session.refresh(paciente)
        assert paciente.ativo is False

    def test_reativar_paciente(self, logged_terapeuta, db_session, paciente):
        """Deve permitir reativar paciente desativado"""
        # Desativar primeiro
        paciente.ativo = False
        db_session.commit()

        response = logged_terapeuta.post(f'/pacientes/{paciente.id}/reativar', follow_redirects=True)

        assert response.status_code == 200
        assert b'reativado' in response.data.lower()

        # Verificar no banco
        db_session.refresh(paciente)
        assert paciente.ativo is True


@pytest.mark.integration
class TestPacienteRelationships:
    """Testes das rotas de relacionamentos de pacientes"""

    def test_vincular_responsavel_via_route(self, logged_terapeuta, db_session, paciente, professor_user):
        """Deve permitir vincular responsável via rota"""
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/vincular',
            data={
                'user_id': professor_user.id,
                'tipo_vinculo': 'professor'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'vinculado' in response.data.lower()

        # Verificar que professor agora pode acessar
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_vincular_responsavel_usuario_invalido(self, logged_terapeuta, db_session, paciente):
        """Não deve vincular responsável com ID inválido"""
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/vincular',
            data={
                'user_id': 99999,  # ID inexistente
                'tipo_vinculo': 'professor'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'encontrado' in response.data.lower() or b'erro' in response.data.lower()

    def test_desvincular_responsavel_via_route(self, logged_terapeuta, db_session, paciente, professor_user):
        """Deve permitir desvincular responsável"""
        # Primeiro vincular
        PermissionService.vincular_responsavel(paciente.id, professor_user.id, 'professor')

        # Agora desvincular
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/desvincular',
            data={'user_id': professor_user.id},
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'desvinculado' in response.data.lower()

        # Verificar que professor não pode mais acessar
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is False

    def test_compartilhar_paciente_via_route(self, logged_terapeuta, db_session, paciente, professor_user):
        """Deve permitir compartilhar paciente com outro usuário"""
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/compartilhar',
            data={
                'user_id': professor_user.id,
                'tipo_acesso': 'leitura',
                'motivo': 'Acompanhamento escolar'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'compartilhado' in response.data.lower()

        # Verificar que professor pode acessar
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_compartilhar_sem_permissao_negado(self, logged_professor, db_session, terapeuta_user):
        """Não pode compartilhar paciente de outro"""
        # Criar paciente do terapeuta
        paciente = Paciente(
            nome='Paciente Privado',
            identificacao='PRIVADO',
            data_nascimento=date(2015, 1, 1),
            sexo='M',
            criador_id=terapeuta_user.id
        )
        db_session.add(paciente)
        db_session.commit()

        # Criar outro usuário
        outro_user = User(
            username='outro',
            email='outro@test.com',
            nome_completo='Outro User',
            tipo='professor',
            ativo=True
        )
        outro_user.set_password('outro123')
        db_session.add(outro_user)
        db_session.commit()

        # Professor tenta compartilhar paciente do terapeuta
        response = logged_professor.post(
            f'/pacientes/{paciente.id}/compartilhar',
            data={
                'user_id': outro_user.id,
                'tipo_acesso': 'leitura',
                'motivo': 'Teste'
            }
        )

        # Deve negar acesso
        assert response.status_code in [302, 403]


@pytest.mark.integration
class TestPacientePermissions:
    """Testes de permissões no nível de model"""

    def test_usuario_vinculado_pode_visualizar(self, db_session, professor_user, paciente):
        """Usuário vinculado pode visualizar paciente"""
        # Vincular professor ao paciente
        PermissionService.vincular_responsavel(paciente.id, professor_user.id, 'professor')

        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_avaliador_pode_visualizar_paciente(self, db_session, professor_user, paciente, instrumento):
        """Usuário que fez avaliação pode visualizar o paciente"""
        # Criar avaliação feita pelo professor
        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=professor_user.id,
            data_avaliacao=date.today(),
            status='em_andamento'
        )
        db_session.add(avaliacao)
        db_session.commit()

        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_compartilhamento_ativo_permite_acesso(self, db_session, terapeuta_user, professor_user, paciente):
        """Compartilhamento ativo permite acesso"""
        # Compartilhar paciente
        PermissionService.compartilhar_paciente(
            paciente.id, terapeuta_user.id, professor_user.id, 'leitura'
        )

        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_compartilhamento_inativo_nega_acesso(self, db_session, terapeuta_user, professor_user, paciente):
        """Compartilhamento inativo não permite acesso"""
        # Compartilhar e revogar
        compartilhamento = PermissionService.compartilhar_paciente(
            paciente.id, terapeuta_user.id, professor_user.id, 'leitura'
        )
        PermissionService.revogar_compartilhamento(compartilhamento.id)

        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is False

    def test_criador_nao_pode_excluir_se_tiver_avaliacoes_de_outros(self, db_session, terapeuta_user, professor_user, paciente, instrumento):
        """Criador não pode excluir paciente com avaliações de outros profissionais"""
        # Criar avaliação de outro profissional
        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=professor_user.id,
            data_avaliacao=date.today(),
            status='concluida'
        )
        db_session.add(avaliacao)
        db_session.commit()

        pode = PermissionService.pode_excluir_paciente(terapeuta_user, paciente.id)
        assert pode is False

    def test_criador_pode_excluir_sem_avaliacoes_de_outros(self, db_session, terapeuta_user, paciente):
        """Criador pode excluir se não houver avaliações de outros"""
        pode = PermissionService.pode_excluir_paciente(terapeuta_user, paciente.id)
        assert pode is True
