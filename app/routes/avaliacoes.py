"""
Rotas para gerenciamento de avaliações
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Avaliacao, Paciente, Instrumento, Questao, Resposta, Dominio
from app.forms import AvaliacaoForm, RespostaForm
from app.services.calculo_service import CalculoService
from app.services.classificacao_service import ClassificacaoService
from sqlalchemy import func
from datetime import datetime

avaliacoes_bp = Blueprint('avaliacoes', __name__)


@avaliacoes_bp.route('/')
@login_required
def listar():
    """Lista todas as avaliações com filtros"""
    # Parâmetros de busca
    status_filtro = request.args.get('status', '').strip()
    paciente_id = request.args.get('paciente_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # Query base
    query = Avaliacao.query.join(Paciente).join(Instrumento)

    # Filtrar por paciente se especificado
    if paciente_id:
        query = query.filter(Avaliacao.paciente_id == paciente_id)

    # Filtrar por status
    if status_filtro and status_filtro in ['em_andamento', 'concluida', 'revisao']:
        query = query.filter(Avaliacao.status == status_filtro)

    # Ordenar por data mais recente
    query = query.order_by(Avaliacao.data_avaliacao.desc())

    # Paginar
    paginacao = query.paginate(page=page, per_page=per_page, error_out=False)
    avaliacoes = paginacao.items

    return render_template(
        'avaliacoes/listar.html',
        avaliacoes=avaliacoes,
        paginacao=paginacao,
        status_filtro=status_filtro,
        paciente_id=paciente_id
    )


@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cria uma nova avaliação"""
    # Obter paciente_id da query string
    paciente_id = request.args.get('paciente_id', type=int)
    instrumento_id = request.args.get('instrumento_id', type=int)

    if not paciente_id:
        flash('Paciente não especificado!', 'danger')
        return redirect(url_for('pacientes.listar'))

    paciente = Paciente.query.get_or_404(paciente_id)

    # Calcular idade para filtrar instrumentos
    idade = paciente.calcular_idade()

    form = AvaliacaoForm()
    form.paciente_id.data = paciente_id

    # Buscar instrumentos adequados para a idade
    instrumentos = Instrumento.query.filter(
        Instrumento.ativo == True,
        Instrumento.idade_minima <= idade,
        Instrumento.idade_maxima >= idade
    ).all()

    # Popular choices do select de instrumentos
    form.instrumento_id.choices = [(0, 'Selecione o instrumento...')] + [
        (i.id, f"{i.nome} ({i.contexto})") for i in instrumentos
    ]

    # Se instrumento foi pré-selecionado
    if instrumento_id and request.method == 'GET':
        form.instrumento_id.data = instrumento_id

    if form.validate_on_submit():
        try:
            instrumento = Instrumento.query.get(form.instrumento_id.data)

            if not instrumento:
                flash('Instrumento inválido!', 'danger')
                return render_template('avaliacoes/form.html', form=form, paciente=paciente)

            # Verificar se instrumento é adequado para a idade
            if idade < instrumento.idade_minima or idade > instrumento.idade_maxima:
                flash(f'Este instrumento não é adequado para a idade do paciente ({idade} anos)!', 'danger')
                return render_template('avaliacoes/form.html', form=form, paciente=paciente)

            # Criar nova avaliação
            avaliacao = Avaliacao(
                paciente_id=paciente_id,
                instrumento_id=instrumento.id,
                avaliador_id=current_user.id,
                data_avaliacao=form.data_avaliacao.data,
                relacionamento_respondente=form.relacionamento_respondente.data,
                comentarios=form.comentarios.data,
                status='em_andamento'
            )

            db.session.add(avaliacao)
            db.session.commit()

            flash(f'Avaliação criada com sucesso! Agora você pode responder às questões.', 'success')
            return redirect(url_for('avaliacoes.responder', id=avaliacao.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar avaliação: {str(e)}', 'danger')

    return render_template('avaliacoes/form.html', form=form, paciente=paciente, instrumentos=instrumentos)


@avaliacoes_bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza detalhes de uma avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    # Buscar respostas agrupadas por domínio
    respostas = (
        Resposta.query
        .join(Questao)
        .join(Dominio)
        .filter(Resposta.avaliacao_id == id)
        .order_by(Dominio.ordem, Questao.numero)
        .all()
    )

    # Agrupar respostas por domínio
    respostas_por_dominio = {}
    for resposta in respostas:
        dominio_nome = resposta.questao.dominio.nome
        if dominio_nome not in respostas_por_dominio:
            respostas_por_dominio[dominio_nome] = []
        respostas_por_dominio[dominio_nome].append(resposta)

    # Calcular progresso
    total_questoes = Questao.query.join(Dominio).filter(
        Dominio.instrumento_id == avaliacao.instrumento_id
    ).count()
    questoes_respondidas = len(respostas)
    progresso = int((questoes_respondidas / total_questoes * 100)) if total_questoes > 0 else 0

    return render_template(
        'avaliacoes/visualizar.html',
        avaliacao=avaliacao,
        respostas_por_dominio=respostas_por_dominio,
        total_questoes=total_questoes,
        questoes_respondidas=questoes_respondidas,
        progresso=progresso
    )


@avaliacoes_bp.route('/<int:id>/responder', methods=['GET', 'POST'])
@login_required
def responder(id):
    """Interface para responder questões da avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)

    if avaliacao.status == 'concluida':
        flash('Esta avaliação já foi concluída!', 'info')
        return redirect(url_for('avaliacoes.visualizar', id=id))

    # Buscar todas as questões do instrumento, ordenadas por domínio e número
    questoes = (
        Questao.query
        .join(Dominio)
        .filter(Dominio.instrumento_id == avaliacao.instrumento_id)
        .filter(Questao.ativo == True)
        .order_by(Dominio.ordem, Questao.numero)
        .all()
    )

    if not questoes:
        flash('Este instrumento não possui questões cadastradas!', 'warning')
        return redirect(url_for('avaliacoes.visualizar', id=id))

    # Buscar respostas já dadas
    respostas_existentes = {
        r.questao_id: r for r in Resposta.query.filter_by(avaliacao_id=id).all()
    }

    # Obter índice da questão atual (ou primeira não respondida)
    questao_idx = request.args.get('q', 0, type=int)

    # Se não especificado, buscar primeira questão não respondida
    if questao_idx == 0:
        for idx, questao in enumerate(questoes):
            if questao.id not in respostas_existentes:
                questao_idx = idx
                break

    # Validar índice
    if questao_idx < 0 or questao_idx >= len(questoes):
        questao_idx = 0

    questao_atual = questoes[questao_idx]
    resposta_existente = respostas_existentes.get(questao_atual.id)

    # Criar formulário
    form = RespostaForm()
    form.questao_id.data = questao_atual.id

    # Preencher com resposta existente
    if resposta_existente and request.method == 'GET':
        form.valor.data = resposta_existente.valor

    if form.validate_on_submit():
        try:
            # Calcular pontuação
            pontuacao = CalculoService.calcular_pontuacao_resposta(
                form.valor.data,
                questao_atual.dominio.escala_invertida
            )

            if resposta_existente:
                # Atualizar resposta existente
                resposta_existente.valor = form.valor.data
                resposta_existente.pontuacao = pontuacao
            else:
                # Criar nova resposta
                resposta = Resposta(
                    avaliacao_id=id,
                    questao_id=questao_atual.id,
                    valor=form.valor.data,
                    pontuacao=pontuacao
                )
                db.session.add(resposta)

            db.session.commit()

            # Verificar se é a última questão
            if questao_idx == len(questoes) - 1:
                flash('Todas as questões foram respondidas!', 'success')
                return redirect(url_for('avaliacoes.finalizar', id=id))
            else:
                # Ir para próxima questão
                return redirect(url_for('avaliacoes.responder', id=id, q=questao_idx + 1))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar resposta: {str(e)}', 'danger')

    # Calcular progresso
    total_questoes = len(questoes)
    questoes_respondidas = len(respostas_existentes)
    progresso = int((questoes_respondidas / total_questoes * 100)) if total_questoes > 0 else 0

    return render_template(
        'avaliacoes/responder.html',
        avaliacao=avaliacao,
        questao=questao_atual,
        questao_idx=questao_idx,
        total_questoes=total_questoes,
        questoes_respondidas=questoes_respondidas,
        progresso=progresso,
        form=form,
        pode_voltar=questao_idx > 0,
        pode_avancar=questao_idx < total_questoes - 1,
        resposta_existente=resposta_existente
    )


@avaliacoes_bp.route('/<int:id>/finalizar', methods=['GET', 'POST'])
@login_required
def finalizar(id):
    """Finaliza uma avaliação e calcula os escores"""
    avaliacao = Avaliacao.query.get_or_404(id)

    # Verificar se todas as questões foram respondidas
    total_questoes = Questao.query.join(Dominio).filter(
        Dominio.instrumento_id == avaliacao.instrumento_id,
        Questao.ativo == True
    ).count()

    questoes_respondidas = Resposta.query.filter_by(avaliacao_id=id).count()

    if questoes_respondidas < total_questoes:
        flash(f'Ainda faltam {total_questoes - questoes_respondidas} questão(ões) para responder!', 'warning')
        return redirect(url_for('avaliacoes.responder', id=id))

    if request.method == 'POST':
        try:
            # Calcular escores
            CalculoService.atualizar_escores_avaliacao(id)

            # Classificar resultados
            ClassificacaoService.classificar_avaliacao(id)

            # Atualizar status e data de conclusão
            avaliacao.status = 'concluida'
            avaliacao.data_conclusao = datetime.utcnow()

            db.session.commit()

            flash('Avaliação finalizada com sucesso! Escores calculados e classificados.', 'success')
            return redirect(url_for('avaliacoes.visualizar', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao finalizar avaliação: {str(e)}', 'danger')

    return render_template('avaliacoes/finalizar.html', avaliacao=avaliacao, total_questoes=total_questoes)


@avaliacoes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui uma avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)
    paciente_id = avaliacao.paciente_id

    try:
        # Excluir respostas associadas
        Resposta.query.filter_by(avaliacao_id=id).delete()

        # Excluir avaliação
        db.session.delete(avaliacao)
        db.session.commit()

        flash('Avaliação excluída com sucesso!', 'success')
        return redirect(url_for('pacientes.visualizar', id=paciente_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir avaliação: {str(e)}', 'danger')
        return redirect(url_for('avaliacoes.visualizar', id=id))
