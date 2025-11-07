"""
Rotas para gerenciamento de anexos de avaliações
"""
from flask import Blueprint, request, flash, redirect, url_for, send_file, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import AnexoAvaliacao, Avaliacao
from app.services.upload_service import UploadService
from app.services.permission_service import PermissionService

anexos_bp = Blueprint('anexos', __name__)


@anexos_bp.route('/upload/<int:avaliacao_id>', methods=['POST'])
@login_required
def upload(avaliacao_id):
    """Upload de arquivo para uma avaliação"""
    # Verificar se pode acessar avaliação
    if not PermissionService.pode_acessar_avaliacao(current_user, avaliacao_id):
        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': False, 'error': 'Sem permissão'}), 403
        flash('Você não tem permissão para anexar arquivos a esta avaliação', 'danger')
        return redirect(url_for('avaliacoes.listar'))

    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    # Verificar se arquivo foi enviado
    if 'arquivo' not in request.files:
        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        flash('Nenhum arquivo foi selecionado', 'warning')
        return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))

    file = request.files['arquivo']
    tipo_anexo = request.form.get('tipo_anexo', 'documento')
    descricao = request.form.get('descricao', '')

    # Salvar arquivo
    anexo, erro = UploadService.salvar_arquivo(
        file=file,
        avaliacao_id=avaliacao_id,
        usuario_id=current_user.id,
        tipo_anexo=tipo_anexo,
        descricao=descricao
    )

    if anexo:
        # Registrar na auditoria
        PermissionService.registrar_acesso(
            current_user, 'avaliacao', avaliacao_id, 'upload_anexo'
        )

        if request.is_json or request.args.get('ajax'):
            return jsonify({
                'success': True,
                'anexo': {
                    'id': anexo.id,
                    'nome': anexo.nome_original,
                    'tamanho': anexo.get_tamanho_formatado(),
                    'icone': anexo.get_icone(),
                    'data': anexo.data_upload.strftime('%d/%m/%Y %H:%M')
                }
            }), 200

        flash(f'Arquivo "{anexo.nome_original}" enviado com sucesso!', 'success')
        return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))
    else:
        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': False, 'error': erro}), 400
        flash(erro, 'danger')
        return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))


@anexos_bp.route('/download/<int:anexo_id>')
@login_required
def download(anexo_id):
    """Download de um anexo"""
    anexo = AnexoAvaliacao.query.get_or_404(anexo_id)

    # Verificar permissão para acessar a avaliação
    if not PermissionService.pode_acessar_avaliacao(current_user, anexo.avaliacao_id):
        flash('Você não tem permissão para baixar este arquivo', 'danger')
        abort(403)

    # Verificar se arquivo existe
    if not UploadService.arquivo_existe(anexo):
        flash('Arquivo não encontrado no servidor', 'danger')
        abort(404)

    # Registrar download na auditoria
    PermissionService.registrar_acesso(
        current_user, 'anexo', anexo_id, 'download'
    )

    # Enviar arquivo
    caminho = UploadService.get_caminho_arquivo(anexo)

    return send_file(
        caminho,
        as_attachment=True,
        download_name=anexo.nome_original,
        mimetype=anexo.tipo_mime
    )


@anexos_bp.route('/visualizar/<int:anexo_id>')
@login_required
def visualizar(anexo_id):
    """Visualiza um anexo inline (para PDFs e imagens)"""
    anexo = AnexoAvaliacao.query.get_or_404(anexo_id)

    # Verificar permissão
    if not PermissionService.pode_acessar_avaliacao(current_user, anexo.avaliacao_id):
        flash('Você não tem permissão para visualizar este arquivo', 'danger')
        abort(403)

    # Verificar se arquivo existe
    if not UploadService.arquivo_existe(anexo):
        flash('Arquivo não encontrado no servidor', 'danger')
        abort(404)

    # Apenas PDFs e imagens podem ser visualizados inline
    if not (anexo.is_pdf() or anexo.is_imagem()):
        flash('Este tipo de arquivo não pode ser visualizado no navegador', 'warning')
        return redirect(url_for('anexos.download', anexo_id=anexo_id))

    # Registrar visualização na auditoria
    PermissionService.registrar_acesso(
        current_user, 'anexo', anexo_id, 'visualizar'
    )

    # Enviar arquivo inline
    caminho = UploadService.get_caminho_arquivo(anexo)

    return send_file(
        caminho,
        mimetype=anexo.tipo_mime
    )


@anexos_bp.route('/excluir/<int:anexo_id>', methods=['POST'])
@login_required
def excluir(anexo_id):
    """Exclui um anexo"""
    anexo = AnexoAvaliacao.query.get_or_404(anexo_id)
    avaliacao_id = anexo.avaliacao_id

    # Verificar permissão (pode excluir se pode editar a avaliação OU se foi quem fez upload)
    pode_editar = PermissionService.pode_editar_avaliacao(current_user, avaliacao_id)
    eh_autor = anexo.usuario_id == current_user.id

    if not (pode_editar or eh_autor or current_user.is_admin()):
        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': False, 'error': 'Sem permissão'}), 403
        flash('Você não tem permissão para excluir este anexo', 'danger')
        return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))

    # Excluir anexo
    sucesso, mensagem = UploadService.excluir_anexo(anexo_id)

    if sucesso:
        # Registrar exclusão na auditoria
        PermissionService.registrar_acesso(
            current_user, 'anexo', anexo_id, 'excluir'
        )

        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': True, 'message': mensagem}), 200

        flash(mensagem, 'success')
    else:
        if request.is_json or request.args.get('ajax'):
            return jsonify({'success': False, 'error': mensagem}), 400

        flash(mensagem, 'danger')

    return redirect(url_for('avaliacoes.visualizar', id=avaliacao_id))


@anexos_bp.route('/listar/<int:avaliacao_id>')
@login_required
def listar(avaliacao_id):
    """Lista anexos de uma avaliação (API JSON)"""
    # Verificar permissão
    if not PermissionService.pode_acessar_avaliacao(current_user, avaliacao_id):
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403

    anexos = UploadService.listar_anexos_avaliacao(avaliacao_id)

    anexos_data = []
    for anexo in anexos:
        anexos_data.append({
            'id': anexo.id,
            'nome': anexo.nome_original,
            'tipo': anexo.tipo_anexo,
            'tamanho': anexo.get_tamanho_formatado(),
            'icone': anexo.get_icone(),
            'data': anexo.data_upload.strftime('%d/%m/%Y %H:%M'),
            'descricao': anexo.descricao,
            'usuario': anexo.usuario.nome_completo if anexo.usuario else 'Desconhecido',
            'is_imagem': anexo.is_imagem(),
            'is_pdf': anexo.is_pdf(),
            'pode_excluir': (
                PermissionService.pode_editar_avaliacao(current_user, avaliacao_id) or
                anexo.usuario_id == current_user.id or
                current_user.is_admin()
            )
        })

    return jsonify({'success': True, 'anexos': anexos_data}), 200
