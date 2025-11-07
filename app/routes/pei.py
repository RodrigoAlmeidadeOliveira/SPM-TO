"""
Rotas para o Sistema PEI (Plano Educacional Individualizado)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Avaliacao, Instrumento, Dominio, PlanoTemplateItem, PlanoItem
from app.forms.pei_forms import PlanoTemplateItemForm, PlanoItemSelecaoForm
from app.services.permission_service import PermissionService
from app.utils.decorators import can_view_avaliacao, can_edit_avaliacao

pei_bp = Blueprint('pei', __name__)


# ==================== ADMINISTRAÇÃO DE TEMPLATES ====================

@pei_bp.route('/templates')
@login_required
def listar_templates():
    """Lista todos os templates de itens PEI"""
    busca = request.args.get('busca', '').strip()
    instrumento_id = request.args.get('instrumento_id', type=int)
    dominio_id = request.args.get('dominio_id', type=int)
    page = request.args.get('page', 1, type=int)

    query = PlanoTemplateItem.query

    # Filtros
    if busca:
        query = query.filter(PlanoTemplateItem.texto.ilike(f'%{busca}%'))

    if instrumento_id:
        query = query.filter_by(instrumento_id=instrumento_id)

    if dominio_id:
        query = query.filter_by(dominio_id=dominio_id)

    # Ordenar e paginar
    query = query.order_by(PlanoTemplateItem.instrumento_id, PlanoTemplateItem.ordem)
    paginacao = query.paginate(page=page, per_page=20, error_out=False)

    # Listas para filtros
    instrumentos = Instrumento.query.filter_by(ativo=True).order_by(Instrumento.nome).all()
    dominios = Dominio.query.order_by(Dominio.nome).all()

    return render_template('pei/templates_listar.html',
                         templates=paginacao.items,
                         paginacao=paginacao,
                         instrumentos=instrumentos,
                         dominios=dominios,
                         busca=busca,
                         instrumento_id=instrumento_id,
                         dominio_id=dominio_id)


@pei_bp.route('/templates/novo', methods=['GET', 'POST'])
@login_required
def novo_template():
    """Cadastra novo template de item PEI"""
    form = PlanoTemplateItemForm()

    # Popular choices
    form.instrumento_id.choices = [(0, 'Selecione...')] + [
        (i.id, i.nome) for i in Instrumento.query.filter_by(ativo=True).order_by(Instrumento.nome).all()
    ]

    form.dominio_id.choices = [(0, 'Geral (sem domínio específico)')] + [
        (d.id, f"{d.instrumento.nome} - {d.nome}")
        for d in Dominio.query.join(Instrumento).order_by(Instrumento.nome, Dominio.ordem).all()
    ]

    if form.validate_on_submit():
        try:
            template = PlanoTemplateItem(
                instrumento_id=form.instrumento_id.data,
                dominio_id=form.dominio_id.data if form.dominio_id.data != 0 else None,
                ordem=form.ordem.data,
                texto=form.texto.data.strip(),
                ativo=form.ativo.data
            )

            db.session.add(template)
            db.session.commit()

            flash('Template PEI cadastrado com sucesso!', 'success')
            return redirect(url_for('pei.listar_templates'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar template: {str(e)}', 'danger')

    return render_template('pei/template_form.html', form=form, titulo='Novo Template PEI')


@pei_bp.route('/templates/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_template(id):
    """Edita template de item PEI existente"""
    template = PlanoTemplateItem.query.get_or_404(id)
    form = PlanoTemplateItemForm(obj=template)

    # Popular choices
    form.instrumento_id.choices = [(0, 'Selecione...')] + [
        (i.id, i.nome) for i in Instrumento.query.filter_by(ativo=True).order_by(Instrumento.nome).all()
    ]

    form.dominio_id.choices = [(0, 'Geral (sem domínio específico)')] + [
        (d.id, f"{d.instrumento.nome} - {d.nome}")
        for d in Dominio.query.join(Instrumento).order_by(Instrumento.nome, Dominio.ordem).all()
    ]

    if form.validate_on_submit():
        try:
            template.instrumento_id = form.instrumento_id.data
            template.dominio_id = form.dominio_id.data if form.dominio_id.data != 0 else None
            template.ordem = form.ordem.data
            template.texto = form.texto.data.strip()
            template.ativo = form.ativo.data

            db.session.commit()

            flash('Template PEI atualizado com sucesso!', 'success')
            return redirect(url_for('pei.listar_templates'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar template: {str(e)}', 'danger')

    # Preencher formulário na primeira carga
    if request.method == 'GET':
        form.dominio_id.data = template.dominio_id if template.dominio_id else 0

    return render_template('pei/template_form.html',
                         form=form,
                         titulo='Editar Template PEI',
                         template=template)


@pei_bp.route('/templates/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_template(id):
    """Exclui template de item PEI"""
    template = PlanoTemplateItem.query.get_or_404(id)

    try:
        # Verificar se há itens usando este template
        itens_usando = PlanoItem.query.filter_by(template_item_id=id).count()

        if itens_usando > 0:
            flash(f'Não é possível excluir: este template está sendo usado em {itens_usando} plano(s).', 'warning')
        else:
            db.session.delete(template)
            db.session.commit()
            flash('Template PEI excluído com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir template: {str(e)}', 'danger')

    return redirect(url_for('pei.listar_templates'))


# ==================== GERAÇÃO DE PEI PARA AVALIAÇÃO ====================

@pei_bp.route('/avaliacao/<int:avaliacao_id>')
@login_required
@can_view_avaliacao
def visualizar_pei(avaliacao_id):
    """Visualiza o PEI gerado para uma avaliação"""
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    # Buscar itens do PEI
    itens_pei = PlanoItem.query.filter_by(
        avaliacao_id=avaliacao_id,
        selecionado=True
    ).join(PlanoTemplateItem).order_by(PlanoTemplateItem.ordem).all()

    return render_template('pei/visualizar.html',
                         avaliacao=avaliacao,
                         itens_pei=itens_pei)


@pei_bp.route('/avaliacao/<int:avaliacao_id>/selecionar', methods=['GET', 'POST'])
@login_required
@can_edit_avaliacao
def selecionar_itens(avaliacao_id):
    """Interface para selecionar itens do PEI baseado na avaliação"""
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    # Verificar se avaliação está concluída
    if avaliacao.status != 'concluida':
        flash('Só é possível gerar PEI para avaliações concluídas.', 'warning')
        return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))

    # Buscar templates aplicáveis ao instrumento da avaliação
    templates = PlanoTemplateItem.query.filter_by(
        instrumento_id=avaliacao.instrumento_id,
        ativo=True
    ).order_by(PlanoTemplateItem.ordem).all()

    if not templates:
        flash('Não há templates cadastrados para este instrumento. Cadastre templates primeiro.', 'warning')
        return redirect(url_for('pei.listar_templates'))

    # Buscar itens já selecionados
    itens_existentes = {
        item.template_item_id: item
        for item in PlanoItem.query.filter_by(avaliacao_id=avaliacao_id).all()
    }

    # Processar seleção
    if request.method == 'POST':
        try:
            # Obter IDs selecionados
            selecionados = request.form.getlist('itens_selecionados', type=int)
            observacoes_dict = {}

            # Obter observações de cada item
            for template_id in selecionados:
                obs = request.form.get(f'observacoes_{template_id}', '').strip()
                if obs:
                    observacoes_dict[template_id] = obs

            # Atualizar ou criar itens
            for template in templates:
                selecionado = template.id in selecionados

                if template.id in itens_existentes:
                    # Atualizar existente
                    item = itens_existentes[template.id]
                    item.selecionado = selecionado
                    item.observacoes = observacoes_dict.get(template.id, item.observacoes)
                else:
                    # Criar novo
                    item = PlanoItem(
                        avaliacao_id=avaliacao_id,
                        template_item_id=template.id,
                        selecionado=selecionado,
                        observacoes=observacoes_dict.get(template.id)
                    )
                    db.session.add(item)

            db.session.commit()

            # Registrar na auditoria
            PermissionService.registrar_acesso(
                current_user, 'pei', avaliacao_id, 'gerar_pei'
            )

            flash('PEI gerado com sucesso!', 'success')
            return redirect(url_for('pei.visualizar_pei', avaliacao_id=avaliacao_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao gerar PEI: {str(e)}', 'danger')

    # Agrupar templates por domínio
    templates_por_dominio = {}
    for template in templates:
        dominio_nome = template.dominio_nome
        if dominio_nome not in templates_por_dominio:
            templates_por_dominio[dominio_nome] = []
        templates_por_dominio[dominio_nome].append(template)

    return render_template('pei/selecionar.html',
                         avaliacao=avaliacao,
                         templates_por_dominio=templates_por_dominio,
                         itens_existentes=itens_existentes)


@pei_bp.route('/avaliacao/<int:avaliacao_id>/sugerir-itens')
@login_required
@can_view_avaliacao
def sugerir_itens(avaliacao_id):
    """API: Sugere itens do PEI baseado nas classificações da avaliação"""
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    # Identificar domínios com disfunção
    dominios_afetados = []

    dominios_map = {
        'SOC': (avaliacao.classificacao_soc, 'Participação Social'),
        'VIS': (avaliacao.classificacao_vis, 'Visão'),
        'HEA': (avaliacao.classificacao_hea, 'Audição'),
        'TOU': (avaliacao.classificacao_tou, 'Tato'),
        'BOD': (avaliacao.classificacao_bod, 'Consciência Corporal'),
        'BAL': (avaliacao.classificacao_bal, 'Equilíbrio'),
        'PLA': (avaliacao.classificacao_pla, 'Planejamento'),
        'OLF': (avaliacao.classificacao_olf, 'Olfato/Paladar')
    }

    for codigo, (classificacao, nome) in dominios_map.items():
        if classificacao in ['PROVAVEL_DISFUNCAO', 'DISFUNCAO_DEFINITIVA']:
            # Buscar domínio no banco
            dominio = Dominio.query.filter_by(
                instrumento_id=avaliacao.instrumento_id,
                codigo=codigo
            ).first()

            if dominio:
                dominios_afetados.append(dominio.id)

    # Buscar templates para os domínios afetados
    templates_sugeridos = PlanoTemplateItem.query.filter(
        PlanoTemplateItem.instrumento_id == avaliacao.instrumento_id,
        PlanoTemplateItem.ativo == True,
        or_(
            PlanoTemplateItem.dominio_id.in_(dominios_afetados),
            PlanoTemplateItem.dominio_id.is_(None)  # Incluir itens gerais
        )
    ).order_by(PlanoTemplateItem.ordem).all()

    return jsonify({
        'success': True,
        'sugeridos': [t.id for t in templates_sugeridos],
        'dominios_afetados': len(dominios_afetados)
    })


@pei_bp.route('/avaliacao/<int:avaliacao_id>/pdf')
@login_required
@can_view_avaliacao
def gerar_pdf(avaliacao_id):
    """Gera relatório PDF do PEI"""
    from app.services.pei_pdf_service import PeiPDFService

    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    # Buscar itens selecionados
    itens_pei = PlanoItem.query.filter_by(
        avaliacao_id=avaliacao_id,
        selecionado=True
    ).join(PlanoTemplateItem).order_by(PlanoTemplateItem.ordem).all()

    if not itens_pei:
        flash('Nenhum item do PEI foi selecionado para esta avaliação.', 'warning')
        return redirect(url_for('pei.visualizar_pei', avaliacao_id=avaliacao_id))

    try:
        pdf_buffer = PeiPDFService.gerar_relatorio_pei(avaliacao, itens_pei)

        # Registrar na auditoria
        PermissionService.registrar_acesso(
            current_user, 'pei', avaliacao_id, 'exportar_pdf'
        )

        from flask import send_file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'PEI_{avaliacao.paciente.nome}_{avaliacao.data_avaliacao.strftime("%Y%m%d")}.pdf'
        )

    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        return redirect(url_for('pei.visualizar_pei', avaliacao_id=avaliacao_id))
