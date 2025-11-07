"""
Modelo de Anexo de Avaliação
"""
from datetime import datetime
from app import db


class AnexoAvaliacao(db.Model):
    """Modelo para anexos de avaliações (PDFs, imagens, documentos)"""
    __tablename__ = 'anexos_avaliacao'

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamento com avaliação
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacoes.id', ondelete='CASCADE'), nullable=False, index=True)

    # Quem fez o upload
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Informações do arquivo
    nome_original = db.Column(db.String(255), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False, unique=True)  # Nome único no storage
    tipo_mime = db.Column(db.String(100), nullable=False)
    tamanho_bytes = db.Column(db.Integer, nullable=False)

    # Tipo de anexo
    tipo_anexo = db.Column(db.String(50), nullable=False, default='documento')
    # 'laudo', 'foto', 'documento', 'relatorio', 'outro'

    # Descrição opcional
    descricao = db.Column(db.Text)

    # Metadados
    data_upload = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamentos
    avaliacao = db.relationship('Avaliacao', backref=db.backref('anexos', lazy='dynamic', cascade='all, delete-orphan'))
    usuario = db.relationship('User', backref='uploads_realizados')

    def __repr__(self):
        return f'<AnexoAvaliacao {self.nome_original}>'

    def get_extensao(self):
        """Retorna a extensão do arquivo"""
        return self.nome_original.rsplit('.', 1)[-1].lower() if '.' in self.nome_original else ''

    def is_imagem(self):
        """Verifica se é uma imagem"""
        extensoes_imagem = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.get_extensao() in extensoes_imagem

    def is_pdf(self):
        """Verifica se é PDF"""
        return self.get_extensao() == 'pdf'

    def get_tamanho_formatado(self):
        """Retorna tamanho formatado (KB, MB)"""
        if self.tamanho_bytes < 1024:
            return f'{self.tamanho_bytes} B'
        elif self.tamanho_bytes < 1024 * 1024:
            return f'{self.tamanho_bytes / 1024:.1f} KB'
        else:
            return f'{self.tamanho_bytes / (1024 * 1024):.1f} MB'

    def get_icone(self):
        """Retorna ícone FontAwesome baseado no tipo"""
        extensao = self.get_extensao()

        icones = {
            'pdf': 'fa-file-pdf text-danger',
            'doc': 'fa-file-word text-primary',
            'docx': 'fa-file-word text-primary',
            'xls': 'fa-file-excel text-success',
            'xlsx': 'fa-file-excel text-success',
            'jpg': 'fa-file-image text-info',
            'jpeg': 'fa-file-image text-info',
            'png': 'fa-file-image text-info',
            'gif': 'fa-file-image text-info',
            'zip': 'fa-file-archive text-warning',
            'rar': 'fa-file-archive text-warning',
        }

        return icones.get(extensao, 'fa-file text-secondary')
