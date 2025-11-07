"""
Service para gerenciamento de uploads de arquivos
"""
import os
import uuid
import io
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
from app import db
from app.models.anexo import AnexoAvaliacao


class UploadService:
    """Service para gerenciar uploads de arquivos com segurança"""

    # Extensões permitidas por categoria
    EXTENSOES_PERMITIDAS = {
        'imagem': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'},
        'documento': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
        'planilha': {'xls', 'xlsx', 'csv'},
        'compactado': {'zip', 'rar', '7z'}
    }

    # Tamanho máximo: 10MB
    TAMANHO_MAXIMO = 10 * 1024 * 1024

    # Tipos MIME permitidos
    MIME_TYPES_PERMITIDOS = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/rtf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        'application/zip',
        'application/x-rar-compressed',
        'application/x-7z-compressed'
    }

    @staticmethod
    def get_upload_folder():
        """Retorna o diretório de uploads"""
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(current_app.root_path, '..', upload_folder)

        # Criar diretório se não existir
        os.makedirs(upload_folder, exist_ok=True)

        return upload_folder

    @staticmethod
    def extensao_permitida(filename):
        """Verifica se a extensão do arquivo é permitida"""
        if '.' not in filename:
            return False

        extensao = filename.rsplit('.', 1)[1].lower()

        todas_extensoes = set()
        for exts in UploadService.EXTENSOES_PERMITIDAS.values():
            todas_extensoes.update(exts)

        return extensao in todas_extensoes

    @staticmethod
    def mime_type_permitido(mime_type):
        """Verifica se o MIME type é permitido"""
        return mime_type in UploadService.MIME_TYPES_PERMITIDOS

    @staticmethod
    def gerar_nome_unico(filename):
        """Gera um nome único para o arquivo"""
        # Pegar extensão original
        extensao = ''
        if '.' in filename:
            extensao = '.' + filename.rsplit('.', 1)[1].lower()

        # Gerar UUID único
        nome_unico = str(uuid.uuid4()) + extensao

        return nome_unico

    @staticmethod
    def validar_arquivo(file):
        """
        Valida um arquivo enviado

        Args:
            file: FileStorage object do Flask

        Returns:
            tuple: (valido: bool, mensagem_erro: str)
        """
        # Verificar se arquivo foi enviado
        if not file or not file.filename:
            return False, 'Nenhum arquivo foi enviado'

        # Verificar nome do arquivo
        if file.filename == '':
            return False, 'Nome de arquivo inválido'

        # Verificar extensão
        if not UploadService.extensao_permitida(file.filename):
            return False, f'Tipo de arquivo não permitido. Extensões aceitas: {", ".join(sorted(set().union(*UploadService.EXTENSOES_PERMITIDAS.values())))}'

        # Verificar MIME type
        if not UploadService.mime_type_permitido(file.content_type):
            return False, f'Tipo de arquivo não permitido: {file.content_type}'

        # Verificar tamanho (se possível)
        file.seek(0, os.SEEK_END)
        tamanho = file.tell()
        file.seek(0)  # Reset para o início

        if tamanho > UploadService.TAMANHO_MAXIMO:
            tamanho_mb = UploadService.TAMANHO_MAXIMO / (1024 * 1024)
            return False, f'Arquivo muito grande. Tamanho máximo: {tamanho_mb:.0f}MB'

        if tamanho == 0:
            return False, 'Arquivo vazio'

        return True, ''

    @staticmethod
    def salvar_arquivo(file, avaliacao_id, usuario_id, tipo_anexo='documento', descricao=None):
        """
        Salva um arquivo no sistema

        Args:
            file: FileStorage object
            avaliacao_id: ID da avaliação
            usuario_id: ID do usuário fazendo upload
            tipo_anexo: Tipo do anexo ('laudo', 'foto', 'documento', etc)
            descricao: Descrição opcional

        Returns:
            tuple: (AnexoAvaliacao ou None, mensagem_erro: str)
        """
        try:
            # Validar arquivo
            valido, erro = UploadService.validar_arquivo(file)
            if not valido:
                return None, erro

            # Gerar nome único
            nome_original = secure_filename(file.filename)
            nome_arquivo = UploadService.gerar_nome_unico(nome_original)

            # Verificar se é imagem e comprimir se necessário
            extensao = nome_original.rsplit('.', 1)[1].lower() if '.' in nome_original else ''
            eh_imagem = extensao in {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}

            upload_folder = UploadService.get_upload_folder()
            caminho_completo = os.path.join(upload_folder, nome_arquivo)

            if eh_imagem:
                # Tentar comprimir imagem
                imagem_comprimida, tamanho_original, tamanho_final = UploadService.comprimir_imagem(file)

                if imagem_comprimida:
                    # Salvar imagem comprimida
                    with open(caminho_completo, 'wb') as f:
                        f.write(imagem_comprimida)
                    tamanho_bytes = tamanho_final
                    print(f"Imagem comprimida: {tamanho_original} -> {tamanho_final} bytes ({100 - int(tamanho_final/tamanho_original*100)}% redução)")
                else:
                    # Salvar imagem original
                    file.seek(0)
                    file.save(caminho_completo)
                    file.seek(0, os.SEEK_END)
                    tamanho_bytes = file.tell()
                    file.seek(0)
            else:
                # Não é imagem, salvar normalmente
                file.seek(0, os.SEEK_END)
                tamanho_bytes = file.tell()
                file.seek(0)
                file.save(caminho_completo)

            # Criar registro no banco
            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao_id,
                usuario_id=usuario_id,
                nome_original=nome_original,
                nome_arquivo=nome_arquivo,
                tipo_mime=file.content_type,
                tamanho_bytes=tamanho_bytes,
                tipo_anexo=tipo_anexo,
                descricao=descricao
            )

            db.session.add(anexo)
            db.session.commit()

            return anexo, ''

        except Exception as e:
            db.session.rollback()
            # Tentar remover arquivo se foi salvo
            try:
                if 'caminho_completo' in locals() and os.path.exists(caminho_completo):
                    os.remove(caminho_completo)
            except:
                pass

            return None, f'Erro ao salvar arquivo: {str(e)}'

    @staticmethod
    def excluir_anexo(anexo_id):
        """
        Exclui um anexo (arquivo + registro)

        Args:
            anexo_id: ID do anexo

        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            anexo = AnexoAvaliacao.query.get(anexo_id)

            if not anexo:
                return False, 'Anexo não encontrado'

            # Remover arquivo do disco
            upload_folder = UploadService.get_upload_folder()
            caminho_arquivo = os.path.join(upload_folder, anexo.nome_arquivo)

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            # Remover registro do banco
            db.session.delete(anexo)
            db.session.commit()

            return True, 'Anexo excluído com sucesso'

        except Exception as e:
            db.session.rollback()
            return False, f'Erro ao excluir anexo: {str(e)}'

    @staticmethod
    def get_caminho_arquivo(anexo):
        """
        Retorna o caminho completo do arquivo no disco

        Args:
            anexo: AnexoAvaliacao object

        Returns:
            str: Caminho completo do arquivo
        """
        upload_folder = UploadService.get_upload_folder()
        return os.path.join(upload_folder, anexo.nome_arquivo)

    @staticmethod
    def arquivo_existe(anexo):
        """
        Verifica se o arquivo físico existe

        Args:
            anexo: AnexoAvaliacao object

        Returns:
            bool: True se existe, False caso contrário
        """
        caminho = UploadService.get_caminho_arquivo(anexo)
        return os.path.exists(caminho)

    @staticmethod
    def listar_anexos_avaliacao(avaliacao_id):
        """
        Lista todos os anexos de uma avaliação

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            list: Lista de AnexoAvaliacao objects
        """
        return AnexoAvaliacao.query.filter_by(
            avaliacao_id=avaliacao_id,
            ativo=True
        ).order_by(AnexoAvaliacao.data_upload.desc()).all()

    @staticmethod
    def contar_anexos_avaliacao(avaliacao_id):
        """
        Conta anexos de uma avaliação

        Args:
            avaliacao_id: ID da avaliação

        Returns:
            int: Número de anexos
        """
        return AnexoAvaliacao.query.filter_by(
            avaliacao_id=avaliacao_id,
            ativo=True
        ).count()

    @staticmethod
    def comprimir_imagem(file, qualidade=85, max_dimensao=1920):
        """
        Comprime uma imagem mantendo qualidade aceitável
        
        Args:
            file: FileStorage object com a imagem
            qualidade: Qualidade de compressão (1-100), padrão 85
            max_dimensao: Dimensão máxima em pixels, padrão 1920px
            
        Returns:
            tuple: (arquivo_comprimido_bytes, tamanho_original, tamanho_final)
        """
        try:
            # Verificar se é imagem
            extensao = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if extensao not in {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}:
                return None, 0, 0
            
            # Obter tamanho original
            file.seek(0, os.SEEK_END)
            tamanho_original = file.tell()
            file.seek(0)
            
            # Abrir imagem com Pillow
            img = Image.open(file)
            
            # Converter RGBA para RGB se necessário (para salvar como JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionar se necessário
            if max(img.size) > max_dimensao:
                ratio = max_dimensao / max(img.size)
                nova_largura = int(img.width * ratio)
                nova_altura = int(img.height * ratio)
                img = img.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
            
            # Salvar em buffer com compressão
            buffer = io.BytesIO()
            
            # Formato de saída
            formato = 'JPEG'
            if extensao == 'png' and img.mode in ('RGBA', 'LA', 'P'):
                formato = 'PNG'
                img.save(buffer, format=formato, optimize=True, compress_level=6)
            elif extensao == 'webp':
                formato = 'WEBP'
                img.save(buffer, format=formato, quality=qualidade, method=6)
            else:
                # Para JPEG e outros, converter para JPEG
                img.save(buffer, format=formato, quality=qualidade, optimize=True)
            
            # Obter bytes comprimidos
            buffer.seek(0)
            imagem_comprimida = buffer.getvalue()
            tamanho_final = len(imagem_comprimida)
            
            # Só retornar comprimida se realmente reduziu
            if tamanho_final < tamanho_original:
                return imagem_comprimida, tamanho_original, tamanho_final
            else:
                file.seek(0)
                return None, tamanho_original, tamanho_original
                
        except Exception as e:
            print(f"Erro ao comprimir imagem: {e}")
            file.seek(0)
            return None, 0, 0

    @staticmethod
    def gerar_thumbnail(anexo, tamanho=(300, 300)):
        """
        Gera thumbnail de uma imagem
        
        Args:
            anexo: AnexoAvaliacao object
            tamanho: Tupla (largura, altura) do thumbnail
            
        Returns:
            str: Caminho do thumbnail ou None se erro
        """
        try:
            if not anexo.is_imagem():
                return None
            
            caminho_original = UploadService.get_caminho_arquivo(anexo)
            
            if not os.path.exists(caminho_original):
                return None
            
            # Nome do thumbnail
            nome_base, ext = os.path.splitext(anexo.nome_arquivo)
            nome_thumbnail = f"{nome_base}_thumb{ext}"
            
            upload_folder = UploadService.get_upload_folder()
            caminho_thumbnail = os.path.join(upload_folder, nome_thumbnail)
            
            # Se já existe, retornar
            if os.path.exists(caminho_thumbnail):
                return caminho_thumbnail
            
            # Criar thumbnail
            img = Image.open(caminho_original)
            img.thumbnail(tamanho, Image.Resampling.LANCZOS)
            img.save(caminho_thumbnail, optimize=True, quality=85)
            
            return caminho_thumbnail
            
        except Exception as e:
            print(f"Erro ao gerar thumbnail: {e}")
            return None
