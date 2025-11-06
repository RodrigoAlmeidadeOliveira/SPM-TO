"""
Modelo de Usuário
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """Modelo de Usuário do sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(200), nullable=False)

    # Tipo de usuário: admin, terapeuta, professor, familiar
    tipo = db.Column(db.String(20), nullable=False, default='terapeuta')

    # Status
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acesso = db.Column(db.DateTime)

    # Relacionamentos
    avaliacoes = db.relationship('Avaliacao', back_populates='avaliador', lazy='dynamic')

    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica a senha do usuário"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.tipo == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para Flask-Login"""
    return User.query.get(int(user_id))
