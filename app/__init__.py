"""
Application Factory para SPM-TO
Implementa o padrão Application Factory para criar instâncias da aplicação Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import os

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """
    Application Factory Pattern

    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Configuração
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from app.config import config
    app.config.from_object(config[config_name])

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Registrar blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.pacientes import pacientes_bp
    from app.routes.avaliacoes import avaliacoes_bp
    from app.routes.instrumentos import instrumentos_bp
    from app.routes.relatorios import relatorios_bp
    from app.routes.admin import admin_bp
    from app.routes.anexos import anexos_bp
    from app.routes.pei import pei_bp
    from app.routes.prontuario import prontuario_bp
    from app.routes.atendimento import atendimento_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(pacientes_bp, url_prefix='/pacientes')
    app.register_blueprint(avaliacoes_bp, url_prefix='/avaliacoes')
    app.register_blueprint(instrumentos_bp, url_prefix='/instrumentos')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(anexos_bp, url_prefix='/anexos')
    app.register_blueprint(pei_bp, url_prefix='/pei')
    app.register_blueprint(prontuario_bp, url_prefix='/prontuario')
    app.register_blueprint(atendimento_bp, url_prefix='/atendimento')

    # Contexto do template
    @app.context_processor
    def inject_globals():
        """Injeta variáveis globais nos templates"""
        return {
            'app_name': 'SPM-TO',
            'app_version': '1.0.0'
        }

    @app.context_processor
    def inject_csrf_token():
        """Disponibiliza função para geração de tokens CSRF em formulários manuais"""
        return {
            'csrf_token': generate_csrf
        }

    # Criar diretórios necessários
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
