"""
Blueprint de Pacientes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.paciente import Paciente
from app.forms.paciente_forms import PacienteForm
from app import db

pacientes_bp = Blueprint('pacientes', __name__)


@pacientes_bp.route('/')
@login_required
def listar():
    """Lista pacientes"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Busca opcional
    busca = request.args.get('busca', '')
    query = Paciente.query.filter_by(ativo=True)

    if busca:
        query = query.filter(
            db.or_(
                Paciente.nome.ilike(f'%{busca}%'),
                Paciente.identificacao.ilike(f'%{busca}%')
            )
        )

    pacientes = query.order_by(Paciente.nome).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('pacientes/listar.html',
                          pacientes=pacientes,
                          busca=busca)


@pacientes_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Novo paciente"""
    form = PacienteForm()

    if form.validate_on_submit():
        paciente = Paciente(
            nome=form.nome.data,
            identificacao=form.identificacao.data if form.identificacao.data else None,
            data_nascimento=form.data_nascimento.data,
            sexo=form.sexo.data,
            raca_etnia=form.raca_etnia.data,
            observacoes=form.observacoes.data
        )

        db.session.add(paciente)
        db.session.commit()

        flash(f'Paciente {paciente.nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('pacientes.visualizar', id=paciente.id))

    return render_template('pacientes/form.html', form=form, titulo='Novo Paciente')


@pacientes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualizar paciente"""
    paciente = Paciente.query.get_or_404(id)

    # Calcular idade
    anos, meses = paciente.calcular_idade()

    # Obter avaliações
    avaliacoes = paciente.avaliacoes.order_by(db.desc('data_avaliacao')).all()

    return render_template('pacientes/visualizar.html',
                          paciente=paciente,
                          idade_anos=anos,
                          idade_meses=meses,
                          avaliacoes=avaliacoes)


@pacientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar paciente"""
    paciente = Paciente.query.get_or_404(id)
    form = PacienteForm(obj=paciente)

    if form.validate_on_submit():
        paciente.nome = form.nome.data
        paciente.identificacao = form.identificacao.data if form.identificacao.data else None
        paciente.data_nascimento = form.data_nascimento.data
        paciente.sexo = form.sexo.data
        paciente.raca_etnia = form.raca_etnia.data
        paciente.observacoes = form.observacoes.data

        db.session.commit()

        flash(f'Paciente {paciente.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('pacientes.visualizar', id=paciente.id))

    return render_template('pacientes/form.html',
                          form=form,
                          paciente=paciente,
                          titulo=f'Editar Paciente: {paciente.nome}')


@pacientes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir (desativar) paciente"""
    paciente = Paciente.query.get_or_404(id)

    # Soft delete - apenas desativa
    paciente.ativo = False
    db.session.commit()

    flash(f'Paciente {paciente.nome} removido com sucesso!', 'success')
    return redirect(url_for('pacientes.listar'))
