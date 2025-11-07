"""
Testes do sistema de permissões granular
"""
import pytest
from app.services.permission_service import PermissionService
from app.models import Paciente, CompartilhamentoPaciente


@pytest.mark.integration
class TestPermissionService:
    """Testes do PermissionService"""

    def test_admin_pode_acessar_qualquer_paciente(self, db_session, admin_user, paciente):
        """Admin pode acessar qualquer paciente"""
        pode = PermissionService.pode_acessar_paciente(admin_user, paciente.id)
        assert pode is True

    def test_criador_pode_acessar_seu_paciente(self, db_session, terapeuta_user, paciente):
        """Criador pode acessar seu próprio paciente"""
        # paciente foi criado por terapeuta_user (conftest)
        pode = PermissionService.pode_acessar_paciente(terapeuta_user, paciente.id)
        assert pode is True

    def test_usuario_nao_pode_acessar_paciente_de_outro(self, db_session, professor_user, paciente):
        """Usuário não pode acessar paciente de outro"""
        # paciente foi criado por terapeuta_user
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is False

    def test_usuario_vinculado_pode_acessar(self, db_session, professor_user, paciente):
        """Usuário vinculado pode acessar paciente"""
        # Vincular professor ao paciente
        PermissionService.vincular_responsavel(
            paciente.id, professor_user.id, 'professor'
        )

        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_filtrar_pacientes_admin_ve_todos(self, db_session, admin_user, terapeuta_user):
        """Admin vê todos os pacientes"""
        # Criar 3 pacientes
        p1 = Paciente(nome='P1', identificacao='P1', data_nascimento='2015-01-01',
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='P2', identificacao='P2', data_nascimento='2015-01-01',
                     sexo='F', criador_id=admin_user.id)
        p3 = Paciente(nome='P3', identificacao='P3', data_nascimento='2015-01-01',
                     sexo='M', criador_id=terapeuta_user.id)

        db_session.add_all([p1, p2, p3])
        db_session.commit()

        query = Paciente.query
        query = PermissionService.filtrar_pacientes_por_permissao(query, admin_user)

        assert query.count() == 3  # Admin vê todos

    def test_filtrar_pacientes_terapeuta_ve_apenas_seus(self, db_session, terapeuta_user, professor_user):
        """Terapeuta vê apenas seus pacientes"""
        # Criar 2 pacientes do terapeuta e 1 do professor
        p1 = Paciente(nome='P1', identificacao='P1', data_nascimento='2015-01-01',
                     sexo='M', criador_id=terapeuta_user.id)
        p2 = Paciente(nome='P2', identificacao='P2', data_nascimento='2015-01-01',
                     sexo='F', criador_id=terapeuta_user.id)
        p3 = Paciente(nome='P3', identificacao='P3', data_nascimento='2015-01-01',
                     sexo='M', criador_id=professor_user.id)

        db_session.add_all([p1, p2, p3])
        db_session.commit()

        query = Paciente.query
        query = PermissionService.filtrar_pacientes_por_permissao(query, terapeuta_user)

        pacientes = query.all()
        assert len(pacientes) == 2
        assert all(p.criador_id == terapeuta_user.id for p in pacientes)

    def test_pode_editar_paciente_criador(self, db_session, terapeuta_user, paciente):
        """Criador pode editar seu paciente"""
        pode = PermissionService.pode_editar_paciente(terapeuta_user, paciente.id)
        assert pode is True

    def test_nao_pode_editar_paciente_de_outro(self, db_session, professor_user, paciente):
        """Não pode editar paciente de outro"""
        pode = PermissionService.pode_editar_paciente(professor_user, paciente.id)
        assert pode is False

    def test_pode_excluir_paciente_criador_sem_outras_avaliacoes(self, db_session, terapeuta_user, paciente):
        """Criador pode excluir se não houver avaliações de outros"""
        pode = PermissionService.pode_excluir_paciente(terapeuta_user, paciente.id)
        assert pode is True

    def test_vincular_responsavel(self, db_session, paciente, professor_user):
        """Testa vinculação de responsável"""
        sucesso = PermissionService.vincular_responsavel(
            paciente.id, professor_user.id, 'professor'
        )
        assert sucesso is True

        # Verificar que pode acessar agora
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_desvincular_responsavel(self, db_session, paciente, professor_user):
        """Testa desvinculação de responsável"""
        # Primeiro vincular
        PermissionService.vincular_responsavel(paciente.id, professor_user.id, 'professor')

        # Depois desvincular
        sucesso = PermissionService.desvincular_responsavel(paciente.id, professor_user.id)
        assert sucesso is True

        # Verificar que não pode mais acessar
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is False

    def test_compartilhar_paciente(self, db_session, terapeuta_user, professor_user, paciente):
        """Testa compartilhamento de paciente"""
        compartilhamento = PermissionService.compartilhar_paciente(
            paciente_id=paciente.id,
            compartilhou_user_id=terapeuta_user.id,
            recebeu_user_id=professor_user.id,
            tipo_acesso='leitura',
            motivo='Compartilhar para acompanhamento escolar'
        )

        assert compartilhamento is not None
        assert compartilhamento.ativo is True
        assert compartilhamento.tipo_acesso == 'leitura'

        # Professor agora pode acessar
        pode = PermissionService.pode_acessar_paciente(professor_user, paciente.id)
        assert pode is True

    def test_revogar_compartilhamento(self, db_session, terapeuta_user, professor_user, paciente):
        """Testa revogação de compartilhamento"""
        # Primeiro compartilhar
        compartilhamento = PermissionService.compartilhar_paciente(
            paciente.id, terapeuta_user.id, professor_user.id, 'leitura'
        )

        # Revogar
        sucesso = PermissionService.revogar_compartilhamento(compartilhamento.id)
        assert sucesso is True

        # Verificar que foi desativado
        db_session.refresh(compartilhamento)
        assert compartilhamento.ativo is False

    def test_registrar_acesso(self, db_session, terapeuta_user, paciente):
        """Testa registro de auditoria"""
        from app.models import AuditoriaAcesso

        # Registrar acesso
        PermissionService.registrar_acesso(
            terapeuta_user, 'paciente', paciente.id, 'visualizar'
        )

        # Verificar que foi criado
        auditoria = AuditoriaAcesso.query.filter_by(
            user_id=terapeuta_user.id,
            recurso_tipo='paciente',
            recurso_id=paciente.id,
            acao='visualizar'
        ).first()

        assert auditoria is not None


@pytest.mark.functional
class TestPermissionRoutes:
    """Testes das rotas de permissão"""

    def test_terapeuta_lista_apenas_seus_pacientes(self, logged_terapeuta, db_session, terapeuta_user, professor_user):
        """Terapeuta vê apenas seus pacientes na listagem"""
        # Criar paciente do terapeuta
        p1 = Paciente(nome='Meu Paciente', identificacao='P1',
                     data_nascimento='2015-01-01', sexo='M',
                     criador_id=terapeuta_user.id)
        # Criar paciente de outro
        p2 = Paciente(nome='Paciente de Outro', identificacao='P2',
                     data_nascimento='2015-01-01', sexo='M',
                     criador_id=professor_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        response = logged_terapeuta.get('/pacientes/')
        assert response.status_code == 200
        assert b'Meu Paciente' in response.data
        assert b'Paciente de Outro' not in response.data

    def test_admin_lista_todos_pacientes(self, logged_admin, db_session, terapeuta_user, professor_user):
        """Admin vê todos os pacientes"""
        # Criar pacientes de diferentes usuários
        p1 = Paciente(nome='Paciente 1', identificacao='P1',
                     data_nascimento='2015-01-01', sexo='M',
                     criador_id=terapeuta_user.id)
        p2 = Paciente(nome='Paciente 2', identificacao='P2',
                     data_nascimento='2015-01-01', sexo='M',
                     criador_id=professor_user.id)

        db_session.add_all([p1, p2])
        db_session.commit()

        response = logged_admin.get('/pacientes/')
        assert response.status_code == 200
        assert b'Paciente 1' in response.data
        assert b'Paciente 2' in response.data

    def test_acesso_negado_paciente_de_outro(self, logged_terapeuta, db_session, professor_user):
        """Acesso negado ao visualizar paciente de outro"""
        # Criar paciente de outro usuário
        paciente_outro = Paciente(
            nome='Paciente Proibido',
            identificacao='PROIBIDO',
            data_nascimento='2015-01-01',
            sexo='M',
            criador_id=professor_user.id
        )
        db_session.add(paciente_outro)
        db_session.commit()

        response = logged_terapeuta.get(f'/pacientes/{paciente_outro.id}')
        # Deve negar acesso ou redirecionar
        assert response.status_code in [302, 403]

    def test_vincular_responsavel_via_route(self, logged_terapeuta, db_session, paciente, professor_user):
        """Testa vinculação de responsável via rota"""
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/vincular',
            data={
                'user_id': professor_user.id,
                'tipo_vinculo': 'professor'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'vinculado' in response.data.lower() or b'sucesso' in response.data.lower()

    def test_compartilhar_paciente_via_route(self, logged_terapeuta, db_session, paciente, professor_user):
        """Testa compartilhamento via rota"""
        response = logged_terapeuta.post(
            f'/pacientes/{paciente.id}/compartilhar',
            data={
                'user_id': professor_user.id,
                'tipo_acesso': 'leitura',
                'motivo': 'Teste'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'compartilhado' in response.data.lower() or b'sucesso' in response.data.lower()
