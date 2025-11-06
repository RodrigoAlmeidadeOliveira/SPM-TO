"""
Blueprint de Relatórios
"""
from flask import Blueprint, render_template
from flask_login import login_required

relatorios_bp = Blueprint('relatorios', __name__)


@relatorios_bp.route('/avaliacao/<int:id>')
@login_required
def avaliacao(id):
    """Relatório de avaliação"""
    return render_template('relatorios/avaliacao.html', avaliacao_id=id)


@relatorios_bp.route('/evolucao/<int:paciente_id>')
@login_required
def evolucao(paciente_id):
    """Relatório de evolução do paciente"""
    return render_template('relatorios/evolucao.html', paciente_id=paciente_id)


@relatorios_bp.route('/pei/<int:avaliacao_id>')
@login_required
def pei(avaliacao_id):
    """Relatório de PEI"""
    return render_template('relatorios/pei.html', avaliacao_id=avaliacao_id)
