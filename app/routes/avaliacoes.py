"""
Blueprint de Avaliações
"""
from flask import Blueprint, render_template
from flask_login import login_required

avaliacoes_bp = Blueprint('avaliacoes', __name__)


@avaliacoes_bp.route('/')
@login_required
def listar():
    """Lista avaliações"""
    return render_template('avaliacoes/listar.html')


@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Nova avaliação"""
    return render_template('avaliacoes/form.html')


@avaliacoes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualizar avaliação"""
    return render_template('avaliacoes/visualizar.html', avaliacao_id=id)


@avaliacoes_bp.route('/<int:id>/responder', methods=['GET', 'POST'])
@login_required
def responder(id):
    """Responder avaliação"""
    return render_template('avaliacoes/responder.html', avaliacao_id=id)
