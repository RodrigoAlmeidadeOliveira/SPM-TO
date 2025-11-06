"""
Blueprint de Avaliações
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.avaliacao import Avaliacao, Resposta
from app.models.paciente import Paciente
from app.models.instrumento import Instrumento, Questao
from app.forms.avaliacao_forms import AvaliacaoForm
from app.services.calculo_service import CalculoService
from app.services.classificacao_service import ClassificacaoService
from app import db
from datetime import datetime

avaliacoes_bp = Blueprint('avaliacoes', __name__)


@avaliacoes_bp.route('/')
@login_required
def listar():
    """Lista avaliações"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    paciente_id = request.args.get('paciente_id', type=int)
    status = request.args.get('status', '')

    query = Avaliacao.query

    if paciente_id:
        query = query.filter_by(paciente_id=paciente_id)

    if status:
        query = query.filter_by(status=status)

    avaliacoes = query.order_by(db.desc(Avaliacao.data_avaliacao)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('avaliacoes/listar.html',
                          avaliacoes=avaliacoes,
                          paciente_id=paciente_id,
                          status=status)


@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Nova avaliação"""
    form = AvaliacaoForm()

    # Preencher choices de pacientes e instrumentos
    form.paciente_id.choices = [('', 'Selecione um paciente')] + [
        (p.id, f'{p.nome} - {p.calcular_idade()[0]} anos')
        for p in Paciente.query.filter_by(ativo=True).order_by(Paciente.nome).all()
    ]

    form.instrumento_id.choices = [('', 'Selecione um instrumento')] + [
        (i.id, i.nome)
        for i in Instrumento.query.filter_by(ativo=True).order_by(Instrumento.nome).all()
    ]

    if form.validate_on_submit():
        avaliacao = Avaliacao(
            paciente_id=form.paciente_id.data,
            instrumento_id=form.instrumento_id.data,
            avaliador_id=current_user.id,
            data_avaliacao=form.data_avaliacao.data,
            relacionamento_respondente=form.relacionamento_respondente.data,
            comentarios=form.comentarios.data,
            status='em_andamento'
        )

        db.session.add(avaliacao)
        db.session.commit()

        flash('Avaliação criada com sucesso! Agora responda as questões.', 'success')
        return redirect(url_for('avaliacoes.responder', id=avaliacao.id))

    # Preencher data padrão
    if not form.data_avaliacao.data:
        form.data_avaliacao.data = datetime.now().date()

    return render_template('avaliacoes/form.html', form=form, titulo='Nova Avaliação')


@avaliacoes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualizar avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    # Calcular estatísticas de progresso
    total_questoes = 0
    for dominio in avaliacao.instrumento.dominios:
        total_questoes += dominio.questoes.filter_by(ativo=True).count()

    total_respostas = avaliacao.respostas.count()
    progresso = (total_respostas / total_questoes * 100) if total_questoes > 0 else 0

    return render_template('avaliacoes/visualizar.html',
                          avaliacao=avaliacao,
                          total_questoes=total_questoes,
                          total_respostas=total_respostas,
                          progresso=progresso)


@avaliacoes_bp.route('/<int:id>/responder', methods=['GET', 'POST'])
@login_required
def responder(id):
    """Interface para responder avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    if request.method == 'POST':
        # Processar respostas em lote (JSON)
        data = request.get_json()

        if data:
            for questao_id, valor in data.items():
                questao = Questao.query.get(int(questao_id))
                if not questao:
                    continue

                # Calcular pontuação
                pontuacao = CalculoService.calcular_pontuacao_resposta(
                    valor,
                    questao.dominio.escala_invertida
                )

                # Verificar se já existe resposta
                resposta = Resposta.query.filter_by(
                    avaliacao_id=avaliacao.id,
                    questao_id=questao.id
                ).first()

                if resposta:
                    resposta.valor = valor
                    resposta.pontuacao = pontuacao
                else:
                    resposta = Resposta(
                        avaliacao_id=avaliacao.id,
                        questao_id=questao.id,
                        valor=valor,
                        pontuacao=pontuacao
                    )
                    db.session.add(resposta)

            db.session.commit()

            # Se completou todas as questões, calcular escores
            if avaliacao.esta_completa():
                CalculoService.atualizar_escores_avaliacao(avaliacao)
                ClassificacaoService.classificar_avaliacao(avaliacao)

                avaliacao.status = 'concluida'
                avaliacao.data_conclusao = datetime.utcnow()
                db.session.commit()

                flash('Avaliação concluída com sucesso!', 'success')
                return jsonify({'redirect': url_for('avaliacoes.visualizar', id=avaliacao.id)})

            return jsonify({'success': True})

    # GET - Carregar questões e respostas existentes
    dominios_questoes = []
    respostas_existentes = {}

    # Obter respostas já preenchidas
    for resposta in avaliacao.respostas:
        respostas_existentes[resposta.questao_id] = resposta.valor

    # Organizar questões por domínio
    for dominio in avaliacao.instrumento.dominios.order_by('ordem'):
        questoes = dominio.questoes.filter_by(ativo=True).order_by('numero').all()
        if questoes:
            dominios_questoes.append({
                'dominio': dominio,
                'questoes': questoes
            })

    return render_template('avaliacoes/responder.html',
                          avaliacao=avaliacao,
                          dominios_questoes=dominios_questoes,
                          respostas_existentes=respostas_existentes)


@avaliacoes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    # Verificar permissão (apenas admin ou quem criou)
    if not current_user.is_admin() and avaliacao.avaliador_id != current_user.id:
        flash('Você não tem permissão para excluir esta avaliação', 'danger')
        return redirect(url_for('avaliacoes.visualizar', id=id))

    paciente_id = avaliacao.paciente_id
    db.session.delete(avaliacao)
    db.session.commit()

    flash('Avaliação excluída com sucesso!', 'success')
    return redirect(url_for('pacientes.visualizar', id=paciente_id))


@avaliacoes_bp.route('/<int:id>/recalcular', methods=['POST'])
@login_required
def recalcular(id):
    """Recalcular escores da avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    if avaliacao.esta_completa():
        CalculoService.atualizar_escores_avaliacao(avaliacao)
        ClassificacaoService.classificar_avaliacao(avaliacao)

        flash('Escores recalculados com sucesso!', 'success')
    else:
        flash('Avaliação incompleta. Complete todas as questões primeiro.', 'warning')

    return redirect(url_for('avaliacoes.visualizar', id=id))
