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
from app.services.modulos_service import ModulosService
from app.services.permission_service import PermissionService
from app.utils.decorators import can_view_avaliacao, can_edit_avaliacao
from sqlalchemy import func
from datetime import datetime

avaliacoes_bp = Blueprint('avaliacoes', __name__)


@avaliacoes_bp.route('/')
@login_required
def listar():
    """Lista avaliações com filtros avançados"""
    from app.models.user import User
    from datetime import datetime as dt

    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    paciente_id = request.args.get('paciente_id', type=int)
    avaliador_id = request.args.get('avaliador_id', type=int)
    status = request.args.get('status', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    busca = request.args.get('busca', '')

    # Query base
    query = Avaliacao.query.join(Paciente).join(Instrumento)

    # Filtrar avaliações baseado nos pacientes que o usuário tem acesso
    if not current_user.is_admin():
        # Obter IDs de pacientes que o usuário pode acessar
        pacientes_query = Paciente.query
        pacientes_query = PermissionService.filtrar_pacientes_por_permissao(pacientes_query, current_user)
        pacientes_ids = [p.id for p in pacientes_query.all()]

        # Filtrar avaliações apenas destes pacientes
        if pacientes_ids:
            query = query.filter(Avaliacao.paciente_id.in_(pacientes_ids))
        else:
            query = query.filter(False)  # Nenhum resultado

    # Filtro por paciente específico
    if paciente_id:
        # Verificar se o usuário tem permissão para este paciente
        if not PermissionService.pode_acessar_paciente(current_user, paciente_id):
            flash('Você não tem permissão para visualizar avaliações deste paciente', 'danger')
            return redirect(url_for('avaliacoes.listar'))
        query = query.filter(Avaliacao.paciente_id == paciente_id)

    # Filtro por avaliador
    if avaliador_id:
        query = query.filter_by(avaliador_id=avaliador_id)

    # Filtro por status
    if status:
        query = query.filter_by(status=status)

    # Filtro por período
    if data_inicio:
        try:
            data_inicio_dt = dt.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(Avaliacao.data_avaliacao >= data_inicio_dt)
        except ValueError:
            flash('Data de início inválida', 'warning')

    if data_fim:
        try:
            data_fim_dt = dt.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(Avaliacao.data_avaliacao <= data_fim_dt)
        except ValueError:
            flash('Data de fim inválida', 'warning')

    # Filtro por busca (nome do paciente)
    if busca:
        query = query.join(Paciente).filter(
            Paciente.nome.ilike(f'%{busca}%')
        )

    # Ordenar e paginar
    avaliacoes = query.order_by(db.desc(Avaliacao.data_avaliacao)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Estatísticas dos filtros
    total_filtrado = query.count()
    total_geral = Avaliacao.query.count()

    # Listas para os filtros
    pacientes = Paciente.query.filter_by(ativo=True).order_by(Paciente.nome).all()
    avaliadores = User.query.filter_by(ativo=True).order_by(User.nome_completo).all()

    return render_template('avaliacoes/listar.html',
                          avaliacoes=avaliacoes,
                          pacientes=pacientes,
                          avaliadores=avaliadores,
                          paciente_id=paciente_id,
                          avaliador_id=avaliador_id,
                          status=status,
                          data_inicio=data_inicio,
                          data_fim=data_fim,
                          busca=busca,
                          total_filtrado=total_filtrado,
                          total_geral=total_geral)

@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cria uma nova avaliação"""
    # Obter paciente_id da query string
    paciente_id = request.args.get('paciente_id', type=int)
    instrumento_id = request.args.get('instrumento_id', type=int)

    if not paciente_id and request.method == 'GET':
        flash('Selecione um paciente para iniciar a avaliação.', 'warning')
        return redirect(url_for('pacientes.listar'))

    # Criar formulário
    form = AvaliacaoForm()

    # Buscar pacientes ativos
    pacientes = Paciente.query.filter_by(ativo=True).order_by(Paciente.nome).all()
    form.paciente_id.choices = [(0, 'Selecione o paciente...')] + [
        (p.id, f"{p.nome} - {p.calcular_idade()[0]} anos") for p in pacientes
    ]

    # Buscar instrumentos disponíveis
    instrumentos_disponiveis = Instrumento.query.filter_by(ativo=True).order_by(Instrumento.nome).all()

    # Se paciente foi pré-selecionado na URL e é GET, filtrar instrumentos por idade
    if paciente_id and request.method == 'GET':
        print(f"DEBUG: Pre-selecionando paciente_id={paciente_id}")
        form.paciente_id.data = paciente_id
        print(f"DEBUG: form.paciente_id.data setado para {form.paciente_id.data}")
        paciente = Paciente.query.get(paciente_id)
        if paciente:
            idade_anos, idade_meses = paciente.calcular_idade()
            print(f"DEBUG: Paciente {paciente.nome}, idade {idade_anos} anos")
            # Filtrar instrumentos adequados para a idade
            instrumentos_disponiveis = Instrumento.query.filter(
                Instrumento.ativo.is_(True),
                Instrumento.idade_minima <= idade_anos,
                Instrumento.idade_maxima >= idade_anos
            ).all()
            print(f"DEBUG: Encontrados {len(instrumentos_disponiveis)} instrumentos adequados")

    # Popular choices de instrumentos
    form.instrumento_id.choices = [(0, 'Selecione o instrumento...')] + [
        (i.id, f"{i.nome} ({i.contexto})") for i in instrumentos_disponiveis
    ]

    # Se instrumento foi pré-selecionado
    if instrumento_id and request.method == 'GET':
        form.instrumento_id.data = instrumento_id

    if form.validate_on_submit():
        try:
            paciente = Paciente.query.get(form.paciente_id.data)
            instrumento = Instrumento.query.get(form.instrumento_id.data)

            if not paciente:
                flash('Paciente inválido!', 'danger')
                return render_template('avaliacoes/form.html', form=form, titulo='Nova Avaliação')

            if not instrumento:
                flash('Instrumento inválido!', 'danger')
                return render_template('avaliacoes/form.html', form=form, titulo='Nova Avaliação')

            # Verificar se instrumento é adequado para a idade
            idade_anos, idade_meses = paciente.calcular_idade()
            if idade_anos < instrumento.idade_minima or idade_anos > instrumento.idade_maxima:
                flash(f'Este instrumento não é adequado para a idade do paciente ({idade_anos} anos)!', 'danger')
                return render_template('avaliacoes/form.html', form=form, titulo='Nova Avaliação')

            # Criar nova avaliação
            avaliacao = Avaliacao(
                paciente_id=paciente.id,
                instrumento_id=instrumento.id,
                avaliador_id=current_user.id,
                data_avaliacao=form.data_avaliacao.data,
                relacionamento_respondente=form.relacionamento_respondente.data,
                comentarios=form.comentarios.data,
                status='em_andamento'
            )

            db.session.add(avaliacao)
            db.session.flush()  # Garantir que o ID seja gerado
            avaliacao_id = avaliacao.id
            db.session.commit()

            print(f"DEBUG: Avaliação criada com ID: {avaliacao_id}")
            flash(f'Avaliação criada com sucesso! Agora você pode responder às questões.', 'success')
            return redirect(url_for('avaliacoes.responder', id=avaliacao_id))

        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Erro ao criar avaliação: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Erro ao criar avaliação: {str(e)}', 'danger')

    return render_template('avaliacoes/form.html', form=form, titulo='Nova Avaliação')


@avaliacoes_bp.route('/<int:id>')
@login_required
@can_view_avaliacao
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

    perfil_sensorial_relatorio = None
    if avaliacao.instrumento and avaliacao.instrumento.codigo.startswith('PERFIL_SENS'):
        perfil_sensorial_relatorio = ModulosService.gerar_relatorio_perfil_sensorial(avaliacao.id)

    return render_template(
        'avaliacoes/visualizar.html',
        avaliacao=avaliacao,
        respostas_por_dominio=respostas_por_dominio,
        total_questoes=total_questoes,
        questoes_respondidas=questoes_respondidas,
        progresso=progresso,
        perfil_sensorial_relatorio=perfil_sensorial_relatorio
    )


@avaliacoes_bp.route('/<int:id>/responder', methods=['GET', 'POST'])
@login_required
@can_edit_avaliacao
def responder(id):
    """Interface para responder questões da avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)
    avaliacao_concluida = avaliacao.status == 'concluida'

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
    questao_idx = request.args.get('q', None, type=int)

    # Encontrar primeira questão não respondida
    primeira_nao_respondida = 0
    for idx, questao in enumerate(questoes):
        if questao.id not in respostas_existentes:
            primeira_nao_respondida = idx
            break

    # Se não especificado, usar primeira questão não respondida
    if questao_idx is None:
        questao_idx = primeira_nao_respondida

    # Validar índice
    if questao_idx < 0 or questao_idx >= len(questoes):
        questao_idx = 0

    questao_atual = questoes[questao_idx]
    resposta_existente = respostas_existentes.get(questao_atual.id)

    # Criar formulário
    form = RespostaForm()
    form.questao_id.data = questao_atual.id

    # Configurar opções dinamicamente conforme o instrumento
    opcao_descricoes = dict(RespostaForm.DEFAULT_DESCRIPTIONS)
    opcoes_customizadas = questao_atual.opcoes_resposta
    if isinstance(opcoes_customizadas, (list, tuple)) and opcoes_customizadas:
        choices = []
        descricoes = {}
        for raw in opcoes_customizadas:
            if '|' in raw:
                valor_opcao, label_text = raw.split('|', 1)
            else:
                valor_opcao, label_text = raw, raw

            valor_opcao = valor_opcao.strip()
            label_principal, _, complemento = label_text.partition('(')
            label_principal = label_principal.strip()
            choices.append((valor_opcao, label_principal))

            complemento = complemento.strip().rstrip(')')
            if complemento:
                descricoes[valor_opcao] = complemento

        form.valor.choices = choices
        opcao_descricoes = descricoes or dict(RespostaForm.DEFAULT_DESCRIPTIONS)
    else:
        form.valor.choices = RespostaForm.DEFAULT_CHOICES

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

            # Se avaliação já estava concluída, recalcular escores automaticamente
            if avaliacao_concluida:
                CalculoService.atualizar_escores_avaliacao(avaliacao)
                ClassificacaoService.classificar_avaliacao(avaliacao)
                flash('Resposta atualizada! Resultados recalculados.', 'success')
                return redirect(url_for('avaliacoes.responder', id=id, q=questao_idx))

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
        resposta_existente=resposta_existente,
        todas_questoes=questoes,
        primeira_nao_respondida=primeira_nao_respondida,
        respostas_existentes=respostas_existentes,
        opcao_descricoes=opcao_descricoes
    )


@avaliacoes_bp.route('/<int:id>/finalizar', methods=['GET', 'POST'])
@login_required
@can_edit_avaliacao
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
            CalculoService.atualizar_escores_avaliacao(avaliacao)

            # Classificar resultados
            ClassificacaoService.classificar_avaliacao(avaliacao)

            # Atualizar status e data de conclusão
            avaliacao.status = 'concluida'
            avaliacao.data_conclusao = datetime.utcnow()

            db.session.commit()

            flash('Avaliação finalizada com sucesso! Escores calculados e classificados.', 'success')
            return redirect(url_for('avaliacoes.visualizar', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao finalizar avaliação: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()

    return render_template('avaliacoes/finalizar.html', avaliacao=avaliacao, total_questoes=total_questoes)


@avaliacoes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@can_edit_avaliacao
def excluir(id):
    """Exclui uma avaliação"""
    avaliacao = Avaliacao.query.get_or_404(id)
    paciente_id = avaliacao.paciente_id

    # Verificar se pode excluir (apenas se não estiver concluída ou se for admin/criador)
    if avaliacao.status == 'concluida' and avaliacao.avaliador_id != current_user.id and not current_user.is_admin():
        flash('Você não pode excluir avaliações concluídas de outros usuários', 'danger')
        return redirect(url_for('avaliacoes.visualizar', id=id))

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
