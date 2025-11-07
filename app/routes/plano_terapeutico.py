"""
Rotas para gerenciamento de Planos Terapêuticos e Objetivos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
import json

from app import db
from app.forms import (
    PlanoTerapeuticoForm, AlterarStatusPlanoForm,
    ObjetivoTerapeuticoForm, AtualizarProgressoObjetivoForm
)
from app.models import PlanoTerapeutico, ObjetivoTerapeutico, Paciente, Prontuario, AuditoriaAcesso
from app.services.permission_service import PermissionService
from app.utils.decorators import can_view_patient, can_edit_patient


plano_terapeutico_bp = Blueprint('plano_terapeutico', __name__)


@plano_terapeutico_bp.route('/paciente/<int:paciente_id>/listar')
@login_required
@can_view_patient
def listar(paciente_id):
    """Lista planos terapêuticos do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first()

    if not prontuario:
        flash('Este paciente não possui prontuário. Crie um primeiro.', 'warning')
        return redirect(url_for('prontuario.criar', paciente_id=paciente_id))

    # Buscar planos
    planos = PlanoTerapeutico.query.filter_by(paciente_id=paciente_id).order_by(
        PlanoTerapeutico.data_inicio.desc()
    ).all()

    return render_template(
        'plano_terapeutico/listar.html',
        paciente=paciente,
        prontuario=prontuario,
        planos=planos
    )


@plano_terapeutico_bp.route('/<int:plano_id>')
@login_required
def visualizar(plano_id):
    """Visualiza um plano terapêutico"""
    plano = PlanoTerapeutico.query.get_or_404(plano_id)

    # Verificar permissão
    if not PermissionService.pode_visualizar_paciente(current_user, plano.paciente_id):
        abort(403)

    # Buscar objetivos agrupados por prioridade
    objetivos = plano.objetivos.all()
    objetivos_por_prioridade = {
        1: [o for o in objetivos if o.prioridade == 1],
        2: [o for o in objetivos if o.prioridade == 2],
        3: [o for o in objetivos if o.prioridade == 3]
    }

    # Registrar auditoria
    auditoria = AuditoriaAcesso(
        user_id=current_user.id,
        recurso_tipo='plano_terapeutico',
        recurso_id=plano.id,
        paciente_id=plano.paciente_id,
        acao='visualizar_plano_terapeutico',
        detalhes=f'Visualizou plano terapêutico #{plano.id} do paciente {plano.paciente.nome}'
    )
    db.session.add(auditoria)
    db.session.commit()

    return render_template(
        'plano_terapeutico/visualizar.html',
        plano=plano,
        paciente=plano.paciente,
        objetivos_por_prioridade=objetivos_por_prioridade
    )


@plano_terapeutico_bp.route('/paciente/<int:paciente_id>/novo', methods=['GET', 'POST'])
@login_required
@can_edit_patient
def novo(paciente_id):
    """Cria novo plano terapêutico"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first()

    if not prontuario:
        flash('Este paciente não possui prontuário. Crie um primeiro.', 'warning')
        return redirect(url_for('prontuario.criar', paciente_id=paciente_id))

    form = PlanoTerapeuticoForm()

    # Pré-preencher data de início
    if request.method == 'GET':
        form.data_inicio.data = date.today()

    if form.validate_on_submit():
        try:
            # Converter áreas de foco para JSON
            areas_list = []
            if form.areas_foco.data:
                areas_list = [a.strip() for a in form.areas_foco.data.split('\n') if a.strip()]

            plano = PlanoTerapeutico(
                prontuario_id=prontuario.id,
                paciente_id=paciente_id,
                profissional_id=current_user.id,
                titulo=form.titulo.data,
                descricao=form.descricao.data,
                data_inicio=form.data_inicio.data,
                data_fim=form.data_fim.data,
                duracao_prevista_meses=form.duracao_prevista_meses.data,
                frequencia_semanal=form.frequencia_semanal.data,
                duracao_sessao_minutos=form.duracao_sessao_minutos.data,
                areas_foco=json.dumps(areas_list, ensure_ascii=False) if areas_list else None,
                estrategias_gerais=form.estrategias_gerais.data,
                recursos_necessarios=form.recursos_necessarios.data,
                orientacoes_familia=form.orientacoes_familia.data,
                orientacoes_escola=form.orientacoes_escola.data,
                orientacoes_equipe=form.orientacoes_equipe.data,
                criterios_alta=form.criterios_alta.data,
                observacoes=form.observacoes.data,
                status='ativo'
            )

            db.session.add(plano)
            db.session.flush()  # garante ID antes do registro de auditoria

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='plano_terapeutico',
                recurso_id=plano.id,
                paciente_id=paciente_id,
                acao='criar_plano_terapeutico',
                detalhes=f'Criou plano terapêutico "{form.titulo.data}" para paciente {paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Plano terapêutico criado com sucesso! Agora você pode adicionar objetivos.', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar plano terapêutico: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/form.html',
        form=form,
        paciente=paciente,
        prontuario=prontuario,
        titulo='Novo Plano Terapêutico'
    )


@plano_terapeutico_bp.route('/<int:plano_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(plano_id):
    """Edita um plano terapêutico"""
    plano = PlanoTerapeutico.query.get_or_404(plano_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    form = PlanoTerapeuticoForm(obj=plano)

    if request.method == 'GET':
        # Converter áreas de foco de JSON para texto
        if plano.areas_foco:
            areas_list = plano.get_areas_foco_list()
            form.areas_foco.data = '\n'.join(areas_list)

    if form.validate_on_submit():
        try:
            # Converter áreas de foco para JSON
            areas_list = []
            if form.areas_foco.data:
                areas_list = [a.strip() for a in form.areas_foco.data.split('\n') if a.strip()]

            plano.titulo = form.titulo.data
            plano.descricao = form.descricao.data
            plano.data_inicio = form.data_inicio.data
            plano.data_fim = form.data_fim.data
            plano.duracao_prevista_meses = form.duracao_prevista_meses.data
            plano.frequencia_semanal = form.frequencia_semanal.data
            plano.duracao_sessao_minutos = form.duracao_sessao_minutos.data
            plano.areas_foco = json.dumps(areas_list, ensure_ascii=False) if areas_list else None
            plano.estrategias_gerais = form.estrategias_gerais.data
            plano.recursos_necessarios = form.recursos_necessarios.data
            plano.orientacoes_familia = form.orientacoes_familia.data
            plano.orientacoes_escola = form.orientacoes_escola.data
            plano.orientacoes_equipe = form.orientacoes_equipe.data
            plano.criterios_alta = form.criterios_alta.data
            plano.observacoes = form.observacoes.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='plano_terapeutico',
                recurso_id=plano.id,
                paciente_id=plano.paciente_id,
                acao='editar_plano_terapeutico',
                detalhes=f'Editou plano terapêutico #{plano.id} do paciente {plano.paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Plano terapêutico atualizado com sucesso!', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar plano terapêutico: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/form.html',
        form=form,
        plano=plano,
        paciente=plano.paciente,
        prontuario=plano.prontuario,
        titulo='Editar Plano Terapêutico'
    )


@plano_terapeutico_bp.route('/<int:plano_id>/alterar-status', methods=['GET', 'POST'])
@login_required
def alterar_status(plano_id):
    """Altera status do plano terapêutico"""
    plano = PlanoTerapeutico.query.get_or_404(plano_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    form = AlterarStatusPlanoForm()

    if request.method == 'GET':
        form.status.data = plano.status

    if form.validate_on_submit():
        try:
            plano.status = form.status.data
            plano.motivo_status = form.motivo_status.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='plano_terapeutico',
                recurso_id=plano.id,
                paciente_id=plano.paciente_id,
                acao='alterar_status_plano',
                detalhes=f'Alterou status do plano #{plano.id} para {form.status.data}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash(f'Status alterado para: {plano.get_status_display()}', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar status: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/alterar_status.html',
        form=form,
        plano=plano
    )


# ========== OBJETIVOS TERAPÊUTICOS ==========

@plano_terapeutico_bp.route('/<int:plano_id>/objetivo/novo', methods=['GET', 'POST'])
@login_required
def novo_objetivo(plano_id):
    """Adiciona novo objetivo ao plano"""
    plano = PlanoTerapeutico.query.get_or_404(plano_id)

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    form = ObjetivoTerapeuticoForm()

    if form.validate_on_submit():
        try:
            objetivo = ObjetivoTerapeutico(
                plano_id=plano_id,
                descricao=form.descricao.data,
                area=form.area.data,
                prioridade=form.prioridade.data,
                tipo=form.tipo.data,
                criterio_sucesso=form.criterio_sucesso.data,
                meta_quantitativa=form.meta_quantitativa.data,
                estrategias=form.estrategias.data,
                recursos=form.recursos.data,
                prazo_estimado=form.prazo_estimado.data,
                observacoes=form.observacoes.data,
                status='em_andamento',
                percentual_progresso=0
            )

            db.session.add(objetivo)
            db.session.flush()

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='objetivo_terapeutico',
                recurso_id=objetivo.id,
                paciente_id=plano.paciente_id,
                acao='criar_objetivo',
                detalhes=f'Criou objetivo no plano #{plano.id}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Objetivo adicionado com sucesso!', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar objetivo: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/objetivo_form.html',
        form=form,
        plano=plano,
        titulo='Novo Objetivo'
    )


@plano_terapeutico_bp.route('/objetivo/<int:objetivo_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_objetivo(objetivo_id):
    """Edita um objetivo"""
    objetivo = ObjetivoTerapeutico.query.get_or_404(objetivo_id)
    plano = objetivo.plano

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    form = ObjetivoTerapeuticoForm(obj=objetivo)

    if form.validate_on_submit():
        try:
            objetivo.descricao = form.descricao.data
            objetivo.area = form.area.data
            objetivo.prioridade = form.prioridade.data
            objetivo.tipo = form.tipo.data
            objetivo.criterio_sucesso = form.criterio_sucesso.data
            objetivo.meta_quantitativa = form.meta_quantitativa.data
            objetivo.estrategias = form.estrategias.data
            objetivo.recursos = form.recursos.data
            objetivo.prazo_estimado = form.prazo_estimado.data
            objetivo.observacoes = form.observacoes.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='objetivo_terapeutico',
                recurso_id=objetivo.id,
                paciente_id=plano.paciente_id,
                acao='editar_objetivo',
                detalhes=f'Editou objetivo #{objetivo_id} do plano #{plano.id}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Objetivo atualizado com sucesso!', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar objetivo: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/objetivo_form.html',
        form=form,
        plano=plano,
        objetivo=objetivo,
        titulo='Editar Objetivo'
    )


@plano_terapeutico_bp.route('/objetivo/<int:objetivo_id>/progresso', methods=['GET', 'POST'])
@login_required
def atualizar_progresso(objetivo_id):
    """Atualiza progresso do objetivo"""
    objetivo = ObjetivoTerapeutico.query.get_or_404(objetivo_id)
    plano = objetivo.plano

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    form = AtualizarProgressoObjetivoForm()

    if request.method == 'GET':
        form.percentual_progresso.data = objetivo.percentual_progresso
        form.status.data = objetivo.status

    if form.validate_on_submit():
        try:
            # Adicionar evolução
            objetivo.adicionar_evolucao(
                form.descricao_evolucao.data,
                form.percentual_progresso.data
            )
            objetivo.status = form.status.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='objetivo_terapeutico',
                recurso_id=objetivo.id,
                paciente_id=plano.paciente_id,
                acao='atualizar_progresso_objetivo',
                detalhes=f'Atualizou progresso do objetivo #{objetivo_id} para {form.percentual_progresso.data}%'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Progresso atualizado com sucesso!', 'success')
            return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar progresso: {str(e)}', 'danger')

    return render_template(
        'plano_terapeutico/atualizar_progresso.html',
        form=form,
        objetivo=objetivo,
        plano=plano
    )


@plano_terapeutico_bp.route('/objetivo/<int:objetivo_id>/excluir', methods=['POST'])
@login_required
def excluir_objetivo(objetivo_id):
    """Exclui um objetivo"""
    objetivo = ObjetivoTerapeutico.query.get_or_404(objetivo_id)
    plano = objetivo.plano

    # Verificar permissão
    if not PermissionService.pode_editar_paciente(plano.paciente_id, current_user):
        abort(403)

    try:
        plano_id = objetivo.plano_id

        # Registrar auditoria
        auditoria = AuditoriaAcesso(
            user_id=current_user.id,
            recurso_tipo='objetivo_terapeutico',
            recurso_id=objetivo.id,
            paciente_id=plano.paciente_id,
            acao='excluir_objetivo',
            detalhes=f'Excluiu objetivo #{objetivo_id} do plano #{plano.id}'
        )
        db.session.add(auditoria)

        db.session.delete(objetivo)
        db.session.commit()

        flash('Objetivo excluído com sucesso!', 'success')
        return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir objetivo: {str(e)}', 'danger')
        return redirect(url_for('plano_terapeutico.visualizar', plano_id=plano.id))
