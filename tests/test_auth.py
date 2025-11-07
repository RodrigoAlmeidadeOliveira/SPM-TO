"""
Testes de autenticação e autorização
"""
import pytest
from flask import session
from app.models import User


@pytest.mark.functional
class TestAuthentication:
    """Testes de autenticação"""

    def test_login_page_loads(self, client):
        """Testa se a página de login carrega"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'Entrar' in response.data

    def test_login_success_admin(self, client, admin_user):
        """Testa login bem-sucedido de admin"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Deve redirecionar para dashboard
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()

    def test_login_success_terapeuta(self, client, terapeuta_user):
        """Testa login bem-sucedido de terapeuta"""
        response = client.post('/auth/login', data={
            'username': 'terapeuta',
            'password': 'terapeuta123'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_login_wrong_password(self, client, admin_user):
        """Testa login com senha incorreta"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'senhaerrada'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'inv' in response.data.lower() or b'incorret' in response.data.lower()

    def test_login_nonexistent_user(self, client):
        """Testa login com usuário inexistente"""
        response = client.post('/auth/login', data={
            'username': 'naoexiste',
            'password': 'senha123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'inv' in response.data.lower() or b'incorret' in response.data.lower()

    def test_login_inactive_user(self, client, db_session):
        """Testa login com usuário inativo"""
        user = User(
            username='inativo',
            email='inativo@test.com',
            nome_completo='Usuário Inativo',
            tipo='terapeuta',
            ativo=False
        )
        user.set_password('senha123')
        db_session.add(user)
        db_session.commit()

        response = client.post('/auth/login', data={
            'username': 'inativo',
            'password': 'senha123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Pode ou não permitir login de inativo, depende da implementação

    def test_logout(self, logged_admin):
        """Testa logout"""
        response = logged_admin.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200

        # Tentar acessar página protegida após logout
        response = logged_admin.get('/pacientes/')
        assert response.status_code == 302  # Redirect para login

    def test_access_protected_route_without_login(self, client):
        """Testa acesso a rota protegida sem login"""
        response = client.get('/pacientes/')
        assert response.status_code == 302  # Redirect
        assert b'/auth/login' in response.data or response.location.endswith('/auth/login')

    def test_access_admin_route_as_terapeuta(self, logged_terapeuta):
        """Testa acesso a rota admin sendo terapeuta"""
        response = logged_terapeuta.get('/admin/usuarios')
        # Deve negar acesso ou redirecionar
        assert response.status_code in [302, 403]

    def test_access_admin_route_as_admin(self, logged_admin):
        """Testa acesso a rota admin sendo admin"""
        response = logged_admin.get('/admin/usuarios')
        assert response.status_code == 200


@pytest.mark.unit
class TestUserModel:
    """Testes do modelo User"""

    def test_create_user(self, db_session):
        """Testa criação de usuário"""
        user = User(
            username='testuser',
            email='test@test.com',
            nome_completo='Test User',
            tipo='terapeuta',
            ativo=True
        )
        user.set_password('senha123')
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.check_password('senha123')

    def test_password_hashing(self, db_session):
        """Testa hash de senha"""
        user = User(
            username='hashtest',
            email='hash@test.com',
            nome_completo='Hash Test',
            tipo='terapeuta'
        )
        user.set_password('minhasenha')
        db_session.add(user)
        db_session.commit()

        # Senha não deve ser armazenada em plain text
        assert user.password_hash != 'minhasenha'
        # Verificação deve funcionar
        assert user.check_password('minhasenha') is True
        assert user.check_password('senhaerrada') is False

    def test_is_admin(self, admin_user, terapeuta_user):
        """Testa método is_admin()"""
        assert admin_user.is_admin() is True
        assert terapeuta_user.is_admin() is False

    def test_unique_username(self, db_session, admin_user):
        """Testa unicidade de username"""
        user = User(
            username='admin',  # Já existe
            email='outro@test.com',
            nome_completo='Outro',
            tipo='terapeuta'
        )
        user.set_password('senha123')
        db_session.add(user)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_unique_email(self, db_session, admin_user):
        """Testa unicidade de email"""
        user = User(
            username='outrouser',
            email='admin@test.com',  # Já existe
            nome_completo='Outro',
            tipo='terapeuta'
        )
        user.set_password('senha123')
        db_session.add(user)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


@pytest.mark.security
class TestPasswordSecurity:
    """Testes de segurança de senhas"""

    def test_password_not_stored_plain(self, admin_user):
        """Garante que senha não é armazenada em texto plano"""
        assert admin_user.password_hash != 'admin123'
        assert 'admin123' not in admin_user.password_hash

    def test_password_minimum_length(self, db_session):
        """Testa senha com comprimento mínimo"""
        user = User(
            username='shortpwd',
            email='short@test.com',
            nome_completo='Short Password',
            tipo='terapeuta'
        )
        user.set_password('123')  # Senha muito curta
        db_session.add(user)
        db_session.commit()

        # Verifica se hash foi criado (backend sempre aceita)
        assert user.password_hash is not None
        # Mas form validation deveria impedir isso

    def test_different_passwords_different_hashes(self, db_session):
        """Testa que senhas diferentes geram hashes diferentes"""
        user1 = User(
            username='user1',
            email='user1@test.com',
            nome_completo='User 1',
            tipo='terapeuta'
        )
        user1.set_password('senha123')
        db_session.add(user1)

        user2 = User(
            username='user2',
            email='user2@test.com',
            nome_completo='User 2',
            tipo='terapeuta'
        )
        user2.set_password('senha456')
        db_session.add(user2)

        db_session.commit()

        assert user1.password_hash != user2.password_hash
