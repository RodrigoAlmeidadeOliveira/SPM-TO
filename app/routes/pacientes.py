"""
Blueprint de Pacientes
"""
from flask import Blueprint, render_template
from flask_login import login_required

pacientes_bp = Blueprint('pacientes', __name__)


@pacientes_bp.route('/')
@login_required
def listar():
    """Lista pacientes"""
    return render_template('pacientes/listar.html')


@pacientes_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Novo paciente"""
    return render_template('pacientes/form.html')


@pacientes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualizar paciente"""
    return render_template('pacientes/visualizar.html', paciente_id=id)
