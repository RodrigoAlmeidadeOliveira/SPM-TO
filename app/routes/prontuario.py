"""
Rotas para gerenciamento de Prontuário Eletrônico
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import json

from app import db
from app.forms import ProntuarioForm, EncerrarProntuarioForm
from app.models import Prontuario, Paciente, Atendimento, PlanoTerapeutico, AuditoriaAcesso
from app.services.permission_service import PermissionService
from app.utils.decorators import can_view_patient, can_edit_patient


prontuario_bp = Blueprint('prontuario', __name__)


@prontuario_bp.route('/paciente/<int:paciente_id>')
@login_required
@can_view_patient
def visualizar(paciente_id):
    """Visualiza o prontuário do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first()

    if not prontuario:
        flash('Este paciente ainda não possui prontuário. Crie um primeiro.', 'info')
        return redirect(url_for('prontuario.criar', paciente_id=paciente_id))

    # Registrar auditoria
    auditoria = AuditoriaAcesso(
        user_id=current_user.id,
        recurso_tipo='prontuario',
        recurso_id=prontuario.id,
        paciente_id=paciente_id,
        acao='visualizar_prontuario',
        detalhes=f'Visualizou prontuário do paciente {paciente.nome}'
    )
    db.session.add(auditoria)
    db.session.commit()

    # Buscar dados relacionados
    atendimentos_recentes = prontuario.atendimentos.limit(5).all()
    total_atendimentos = prontuario.count_atendimentos()
    plano_ativo = prontuario.get_plano_terapeutico_ativo()

    return render_template(
        'prontuario/visualizar.html',
        paciente=paciente,
        prontuario=prontuario,
        atendimentos_recentes=atendimentos_recentes,
        total_atendimentos=total_atendimentos,
        plano_ativo=plano_ativo
    )


@prontuario_bp.route('/paciente/<int:paciente_id>/criar', methods=['GET', 'POST'])
@login_required
@can_edit_patient
def criar(paciente_id):
    """Cria prontuário para o paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)

    # Verificar se já existe prontuário
    prontuario_existente = Prontuario.query.filter_by(paciente_id=paciente_id).first()
    if prontuario_existente:
        flash('Este paciente já possui prontuário!', 'warning')
        return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

    form = ProntuarioForm()

    if form.validate_on_submit():
        try:
            # Converter campos de texto com listas em JSON
            diagnosticos_list = [d.strip() for d in form.diagnosticos.data.split('\n') if d.strip()] if form.diagnosticos.data else []
            medicamentos_list = [m.strip() for m in form.medicamentos_uso.data.split('\n') if m.strip()] if form.medicamentos_uso.data else []
            alergias_list = [a.strip() for a in form.alergias.data.split('\n') if a.strip()] if form.alergias.data else []
            cirurgias_list = [c.strip() for c in form.cirurgias_previas.data.split('\n') if c.strip()] if form.cirurgias_previas.data else []
            internacoes_list = [i.strip() for i in form.internacoes_previas.data.split('\n') if i.strip()] if form.internacoes_previas.data else []

            prontuario = Prontuario(
                paciente_id=paciente_id,
                profissional_abertura_id=current_user.id,
                queixa_principal=form.queixa_principal.data,
                historia_doenca_atual=form.historia_doenca_atual.data,
                historia_previa=form.historia_previa.data,
                gestacao=form.gestacao.data,
                parto=form.parto.data,
                desenvolvimento_motor=form.desenvolvimento_motor.data,
                desenvolvimento_linguagem=form.desenvolvimento_linguagem.data,
                desenvolvimento_social=form.desenvolvimento_social.data,
                diagnosticos=json.dumps(diagnosticos_list, ensure_ascii=False) if diagnosticos_list else None,
                medicamentos_uso=json.dumps(medicamentos_list, ensure_ascii=False) if medicamentos_list else None,
                alergias=json.dumps(alergias_list, ensure_ascii=False) if alergias_list else None,
                cirurgias_previas=json.dumps(cirurgias_list, ensure_ascii=False) if cirurgias_list else None,
                internacoes_previas=json.dumps(internacoes_list, ensure_ascii=False) if internacoes_list else None,
                historia_familiar=form.historia_familiar.data,
                escola=form.escola.data,
                serie_ano=form.serie_ano.data,
                possui_aee=form.possui_aee.data,
                possui_cuidador=form.possui_cuidador.data,
                composicao_familiar=form.composicao_familiar.data,
                objetivos_gerais=form.objetivos_gerais.data,
                observacoes=form.observacoes.data,
                status='ativo'
            )

            db.session.add(prontuario)
            db.session.flush()  # garante ID para auditoria antes do commit

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='prontuario',
                recurso_id=prontuario.id,
                paciente_id=paciente_id,
                acao='criar_prontuario',
                detalhes=f'Criou prontuário para paciente {paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Prontuário criado com sucesso!', 'success')
            return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar prontuário: {str(e)}', 'danger')

    return render_template('prontuario/form.html', form=form, paciente=paciente, titulo='Criar Prontuário')


@prontuario_bp.route('/paciente/<int:paciente_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_patient
def editar(paciente_id):
    """Edita prontuário do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first_or_404()

    form = ProntuarioForm(obj=prontuario)

    if request.method == 'GET':
        # Preencher campos de listas convertendo JSON para texto
        if prontuario.diagnosticos:
            form.diagnosticos.data = '\n'.join(prontuario.get_diagnosticos_list())
        if prontuario.medicamentos_uso:
            form.medicamentos_uso.data = '\n'.join(prontuario.get_medicamentos_list())
        if prontuario.alergias:
            form.alergias.data = '\n'.join(prontuario.get_alergias_list())
        if prontuario.cirurgias_previas:
            try:
                cirurgias = json.loads(prontuario.cirurgias_previas)
                form.cirurgias_previas.data = '\n'.join(cirurgias)
            except:
                pass
        if prontuario.internacoes_previas:
            try:
                internacoes = json.loads(prontuario.internacoes_previas)
                form.internacoes_previas.data = '\n'.join(internacoes)
            except:
                pass

    if form.validate_on_submit():
        try:
            # Converter campos de texto com listas em JSON
            diagnosticos_list = [d.strip() for d in form.diagnosticos.data.split('\n') if d.strip()] if form.diagnosticos.data else []
            medicamentos_list = [m.strip() for m in form.medicamentos_uso.data.split('\n') if m.strip()] if form.medicamentos_uso.data else []
            alergias_list = [a.strip() for a in form.alergias.data.split('\n') if a.strip()] if form.alergias.data else []
            cirurgias_list = [c.strip() for c in form.cirurgias_previas.data.split('\n') if c.strip()] if form.cirurgias_previas.data else []
            internacoes_list = [i.strip() for i in form.internacoes_previas.data.split('\n') if i.strip()] if form.internacoes_previas.data else []

            prontuario.queixa_principal = form.queixa_principal.data
            prontuario.historia_doenca_atual = form.historia_doenca_atual.data
            prontuario.historia_previa = form.historia_previa.data
            prontuario.gestacao = form.gestacao.data
            prontuario.parto = form.parto.data
            prontuario.desenvolvimento_motor = form.desenvolvimento_motor.data
            prontuario.desenvolvimento_linguagem = form.desenvolvimento_linguagem.data
            prontuario.desenvolvimento_social = form.desenvolvimento_social.data
            prontuario.diagnosticos = json.dumps(diagnosticos_list, ensure_ascii=False) if diagnosticos_list else None
            prontuario.medicamentos_uso = json.dumps(medicamentos_list, ensure_ascii=False) if medicamentos_list else None
            prontuario.alergias = json.dumps(alergias_list, ensure_ascii=False) if alergias_list else None
            prontuario.cirurgias_previas = json.dumps(cirurgias_list, ensure_ascii=False) if cirurgias_list else None
            prontuario.internacoes_previas = json.dumps(internacoes_list, ensure_ascii=False) if internacoes_list else None
            prontuario.historia_familiar = form.historia_familiar.data
            prontuario.escola = form.escola.data
            prontuario.serie_ano = form.serie_ano.data
            prontuario.possui_aee = form.possui_aee.data
            prontuario.possui_cuidador = form.possui_cuidador.data
            prontuario.composicao_familiar = form.composicao_familiar.data
            prontuario.objetivos_gerais = form.objetivos_gerais.data
            prontuario.observacoes = form.observacoes.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='prontuario',
                recurso_id=prontuario.id,
                paciente_id=paciente_id,
                acao='editar_prontuario',
                detalhes=f'Editou prontuário do paciente {paciente.nome}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash('Prontuário atualizado com sucesso!', 'success')
            return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar prontuário: {str(e)}', 'danger')

    return render_template('prontuario/form.html', form=form, paciente=paciente, prontuario=prontuario, titulo='Editar Prontuário')


@prontuario_bp.route('/paciente/<int:paciente_id>/encerrar', methods=['GET', 'POST'])
@login_required
@can_edit_patient
def encerrar(paciente_id):
    """Encerra o prontuário do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first_or_404()

    if prontuario.status != 'ativo':
        flash('Este prontuário já foi encerrado!', 'warning')
        return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

    form = EncerrarProntuarioForm()

    if form.validate_on_submit():
        try:
            prontuario.status = form.status.data
            prontuario.data_encerramento = form.data_encerramento.data
            prontuario.motivo_encerramento = form.motivo_encerramento.data

            # Registrar auditoria
            auditoria = AuditoriaAcesso(
                user_id=current_user.id,
                recurso_tipo='prontuario',
                recurso_id=prontuario.id,
                paciente_id=paciente_id,
                acao='encerrar_prontuario',
                detalhes=f'Encerrou prontuário do paciente {paciente.nome} - Status: {form.status.data}'
            )
            db.session.add(auditoria)

            db.session.commit()

            flash(f'Prontuário encerrado com sucesso! Status: {prontuario.get_status_display()}', 'success')
            return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao encerrar prontuário: {str(e)}', 'danger')

    return render_template('prontuario/encerrar.html', form=form, paciente=paciente, prontuario=prontuario)


@prontuario_bp.route('/paciente/<int:paciente_id>/reativar', methods=['POST'])
@login_required
@can_edit_patient
def reativar(paciente_id):
    """Reativa um prontuário encerrado"""
    paciente = Paciente.query.get_or_404(paciente_id)
    prontuario = Prontuario.query.filter_by(paciente_id=paciente_id).first_or_404()

    if prontuario.status == 'ativo':
        flash('Este prontuário já está ativo!', 'info')
        return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))

    try:
        prontuario.status = 'ativo'
        prontuario.data_encerramento = None
        prontuario.motivo_encerramento = None

        # Registrar auditoria
        auditoria = AuditoriaAcesso(
            user_id=current_user.id,
            recurso_tipo='prontuario',
            recurso_id=prontuario.id,
            paciente_id=paciente_id,
            acao='reativar_prontuario',
            detalhes=f'Reativou prontuário do paciente {paciente.nome}'
        )
        db.session.add(auditoria)

        db.session.commit()

        flash('Prontuário reativado com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar prontuário: {str(e)}', 'danger')

    return redirect(url_for('prontuario.visualizar', paciente_id=paciente_id))
