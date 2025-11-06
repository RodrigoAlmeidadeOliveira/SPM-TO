"""
Rotas para gerenciamento de instrumentos SPM
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import or_, func

from app import db
from app.forms import InstrumentoForm, DominioForm, QuestaoForm
from app.models import Instrumento, Dominio, Questao

instrumentos_bp = Blueprint('instrumentos', __name__)


@instrumentos_bp.route('/')
@login_required
def listar():
    """Lista instrumentos cadastrados com filtros básicos"""
    busca = request.args.get('busca', '').strip()
    contexto = request.args.get('contexto', '').strip()
    status = request.args.get('status', 'ativo').strip()

    query = Instrumento.query

    if busca:
        like = f'%{busca}%'
        query = query.filter(or_(Instrumento.nome.ilike(like),
                                 Instrumento.codigo.ilike(like)))

    if contexto in ('casa', 'escola'):
        query = query.filter(Instrumento.contexto == contexto)

    if status == 'ativo':
        query = query.filter(Instrumento.ativo.is_(True))
    elif status == 'inativo':
        query = query.filter(Instrumento.ativo.is_(False))

    instrumentos = query.order_by(Instrumento.nome.asc()).all()

    return render_template(
        'instrumentos/listar.html',
        instrumentos=instrumentos,
        busca=busca,
        contexto=contexto,
        status=status
    )


@instrumentos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastro de novo instrumento"""
    form = InstrumentoForm()

    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        form.codigo.data = codigo

        if Instrumento.query.filter_by(codigo=codigo).first():
            form.codigo.errors.append('Já existe um instrumento com este código.')
        else:
            instrumento = Instrumento(
                codigo=codigo,
                nome=form.nome.data.strip(),
                contexto=form.contexto.data,
                idade_minima=form.idade_minima.data,
                idade_maxima=form.idade_maxima.data,
                instrucoes=form.instrucoes.data.strip() if form.instrucoes.data else None,
                ativo=form.ativo.data
            )
            db.session.add(instrumento)
            db.session.commit()

            flash('Instrumento cadastrado com sucesso!', 'success')
            return redirect(url_for('instrumentos.visualizar', id=instrumento.id))

    return render_template('instrumentos/form.html', form=form, titulo='Novo Instrumento')


@instrumentos_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Detalhes de um instrumento"""
    instrumento = Instrumento.query.get_or_404(id)
    dominios = instrumento.dominios.order_by(Dominio.ordem).all()

    return render_template(
        'instrumentos/visualizar.html',
        instrumento=instrumento,
        dominios=dominios
    )


@instrumentos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edição de instrumento existente"""
    instrumento = Instrumento.query.get_or_404(id)
    form = InstrumentoForm(obj=instrumento)

    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        form.codigo.data = codigo
        existente = Instrumento.query.filter(Instrumento.codigo == codigo,
                                             Instrumento.id != instrumento.id).first()
        if existente:
            form.codigo.errors.append('Já existe outro instrumento com este código.')
        else:
            instrumento.codigo = codigo
            instrumento.nome = form.nome.data.strip()
            instrumento.contexto = form.contexto.data
            instrumento.idade_minima = form.idade_minima.data
            instrumento.idade_maxima = form.idade_maxima.data
            instrumento.instrucoes = form.instrucoes.data.strip() if form.instrucoes.data else None
            instrumento.ativo = form.ativo.data

            db.session.commit()
            flash('Instrumento atualizado com sucesso!', 'success')
            return redirect(url_for('instrumentos.visualizar', id=instrumento.id))

    else:
        if request.method == 'GET':
            form.codigo.data = instrumento.codigo

    return render_template(
        'instrumentos/form.html',
        form=form,
        titulo=f'Editar Instrumento: {instrumento.nome}'
    )


@instrumentos_bp.route('/<int:instrumento_id>/dominios/novo', methods=['GET', 'POST'])
@login_required
def novo_dominio(instrumento_id):
    """Cadastro de domínio vinculado a um instrumento"""
    instrumento = Instrumento.query.get_or_404(instrumento_id)
    form = DominioForm()

    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        form.codigo.data = codigo

        if instrumento.dominios.filter(func.upper(Dominio.codigo) == codigo).first():
            form.codigo.errors.append('Já existe um domínio com este código para o instrumento.')
        elif instrumento.dominios.filter(Dominio.ordem == form.ordem.data).first():
            form.ordem.errors.append('Já existe um domínio com esta ordem para o instrumento.')
        else:
            dominio = Dominio(
                instrumento_id=instrumento.id,
                codigo=codigo,
                nome=form.nome.data.strip(),
                ordem=form.ordem.data,
                escala_invertida=form.escala_invertida.data
            )
            db.session.add(dominio)
            db.session.commit()

            flash('Domínio cadastrado com sucesso!', 'success')
            return redirect(url_for('instrumentos.visualizar', id=instrumento.id))

    return render_template(
        'instrumentos/dominio_form.html',
        form=form,
        instrumento=instrumento,
        titulo='Novo Domínio'
    )


@instrumentos_bp.route('/dominios/<int:dominio_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_dominio(dominio_id):
    """Edição de um domínio existente"""
    dominio = Dominio.query.get_or_404(dominio_id)
    instrumento = dominio.instrumento
    form = DominioForm(obj=dominio)

    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        form.codigo.data = codigo

        existente_codigo = instrumento.dominios.filter(
            func.upper(Dominio.codigo) == codigo,
            Dominio.id != dominio.id
        ).first()
        existente_ordem = instrumento.dominios.filter(
            Dominio.ordem == form.ordem.data,
            Dominio.id != dominio.id
        ).first()

        if existente_codigo:
            form.codigo.errors.append('Já existe outro domínio com este código.')
        elif existente_ordem:
            form.ordem.errors.append('Já existe outro domínio com esta ordem.')
        else:
            dominio.codigo = codigo
            dominio.nome = form.nome.data.strip()
            dominio.ordem = form.ordem.data
            dominio.escala_invertida = form.escala_invertida.data

            db.session.commit()
            flash('Domínio atualizado com sucesso!', 'success')
            return redirect(url_for('instrumentos.visualizar', id=instrumento.id))

    else:
        if request.method == 'GET':
            form.codigo.data = dominio.codigo

    return render_template(
        'instrumentos/dominio_form.html',
        form=form,
        instrumento=instrumento,
        titulo=f'Editar Domínio: {dominio.nome}'
    )


@instrumentos_bp.route('/dominios/<int:dominio_id>/questoes/novo', methods=['GET', 'POST'])
@login_required
def nova_questao(dominio_id):
    """Cadastro de nova questão dentro de um domínio"""
    dominio = Dominio.query.get_or_404(dominio_id)
    instrumento = dominio.instrumento
    form = QuestaoForm()

    if form.validate_on_submit():
        numero = form.numero.data
        numero_global = form.numero_global.data

        existente_dom = dominio.questoes.filter(Questao.numero == numero).first()
        existente_global = Questao.query.join(Dominio).filter(
            Dominio.instrumento_id == instrumento.id,
            Questao.numero_global == numero_global
        ).first()

        if existente_dom:
            form.numero.errors.append('Já existe uma questão com este número neste domínio.')
        elif existente_global:
            form.numero_global.errors.append('Já existe uma questão com este número global para o instrumento.')
        else:
            questao = Questao(
                dominio_id=dominio.id,
                numero=numero,
                numero_global=numero_global,
                texto=form.texto.data.strip(),
                ativo=form.ativo.data
            )
            db.session.add(questao)
            db.session.commit()

            flash('Questão cadastrada com sucesso!', 'success')
            return redirect(url_for('instrumentos.listar_questoes', id=instrumento.id))

    return render_template(
        'instrumentos/questao_form.html',
        form=form,
        instrumento=instrumento,
        dominio=dominio,
        titulo='Nova Questão'
    )


@instrumentos_bp.route('/questoes/<int:questao_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_questao(questao_id):
    """Edição de questão existente"""
    questao = Questao.query.get_or_404(questao_id)
    dominio = questao.dominio
    instrumento = dominio.instrumento
    form = QuestaoForm(obj=questao)

    if form.validate_on_submit():
        numero = form.numero.data
        numero_global = form.numero_global.data

        existente_dom = dominio.questoes.filter(
            Questao.numero == numero,
            Questao.id != questao.id
        ).first()
        existente_global = Questao.query.join(Dominio).filter(
            Dominio.instrumento_id == instrumento.id,
            Questao.numero_global == numero_global,
            Questao.id != questao.id
        ).first()

        if existente_dom:
            form.numero.errors.append('Já existe outra questão com este número neste domínio.')
        elif existente_global:
            form.numero_global.errors.append('Já existe outra questão com este número global para o instrumento.')
        else:
            questao.numero = numero
            questao.numero_global = numero_global
            questao.texto = form.texto.data.strip()
            questao.ativo = form.ativo.data

            db.session.commit()
            flash('Questão atualizada com sucesso!', 'success')
            return redirect(url_for('instrumentos.listar_questoes', id=instrumento.id))

    return render_template(
        'instrumentos/questao_form.html',
        form=form,
        instrumento=instrumento,
        dominio=dominio,
        titulo=f'Editar Questão #{questao.numero_global}'
    )


@instrumentos_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def alterar_status(id):
    """Ativa ou desativa um instrumento"""
    instrumento = Instrumento.query.get_or_404(id)
    instrumento.ativo = not instrumento.ativo
    db.session.commit()

    mensagem = 'Instrumento ativado com sucesso!' if instrumento.ativo else 'Instrumento desativado com sucesso!'
    flash(mensagem, 'success')

    proxima = request.args.get('next')
    if proxima:
        return redirect(proxima)

    return redirect(url_for('instrumentos.visualizar', id=instrumento.id))


@instrumentos_bp.route('/<int:id>/questoes')
@login_required
def listar_questoes(id):
    """Lista questões de um instrumento agrupadas por domínio"""
    instrumento = Instrumento.query.get_or_404(id)
    dominios = instrumento.dominios.order_by(Dominio.ordem).all()
    dominios_detalhes = [
        {
            'dominio': dominio,
            'questoes': dominio.questoes.order_by(Questao.numero.asc()).all()
        }
        for dominio in dominios
    ]

    return render_template(
        'instrumentos/questoes.html',
        instrumento=instrumento,
        dominios=dominios_detalhes
    )
