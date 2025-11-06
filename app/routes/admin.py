"""
Blueprint de Administração
"""
from flask import Blueprint, render_template
from flask_login import login_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
def dashboard():
    """Dashboard administrativo"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/usuarios')
@login_required
def usuarios():
    """Gerenciar usuários"""
    return render_template('admin/usuarios.html')


@admin_bp.route('/configuracoes')
@login_required
def configuracoes():
    """Configurações do sistema"""
    return render_template('admin/configuracoes.html')
