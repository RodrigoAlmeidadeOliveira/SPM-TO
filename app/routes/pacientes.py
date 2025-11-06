"""
Rotas para gerenciamento de pacientes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import or_

from app import db
from app.forms import PacienteForm
from app.models import Paciente, Avaliacao


pacientes_bp = Blueprint('pacientes', __name__)


@pacientes_bp.route('/')
@login_required
def listar():
    """Lista todos os pacientes com busca e filtros"""
    busca = request.args.get('busca', '').strip()
    sexo_filtro = request.args.get('sexo', '').strip()
    ativo_filtro = request.args.get('ativo', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = Paciente.query

    if busca:
        query = query.filter(
            or_(
                Paciente.nome.ilike(f'%{busca}%'),
                Paciente.identificacao.ilike(f'%{busca}%')
            )
        )

    if sexo_filtro and sexo_filtro in ['M', 'F', 'O']:
        query = query.filter(Paciente.sexo == sexo_filtro)

    if ativo_filtro == 'true':
        query = query.filter(Paciente.ativo.is_(True))
    elif ativo_filtro == 'false':
        query = query.filter(Paciente.ativo.is_(False))

    query = query.order_by(Paciente.nome)

    paginacao = query.paginate(page=page, per_page=per_page, error_out=False)
    pacientes = paginacao.items

    for paciente in pacientes:
        idade_anos, idade_meses = paciente.calcular_idade()
        paciente.idade = idade_anos
        paciente.idade_meses = idade_meses
        paciente.num_avaliacoes = Avaliacao.query.filter_by(paciente_id=paciente.id).count()

    return render_template(
        'pacientes/listar.html',
        pacientes=pacientes,
        paginacao=paginacao,
        busca=busca,
        sexo_filtro=sexo_filtro,
        ativo_filtro=ativo_filtro
    )


@pacientes_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cria um novo paciente"""
    form = PacienteForm()

    if form.validate_on_submit():
        try:
            paciente_existente = Paciente.query.filter_by(
                identificacao=form.identificacao.data
            ).first()

            if paciente_existente:
                flash('Já existe um paciente com esta identificação!', 'danger')
                return render_template('pacientes/form.html', form=form, titulo='Novo Paciente')

            paciente = Paciente(
                nome=form.nome.data,
                identificacao=form.identificacao.data,
                data_nascimento=form.data_nascimento.data,
                sexo=form.sexo.data,
                raca_etnia=form.raca_etnia.data if form.raca_etnia.data else None,
                observacoes=form.observacoes.data,
                ativo=form.ativo.data
            )

            db.session.add(paciente)
            db.session.commit()

            flash(f'Paciente {paciente.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('pacientes.visualizar', id=paciente.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'danger')

    return render_template('pacientes/form.html', form=form, titulo='Novo Paciente')


@pacientes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza detalhes de um paciente"""
    paciente = Paciente.query.get_or_404(id)

    idade_anos, idade_meses = paciente.calcular_idade()
    instrumento_adequado = paciente.get_instrumento_adequado()

    avaliacoes = Avaliacao.query.filter_by(paciente_id=id).order_by(
        Avaliacao.data_avaliacao.desc()
    ).all()

    total_avaliacoes = len(avaliacoes)
    avaliacoes_concluidas = sum(1 for a in avaliacoes if a.status == 'concluida')
    avaliacoes_andamento = sum(1 for a in avaliacoes if a.status == 'em_andamento')

    return render_template(
        'pacientes/visualizar.html',
        paciente=paciente,
        idade_anos=idade_anos,
        idade_meses=idade_meses,
        instrumento_adequado=instrumento_adequado,
        avaliacoes=avaliacoes,
        total_avaliacoes=total_avaliacoes,
        avaliacoes_concluidas=avaliacoes_concluidas,
        avaliacoes_andamento=avaliacoes_andamento
    )


@pacientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um paciente existente"""
    paciente = Paciente.query.get_or_404(id)
    form = PacienteForm(obj=paciente)

    if form.validate_on_submit():
        try:
            if form.identificacao.data != paciente.identificacao:
                paciente_existente = Paciente.query.filter_by(
                    identificacao=form.identificacao.data
                ).first()

                if paciente_existente:
                    flash('Já existe outro paciente com esta identificação!', 'danger')
                    return render_template(
                        'pacientes/form.html',
                        form=form,
                        titulo=f'Editar Paciente: {paciente.nome}',
                        paciente=paciente
                    )

            paciente.nome = form.nome.data
            paciente.identificacao = form.identificacao.data
            paciente.data_nascimento = form.data_nascimento.data
            paciente.sexo = form.sexo.data
            paciente.raca_etnia = form.raca_etnia.data if form.raca_etnia.data else None
            paciente.observacoes = form.observacoes.data
            paciente.ativo = form.ativo.data

            db.session.commit()

            flash(f'Paciente {paciente.nome} atualizado com sucesso!', 'success')
            return redirect(url_for('pacientes.visualizar', id=paciente.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar paciente: {str(e)}', 'danger')

    return render_template(
        'pacientes/form.html',
        form=form,
        titulo=f'Editar Paciente: {paciente.nome}',
        paciente=paciente
    )


@pacientes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui (desativa) um paciente"""
    paciente = Paciente.query.get_or_404(id)

    try:
        num_avaliacoes = Avaliacao.query.filter_by(paciente_id=id).count()

        if num_avaliacoes > 0:
            paciente.ativo = False
            db.session.commit()
            flash(
                f'Paciente {paciente.nome} desativado com sucesso! '
                f'({num_avaliacoes} avaliação(ões) mantida(s))',
                'warning'
            )
        else:
            nome = paciente.nome
            db.session.delete(paciente)
            db.session.commit()
            flash(f'Paciente {nome} excluído permanentemente!', 'success')

        return redirect(url_for('pacientes.listar'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir paciente: {str(e)}', 'danger')
        return redirect(url_for('pacientes.visualizar', id=id))


@pacientes_bp.route('/<int:id>/reativar', methods=['POST'])
@login_required
def reativar(id):
    """Reativa um paciente desativado"""
    paciente = Paciente.query.get_or_404(id)

    try:
        paciente.ativo = True
        db.session.commit()
        flash(f'Paciente {paciente.nome} reativado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar paciente: {str(e)}', 'danger')

    return redirect(url_for('pacientes.visualizar', id=id))
