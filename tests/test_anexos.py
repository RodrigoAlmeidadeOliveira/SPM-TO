"""
Testes para o sistema de anexos (upload, download, segurança)
"""
import pytest
import io
import os
from app.models import AnexoAvaliacao
from app.services.upload_service import UploadService
from app.services.permission_service import PermissionService


@pytest.mark.unit
class TestUploadService:
    """Testes unitários do UploadService"""

    def test_extensao_permitida_valida(self):
        """Deve aceitar extensões permitidas"""
        assert UploadService.extensao_permitida('documento.pdf') is True
        assert UploadService.extensao_permitida('imagem.jpg') is True
        assert UploadService.extensao_permitida('planilha.xlsx') is True
        assert UploadService.extensao_permitida('arquivo.zip') is True

    def test_extensao_nao_permitida(self):
        """Deve rejeitar extensões não permitidas"""
        assert UploadService.extensao_permitida('script.exe') is False
        assert UploadService.extensao_permitida('virus.bat') is False
        assert UploadService.extensao_permitida('arquivo.sh') is False
        assert UploadService.extensao_permitida('sem_extensao') is False

    def test_mime_type_permitido_valido(self):
        """Deve aceitar MIME types permitidos"""
        assert UploadService.mime_type_permitido('application/pdf') is True
        assert UploadService.mime_type_permitido('image/jpeg') is True
        assert UploadService.mime_type_permitido('application/zip') is True

    def test_mime_type_nao_permitido(self):
        """Deve rejeitar MIME types não permitidos"""
        assert UploadService.mime_type_permitido('application/x-executable') is False
        assert UploadService.mime_type_permitido('text/javascript') is False

    def test_gerar_nome_unico(self):
        """Deve gerar nome único com UUID"""
        nome1 = UploadService.gerar_nome_unico('documento.pdf')
        nome2 = UploadService.gerar_nome_unico('documento.pdf')

        # Nomes devem ser diferentes
        assert nome1 != nome2
        # Devem manter a extensão
        assert nome1.endswith('.pdf')
        assert nome2.endswith('.pdf')

    def test_validar_arquivo_vazio_rejeita(self, app):
        """Deve rejeitar arquivo vazio"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            file = FileStorage(
                stream=io.BytesIO(b''),
                filename='vazio.pdf',
                content_type='application/pdf'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is False
            assert 'vazio' in erro.lower()

    def test_validar_arquivo_muito_grande_rejeita(self, app):
        """Deve rejeitar arquivo maior que 10MB"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            # Criar arquivo de 11MB
            conteudo = b'x' * (11 * 1024 * 1024)

            file = FileStorage(
                stream=io.BytesIO(conteudo),
                filename='grande.pdf',
                content_type='application/pdf'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is False
            assert 'grande' in erro.lower() or 'tamanho' in erro.lower()

    def test_validar_arquivo_extensao_invalida_rejeita(self, app):
        """Deve rejeitar arquivo com extensão inválida"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            file = FileStorage(
                stream=io.BytesIO(b'conteudo'),
                filename='virus.exe',
                content_type='application/x-executable'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is False
            assert 'permitido' in erro.lower()

    def test_validar_arquivo_valido_aceita(self, app):
        """Deve aceitar arquivo válido"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            file = FileStorage(
                stream=io.BytesIO(b'%PDF-1.4 conteudo do pdf'),
                filename='documento.pdf',
                content_type='application/pdf'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is True
            assert erro == ''


@pytest.mark.integration
class TestAnexoModel:
    """Testes do modelo AnexoAvaliacao"""

    def test_get_extensao(self, db_session, avaliacao, terapeuta_user):
        """Deve extrair extensão do nome original"""
        anexo = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='documento.pdf',
            nome_arquivo='uuid.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=1024
        )

        assert anexo.get_extensao() == 'pdf'

    def test_is_imagem(self, db_session, avaliacao, terapeuta_user):
        """Deve identificar imagens corretamente"""
        anexo_imagem = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='foto.jpg',
            nome_arquivo='uuid.jpg',
            tipo_mime='image/jpeg',
            tamanho_bytes=1024
        )

        anexo_pdf = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='doc.pdf',
            nome_arquivo='uuid.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=1024
        )

        assert anexo_imagem.is_imagem() is True
        assert anexo_pdf.is_imagem() is False

    def test_is_pdf(self, db_session, avaliacao, terapeuta_user):
        """Deve identificar PDFs corretamente"""
        anexo_pdf = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='documento.pdf',
            nome_arquivo='uuid.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=1024
        )

        anexo_imagem = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='foto.jpg',
            nome_arquivo='uuid.jpg',
            tipo_mime='image/jpeg',
            tamanho_bytes=1024
        )

        assert anexo_pdf.is_pdf() is True
        assert anexo_imagem.is_pdf() is False

    def test_get_tamanho_formatado(self, db_session, avaliacao, terapeuta_user):
        """Deve formatar tamanho em bytes/KB/MB"""
        anexo_bytes = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='pequeno.txt',
            nome_arquivo='uuid.txt',
            tipo_mime='text/plain',
            tamanho_bytes=512
        )

        anexo_kb = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='medio.pdf',
            nome_arquivo='uuid.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=50 * 1024
        )

        anexo_mb = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='grande.zip',
            nome_arquivo='uuid.zip',
            tipo_mime='application/zip',
            tamanho_bytes=5 * 1024 * 1024
        )

        assert 'B' in anexo_bytes.get_tamanho_formatado()
        assert 'KB' in anexo_kb.get_tamanho_formatado()
        assert 'MB' in anexo_mb.get_tamanho_formatado()

    def test_get_icone(self, db_session, avaliacao, terapeuta_user):
        """Deve retornar ícone FontAwesome baseado no tipo"""
        anexo_pdf = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='doc.pdf',
            nome_arquivo='uuid.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=1024
        )

        anexo_imagem = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='foto.jpg',
            nome_arquivo='uuid.jpg',
            tipo_mime='image/jpeg',
            tamanho_bytes=1024
        )

        assert 'pdf' in anexo_pdf.get_icone()
        assert 'image' in anexo_imagem.get_icone()


@pytest.mark.functional
class TestAnexoRoutes:
    """Testes funcionais das rotas de anexos"""

    def test_upload_arquivo_valido(self, logged_terapeuta, db_session, avaliacao, app):
        """Deve permitir upload de arquivo válido"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            # Criar arquivo fake
            file_data = io.BytesIO(b'%PDF-1.4 conteudo do pdf')
            file_data.seek(0)

            data = {
                'arquivo': (file_data, 'laudo.pdf'),
                'tipo_anexo': 'laudo',
                'descricao': 'Laudo médico'
            }

            response = logged_terapeuta.post(
                f'/anexos/upload/{avaliacao.id}',
                data=data,
                content_type='multipart/form-data',
                follow_redirects=True
            )

            assert response.status_code == 200

            # Verificar que anexo foi criado
            anexo = AnexoAvaliacao.query.filter_by(avaliacao_id=avaliacao.id).first()
            assert anexo is not None
            assert anexo.nome_original == 'laudo.pdf'
            assert anexo.tipo_anexo == 'laudo'

    def test_upload_sem_arquivo_rejeita(self, logged_terapeuta, db_session, avaliacao):
        """Deve rejeitar upload sem arquivo"""
        response = logged_terapeuta.post(
            f'/anexos/upload/{avaliacao.id}',
            data={'tipo_anexo': 'documento'},
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'arquivo' in response.data.lower() or b'selecionado' in response.data.lower()

    def test_upload_sem_permissao_negado(self, logged_professor, db_session, terapeuta_user, instrumento, app):
        """Não deve permitir upload em avaliação sem permissão"""
        from app.models import Paciente, Avaliacao

        # Criar paciente e avaliação do terapeuta
        paciente = Paciente(nome='Privado', identificacao='PRIV', data_nascimento='2015-01-01',
                           sexo='M', criador_id=terapeuta_user.id)
        db_session.add(paciente)
        db_session.commit()

        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            instrumento_id=instrumento.id,
            avaliador_id=terapeuta_user.id,
            data_avaliacao='2023-01-01',
            status='em_andamento'
        )
        db_session.add(avaliacao)
        db_session.commit()

        with app.app_context():
            from werkzeug.datastructures import FileStorage

            file_data = io.BytesIO(b'conteudo')
            data = {'arquivo': (file_data, 'doc.pdf')}

            response = logged_professor.post(
                f'/anexos/upload/{avaliacao.id}',
                data=data,
                content_type='multipart/form-data'
            )

            assert response.status_code in [302, 403]

    def test_download_anexo_com_permissao(self, logged_terapeuta, db_session, avaliacao, terapeuta_user, app):
        """Deve permitir download de anexo com permissão"""
        with app.app_context():
            # Criar anexo
            upload_folder = UploadService.get_upload_folder()
            nome_arquivo = 'test-uuid.pdf'
            caminho = os.path.join(upload_folder, nome_arquivo)

            # Salvar arquivo físico
            with open(caminho, 'wb') as f:
                f.write(b'%PDF-1.4 conteudo')

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='documento.pdf',
                nome_arquivo=nome_arquivo,
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            response = logged_terapeuta.get(f'/anexos/download/{anexo.id}')
            assert response.status_code == 200

            # Limpar arquivo
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_download_sem_permissao_negado(self, logged_professor, db_session, terapeuta_user, instrumento, app):
        """Não deve permitir download de anexo sem permissão"""
        from app.models import Paciente, Avaliacao

        with app.app_context():
            # Criar paciente e avaliação do terapeuta
            paciente = Paciente(nome='Privado', identificacao='PRIV', data_nascimento='2015-01-01',
                               sexo='M', criador_id=terapeuta_user.id)
            db_session.add(paciente)
            db_session.commit()

            avaliacao = Avaliacao(
                paciente_id=paciente.id,
                instrumento_id=instrumento.id,
                avaliador_id=terapeuta_user.id,
                data_avaliacao='2023-01-01',
                status='em_andamento'
            )
            db_session.add(avaliacao)
            db_session.commit()

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='privado.pdf',
                nome_arquivo='uuid.pdf',
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            response = logged_professor.get(f'/anexos/download/{anexo.id}')
            assert response.status_code in [302, 403]

    def test_visualizar_pdf_inline(self, logged_terapeuta, db_session, avaliacao, terapeuta_user, app):
        """Deve permitir visualizar PDF inline"""
        with app.app_context():
            # Criar anexo PDF
            upload_folder = UploadService.get_upload_folder()
            nome_arquivo = 'test-pdf.pdf'
            caminho = os.path.join(upload_folder, nome_arquivo)

            with open(caminho, 'wb') as f:
                f.write(b'%PDF-1.4 conteudo')

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='documento.pdf',
                nome_arquivo=nome_arquivo,
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            response = logged_terapeuta.get(f'/anexos/visualizar/{anexo.id}')
            assert response.status_code == 200

            # Limpar
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_visualizar_imagem_inline(self, logged_terapeuta, db_session, avaliacao, terapeuta_user, app):
        """Deve permitir visualizar imagem inline"""
        with app.app_context():
            # Criar anexo de imagem
            upload_folder = UploadService.get_upload_folder()
            nome_arquivo = 'test-image.jpg'
            caminho = os.path.join(upload_folder, nome_arquivo)

            # Criar imagem fake (JPEG mínimo)
            with open(caminho, 'wb') as f:
                f.write(b'\xFF\xD8\xFF\xE0' + b'\x00' * 100)

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='foto.jpg',
                nome_arquivo=nome_arquivo,
                tipo_mime='image/jpeg',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            response = logged_terapeuta.get(f'/anexos/visualizar/{anexo.id}')
            assert response.status_code == 200

            # Limpar
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_excluir_anexo_proprio(self, logged_terapeuta, db_session, avaliacao, terapeuta_user, app):
        """Deve permitir excluir anexo que o próprio usuário fez upload"""
        with app.app_context():
            # Criar anexo
            upload_folder = UploadService.get_upload_folder()
            nome_arquivo = 'test-delete.pdf'
            caminho = os.path.join(upload_folder, nome_arquivo)

            with open(caminho, 'wb') as f:
                f.write(b'conteudo')

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='delete.pdf',
                nome_arquivo=nome_arquivo,
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()
            anexo_id = anexo.id

            response = logged_terapeuta.post(
                f'/anexos/excluir/{anexo_id}',
                follow_redirects=True
            )

            assert response.status_code == 200

            # Verificar que foi excluído
            anexo_excluido = AnexoAvaliacao.query.get(anexo_id)
            assert anexo_excluido is None

    def test_excluir_anexo_de_outro_negado(self, logged_professor, db_session, avaliacao, terapeuta_user, app):
        """Não deve permitir excluir anexo de outro usuário sem permissão"""
        with app.app_context():
            # Criar anexo do terapeuta
            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='privado.pdf',
                nome_arquivo='uuid.pdf',
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            response = logged_professor.post(f'/anexos/excluir/{anexo.id}')
            assert response.status_code in [302, 403]

    def test_listar_anexos_json(self, logged_terapeuta, db_session, avaliacao, terapeuta_user):
        """Deve retornar lista de anexos em JSON"""
        # Criar alguns anexos
        anexo1 = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='doc1.pdf',
            nome_arquivo='uuid1.pdf',
            tipo_mime='application/pdf',
            tamanho_bytes=1024
        )
        anexo2 = AnexoAvaliacao(
            avaliacao_id=avaliacao.id,
            usuario_id=terapeuta_user.id,
            nome_original='foto.jpg',
            nome_arquivo='uuid2.jpg',
            tipo_mime='image/jpeg',
            tamanho_bytes=2048
        )

        db_session.add_all([anexo1, anexo2])
        db_session.commit()

        response = logged_terapeuta.get(f'/anexos/listar/{avaliacao.id}')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert data['success'] is True
        assert len(data['anexos']) == 2


@pytest.mark.security
class TestAnexoSecurity:
    """Testes de segurança do sistema de anexos"""

    def test_path_traversal_bloqueado(self, app):
        """Deve bloquear tentativas de path traversal"""
        with app.app_context():
            from werkzeug.utils import secure_filename

            # Tentar path traversal
            filename_malicioso = '../../../etc/passwd'
            nome_seguro = secure_filename(filename_malicioso)

            # secure_filename deve remover caracteres perigosos
            assert '..' not in nome_seguro
            assert '/' not in nome_seguro

    def test_extensao_dupla_bloqueada(self, app):
        """Deve validar extensão mesmo com dupla extensão"""
        with app.app_context():
            # Arquivo com dupla extensão
            valido = UploadService.extensao_permitida('imagem.jpg.exe')
            # Deve verificar a última extensão (.exe)
            assert valido is False

    def test_tamanho_maximo_enforced(self, app):
        """Deve enforçar tamanho máximo de 10MB"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            # Arquivo de 11MB
            conteudo_grande = b'x' * (11 * 1024 * 1024)

            file = FileStorage(
                stream=io.BytesIO(conteudo_grande),
                filename='grande.pdf',
                content_type='application/pdf'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is False

    def test_mime_type_verificado(self, app):
        """Deve verificar MIME type além da extensão"""
        with app.app_context():
            from werkzeug.datastructures import FileStorage

            # Arquivo com extensão .pdf mas MIME type errado
            file = FileStorage(
                stream=io.BytesIO(b'conteudo'),
                filename='fake.pdf',
                content_type='application/x-executable'
            )

            valido, erro = UploadService.validar_arquivo(file)
            assert valido is False

    def test_nomes_unicos_previnem_conflito(self):
        """UUID deve prevenir conflitos de nomes"""
        nomes = set()

        # Gerar 100 nomes para o mesmo arquivo
        for _ in range(100):
            nome = UploadService.gerar_nome_unico('teste.pdf')
            nomes.add(nome)

        # Todos devem ser únicos
        assert len(nomes) == 100

    def test_auditoria_registrada_ao_acessar(self, logged_terapeuta, db_session, avaliacao, terapeuta_user, app):
        """Deve registrar acesso na auditoria"""
        from app.models import AuditoriaAcesso

        with app.app_context():
            # Criar anexo
            upload_folder = UploadService.get_upload_folder()
            nome_arquivo = 'audit-test.pdf'
            caminho = os.path.join(upload_folder, nome_arquivo)

            with open(caminho, 'wb') as f:
                f.write(b'conteudo')

            anexo = AnexoAvaliacao(
                avaliacao_id=avaliacao.id,
                usuario_id=terapeuta_user.id,
                nome_original='audit.pdf',
                nome_arquivo=nome_arquivo,
                tipo_mime='application/pdf',
                tamanho_bytes=100
            )
            db_session.add(anexo)
            db_session.commit()

            # Download
            logged_terapeuta.get(f'/anexos/download/{anexo.id}')

            # Verificar auditoria
            auditoria = AuditoriaAcesso.query.filter_by(
                user_id=terapeuta_user.id,
                recurso_tipo='anexo',
                recurso_id=anexo.id,
                acao='download'
            ).first()

            assert auditoria is not None

            # Limpar
            if os.path.exists(caminho):
                os.remove(caminho)
