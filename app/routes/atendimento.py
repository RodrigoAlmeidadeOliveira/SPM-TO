"""
Rotas para gerenciamento de Atendimentos (Sessões Terapêuticas)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import json

from app import db
from app.forms import AtendimentoForm, FinalizarAtendimentoForm
from app.models import Atendimento, Paciente, Prontuario, Avaliacao, AuditoriaAcesso
from app.services.permission_service import PermissionService
from app.utils.decorators import can_view_patient, can_edit_patient


atendimento_bp = Blueprint('atendimento', __name__)


@atendimento_bp.route('/paciente/<int:paciente_id>/listar')
@login_required
@can_view_patient
def listar(paciente_id):
    """Lista atendimentos do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first()

    if not prontuario:
        flash('Este paciente não possui prontuário. Crie um primeiro.', 'warning')
        return redirect(url_for('prontuario.criar', paciente_id=paciente_id))

    # Filtros
    tipo_filtro = request.args.get('tipo', '').strip()
    status_filtro = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Query base
    query = Atendimento.query.filter_by(paciente_id=paciente_id)

    # Aplicar filtros
    if tipo_filtro:
        query = query.filter(Atendimento.tipo == tipo_filtro)
    if status_filtro:
        query = query.filter(Atendimento.status == status_filtro)

    # Ordenar por data (mais recentes primeiro)
    query = query.order_by(Atendimento.data_hora.desc())

    # Paginar
    paginacao = query.paginate(page=page, per_page=per_page, error_out=False)
    atendimentos = paginacao.items

    return render_template(
        'atendimento/listar.html',
        paciente=paciente,
        prontuario=prontuario,
        atendimentos=atendimentos,
        paginacao=paginacao,
        tipo_filtro=tipo_filtro,
        status_filtro=status_filtro
    )


@atendimento_bp.route('/<int:atendimento_id>')
@login_required
def visualizar(atendimento_id):
    """Visualiza um atendimento específico"""
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    # Verificar permissão
    if not PermissionService.pode_visualizar_paciente(atendimento.paciente_id, current_user):
        abort(403)

    # Registrar auditoria
    auditoria = AuditoriaAcesso(
        user_id=current_user.id,
        paciente_id=atendimento.paciente_id,
        acao='visualizar_atendimento',
        detalhes=f'Visualizou atendimento #{atendimento.id} do paciente {atendimento.paciente.nome}'
    )
    db.session.add(auditoria)
    db.session.commit()

    return render_template(
        'atendimento/visualizar.html',
        atendimento=atendimento,
        paciente=atendimento.paciente
    )


@atendimento_bp.route('/paciente/<int:paciente_id>/novo', methods=['GET', 'POST'])
@login_required
@can_edit_patient
def novo(paciente_id):
    """Cria novo atendimento"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first()

    if not prontuario:
        flash('Este paciente não possui prontuário. Crie um primeiro.', 'warning')
        return redirect(url_for('prontuario.criar', paciente_id=paciente_id))

    form = AtendimentoForm()

    # Pré-preencher data/hora atual
    if request.method == 'GET':
        form.data_hora.data = datetime.now().replace(second=0, microsecond=0)

    if form.validate_on_submit():
        try:
            # Converter intervenções para JSON
            intervencoes_list = []
            if form.intervencoes.data:
                intervencoes_list = [i.strip() for i in form.intervencoes.data.split('\n') if i.strip()]

            atendimento = Atendimento(
                prontuario_id=prontuario.id,
                paciente_id=paciente_id,
                profissional_id=current_user.id,
                data_hora=form.data_hora.data,
                duracao_minutos=form.duracao_minutos.data,
                tipo=form.tipo.data,
                modalidade=form.modalidade.data if form.modalidade.data else None,
                local=form.local.data,
                compareceu=form.compareceu.data,
                motivo_falta=form.motivo_falta.data if not form.compareceu.data else None,
                subjetivo=form.subjetivo.data,
                objetivo=form.objetivo.data,
                avaliacao=form.avaliacao.data,
                plano=form.plano.data,
                intervencoes=json.dumps(intervencoes_list, ensure_ascii=False) if intervencoes_list else None,
                recursos_utilizados=form.recursos_utilizados.data,
                orientacoes_familia=form.orientacoes_familia.data,
                orientacoes_escola=form.orientacoes_escola.data,
                observacoes=form.observacoes.data,
                status='rascunho'
            )

            db.session.add(atendimento)

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                paciente_id=paciente_id,
                acao='criar_atendimento',
                detalhes=f'Criou atendimento para paciente {paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Atendimento registrado com sucesso!', 'success')
            return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar atendimento: {str(e)}', 'danger')

    return render_template(
        'atendimento/form.html',
        form=form,
        paciente=paciente,
        prontuario=prontuario,
        titulo='Novo Atendimento'
    )


@atendimento_bp.route('/<int:atendimento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(atendimento_id):
    """Edita um atendimento existente"""
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(atendimento.paciente_id, current_user):
        abort(403)

    # Não permitir edição de atendimentos finalizados por outros usuários
    if atendimento.status == 'finalizado' and atendimento.profissional_id != current_user.id and not current_user.eh_admin():
        flash('Você não pode editar atendimentos finalizados por outros profissionais!', 'danger')
        return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))

    form = AtendimentoForm(obj=atendimento)

    if request.method == 'GET':
        # Converter JSON de intervenções para texto
        if atendimento.intervencoes:
            intervencoes_list = atendimento.get_intervencoes_list()
            form.intervencoes.data = '\n'.join(intervencoes_list)

    if form.validate_on_submit():
        try:
            # Converter intervenções para JSON
            intervencoes_list = []
            if form.intervencoes.data:
                intervencoes_list = [i.strip() for i in form.intervencoes.data.split('\n') if i.strip()]

            atendimento.data_hora = form.data_hora.data
            atendimento.duracao_minutos = form.duracao_minutos.data
            atendimento.tipo = form.tipo.data
            atendimento.modalidade = form.modalidade.data if form.modalidade.data else None
            atendimento.local = form.local.data
            atendimento.compareceu = form.compareceu.data
            atendimento.motivo_falta = form.motivo_falta.data if not form.compareceu.data else None
            atendimento.subjetivo = form.subjetivo.data
            atendimento.objetivo = form.objetivo.data
            atendimento.avaliacao = form.avaliacao.data
            atendimento.plano = form.plano.data
            atendimento.intervencoes = json.dumps(intervencoes_list, ensure_ascii=False) if intervencoes_list else None
            atendimento.recursos_utilizados = form.recursos_utilizados.data
            atendimento.orientacoes_familia = form.orientacoes_familia.data
            atendimento.orientacoes_escola = form.orientacoes_escola.data
            atendimento.observacoes = form.observacoes.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                paciente_id=atendimento.paciente_id,
                acao='editar_atendimento',
                detalhes=f'Editou atendimento #{atendimento_id} do paciente {atendimento.paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Atendimento atualizado com sucesso!', 'success')
            return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar atendimento: {str(e)}', 'danger')

    return render_template(
        'atendimento/form.html',
        form=form,
        atendimento=atendimento,
        paciente=atendimento.paciente,
        prontuario=atendimento.prontuario,
        titulo='Editar Atendimento'
    )


@atendimento_bp.route('/<int:atendimento_id>/finalizar', methods=['POST'])
@login_required
def finalizar(atendimento_id):
    """Finaliza um atendimento"""
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(atendimento.paciente_id, current_user):
        abort(403)

    if atendimento.status == 'finalizado':
        flash('Este atendimento já foi finalizado!', 'info')
        return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))

    try:
        atendimento.finalizar()

        # Registrar auditoria
        auditoria = AuditoriaAcesso(
            user_id=current_user.id,
            paciente_id=atendimento.paciente_id,
            acao='finalizar_atendimento',
            detalhes=f'Finalizou atendimento #{atendimento_id} do paciente {atendimento.paciente.nome}'
        )
        db.session.add(auditoria)

        db.session.commit()

        flash('Atendimento finalizado com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao finalizar atendimento: {str(e)}', 'danger')

    return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))


@atendimento_bp.route('/<int:atendimento_id>/excluir', methods=['POST'])
@login_required
def excluir(atendimento_id):
    """Exclui um atendimento"""
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(atendimento.paciente_id, current_user):
        abort(403)

    # Apenas criador ou admin pode excluir
    if atendimento.profissional_id != current_user.id and not current_user.eh_admin():
        flash('Apenas o profissional que criou o atendimento ou administradores podem excluí-lo!', 'danger')
        return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))

    # Não permitir exclusão de atendimentos finalizados
    if atendimento.status == 'finalizado':
        flash('Não é possível excluir atendimentos finalizados!', 'danger')
        return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))

    try:
        paciente_id = atendimento.paciente_id
        paciente_nome = atendimento.paciente.nome

        # Registrar auditoria
        auditoria = AuditoriaAcesso(
            user_id=current_user.id,
            paciente_id=paciente_id,
            acao='excluir_atendimento',
            detalhes=f'Excluiu atendimento #{atendimento_id} do paciente {paciente_nome}'
        )
        db.session.add(auditoria)

        db.session.delete(atendimento)
        db.session.commit()

        flash('Atendimento excluído com sucesso!', 'success')
        return redirect(url_for('atendimento.listar', paciente_id=paciente_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir atendimento: {str(e)}', 'danger')
        return redirect(url_for('atendimento.visualizar', atendimento_id=atendimento_id))
