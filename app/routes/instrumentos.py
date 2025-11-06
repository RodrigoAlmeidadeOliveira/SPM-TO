"""
Blueprint de Instrumentos
"""
from flask import Blueprint, render_template
from flask_login import login_required

instrumentos_bp = Blueprint('instrumentos', __name__)


@instrumentos_bp.route('/')
@login_required
def listar():
    """Lista instrumentos"""
    return render_template('instrumentos/listar.html')


@instrumentos_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualizar instrumento"""
    return render_template('instrumentos/visualizar.html', instrumento_id=id)


@instrumentos_bp.route('/<int:id>/questoes', methods=['GET', 'POST'])
@login_required
def gerenciar_questoes(id):
    """Gerenciar questões do instrumento"""
    return render_template('instrumentos/questoes.html', instrumento_id=id)
