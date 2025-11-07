"""
Service para controle de permissões e acesso a recursos
"""
from flask import request
from sqlalchemy import or_
from app import db
from app.models import Paciente, Avaliacao, AuditoriaAcesso, CompartilhamentoPaciente, User
from app.models.paciente import paciente_responsavel


class PermissionService:
    """Service para gerenciar permissões de acesso"""

    @staticmethod
    def pode_acessar_paciente(user, paciente_id):
        """
        Verifica se o usuário pode acessar um paciente

        Regras:
        - Admin: acessa tudo
        - Criador do paciente: acessa sempre
        - Responsável vinculado: acessa se estiver na tabela paciente_responsavel
        - Avaliador: acessa se tiver feito alguma avaliação do paciente

        Args:
            user: Usuário atual
            paciente_id: ID do paciente

        Returns:
            bool: True se pode acessar, False caso contrário
        """
        if not user or not user.is_authenticated:
            return False

        # Admin acessa tudo
        if user.is_admin():
            return True

        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return False

        # Criador do paciente
        if paciente.criador_id == user.id:
            return True

        # Verifica se é responsável vinculado
        vinculo = db.session.query(paciente_responsavel).filter_by(
            paciente_id=paciente_id,
            user_id=user.id
        ).first()

        if vinculo:
            return True

        # Verifica se já fez alguma avaliação deste paciente
        avaliacao = Avaliacao.query.filter_by(
            paciente_id=paciente_id,
            avaliador_id=user.id
        ).first()

        if avaliacao:
            return True

        # Verifica compartilhamentos ativos
        compartilhamento = CompartilhamentoPaciente.query.filter_by(
            paciente_id=paciente_id,
            recebeu_user_id=user.id,
            ativo=True
        ).first()

        return compartilhamento is not None

    @staticmethod
    def pode_editar_paciente(user, paciente_id):
        """
        Verifica se o usuário pode editar um paciente

        Regras:
        - Admin: edita tudo
        - Criador: edita sempre
        - Responsável vinculado como terapeuta: pode editar
        - Compartilhamento com acesso 'edicao' ou 'completo': pode editar

        Args:
            user: Usuário atual
            paciente_id: ID do paciente

        Returns:
            bool: True se pode editar, False caso contrário
        """
        if not user or not user.is_authenticated:
            return False

        # Admin edita tudo
        if user.is_admin():
            return True

        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return False

        # Criador pode editar
        if paciente.criador_id == user.id:
            return True

        # Verifica se é responsável vinculado
        vinculo = db.session.query(paciente_responsavel).filter_by(
            paciente_id=paciente_id,
            user_id=user.id
        ).first()

        if vinculo:
            return True

        # Verifica compartilhamento com permissão de edição
        compartilhamento = CompartilhamentoPaciente.query.filter_by(
            paciente_id=paciente_id,
            recebeu_user_id=user.id,
            ativo=True
        ).filter(CompartilhamentoPaciente.tipo_acesso.in_(['edicao', 'completo'])).first()

        return compartilhamento is not None

    @staticmethod
    def pode_excluir_paciente(user, paciente_id):
        """
        Verifica se o usuário pode excluir um paciente

        Regras:
        - Admin: exclui tudo
        - Criador: exclui se não houver avaliações de outros usuários
        - Compartilhamento 'completo': pode excluir

        Args:
            user: Usuário atual
            paciente_id: ID do paciente

        Returns:
            bool: True se pode excluir, False caso contrário
        """
        if not user or not user.is_authenticated:
            return False

        # Admin exclui tudo
        if user.is_admin():
            return True

        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return False

        # Criador pode excluir se não houver avaliações de outros
        if paciente.criador_id == user.id:
            outras_avaliacoes = Avaliacao.query.filter(
                Avaliacao.paciente_id == paciente_id,
                Avaliacao.avaliador_id != user.id
            ).first()
            return outras_avaliacoes is None

        # Compartilhamento completo pode excluir
        compartilhamento = CompartilhamentoPaciente.query.filter_by(
            paciente_id=paciente_id,
            recebeu_user_id=user.id,
            ativo=True,
            tipo_acesso='completo'
        ).first()

        return compartilhamento is not None

    @staticmethod
    def filtrar_pacientes_por_permissao(query, user):
        """
        Filtra query de pacientes baseado nas permissões do usuário

        Args:
            query: Query do SQLAlchemy
            user: Usuário atual

        Returns:
            Query filtrada
        """
        if not user or not user.is_authenticated:
            return query.filter(False)  # Retorna query vazia

        # Admin vê tudo
        if user.is_admin():
            return query

        # Construir filtro composto
        # 1. Pacientes criados pelo usuário
        filtro = (Paciente.criador_id == user.id)

        # 2. Pacientes vinculados
        pacientes_vinculados = db.session.query(paciente_responsavel.c.paciente_id).filter(
            paciente_responsavel.c.user_id == user.id
        ).subquery()

        filtro = or_(
            filtro,
            Paciente.id.in_(pacientes_vinculados)
        )

        # 3. Pacientes com avaliações feitas pelo usuário
        pacientes_avaliados = db.session.query(Avaliacao.paciente_id.distinct()).filter(
            Avaliacao.avaliador_id == user.id
        ).subquery()

        filtro = or_(
            filtro,
            Paciente.id.in_(pacientes_avaliados)
        )

        # 4. Pacientes compartilhados ativos
        pacientes_compartilhados = db.session.query(CompartilhamentoPaciente.paciente_id).filter(
            CompartilhamentoPaciente.recebeu_user_id == user.id,
            CompartilhamentoPaciente.ativo == True
        ).subquery()

        filtro = or_(
            filtro,
            Paciente.id.in_(pacientes_compartilhados)
        )

        return query.filter(filtro)

    @staticmethod
    def pode_acessar_avaliacao(user, avaliacao_id):
        """
        Verifica se o usuário pode acessar uma avaliação

        Regras:
        - Se pode acessar o paciente, pode acessar suas avaliações

        Args:
            user: Usuário atual
            avaliacao_id: ID da avaliação

        Returns:
            bool: True se pode acessar, False caso contrário
        """
        if not user or not user.is_authenticated:
            return False

        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao:
            return False

        return PermissionService.pode_acessar_paciente(user, avaliacao.paciente_id)

    @staticmethod
    def pode_editar_avaliacao(user, avaliacao_id):
        """
        Verifica se o usuário pode editar uma avaliação

        Regras:
        - Admin: edita tudo
        - Avaliador que criou: pode editar se status não for 'concluida'
        - Pode editar paciente E avaliação não concluída: pode editar

        Args:
            user: Usuário atual
            avaliacao_id: ID da avaliação

        Returns:
            bool: True se pode editar, False caso contrário
        """
        if not user or not user.is_authenticated:
            return False

        # Admin edita tudo
        if user.is_admin():
            return True

        avaliacao = Avaliacao.query.get(avaliacao_id)
        if not avaliacao:
            return False

        # Avaliador que criou pode editar se não concluída
        if avaliacao.avaliador_id == user.id and avaliacao.status != 'concluida':
            return True

        # Se pode editar paciente e avaliação não concluída
        if avaliacao.status != 'concluida':
            return PermissionService.pode_editar_paciente(user, avaliacao.paciente_id)

        return False

    @staticmethod
    def registrar_acesso(user, recurso_tipo, recurso_id, acao):
        """
        Registra um acesso na tabela de auditoria

        Args:
            user: Usuário que acessou
            recurso_tipo: Tipo do recurso ('paciente', 'avaliacao', 'relatorio')
            recurso_id: ID do recurso
            acao: Ação realizada ('visualizar', 'editar', 'excluir', 'criar', 'exportar')
        """
        try:
            auditoria = AuditoriaAcesso(
                user_id=user.id if user and user.is_authenticated else None,
                recurso_tipo=recurso_tipo,
                recurso_id=recurso_id,
                acao=acao,
                ip_address=request.remote_addr if request else None,
                user_agent=request.user_agent.string if request and request.user_agent else None
            )
            db.session.add(auditoria)
            db.session.commit()
        except Exception as e:
            # Não deve quebrar a aplicação se auditoria falhar
            db.session.rollback()
            print(f"Erro ao registrar auditoria: {e}")

    @staticmethod
    def vincular_responsavel(paciente_id, user_id, tipo_vinculo='terapeuta'):
        """
        Vincula um responsável a um paciente

        Args:
            paciente_id: ID do paciente
            user_id: ID do usuário a vincular
            tipo_vinculo: Tipo de vínculo ('terapeuta', 'professor', 'familiar')

        Returns:
            bool: True se vinculado com sucesso
        """
        try:
            # Verifica se já existe vínculo
            vinculo_existente = db.session.query(paciente_responsavel).filter_by(
                paciente_id=paciente_id,
                user_id=user_id
            ).first()

            if vinculo_existente:
                return True  # Já vinculado

            # Inserir vínculo
            stmt = paciente_responsavel.insert().values(
                paciente_id=paciente_id,
                user_id=user_id,
                tipo_vinculo=tipo_vinculo
            )
            db.session.execute(stmt)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao vincular responsável: {e}")
            return False

    @staticmethod
    def desvincular_responsavel(paciente_id, user_id):
        """
        Remove vínculo entre responsável e paciente

        Args:
            paciente_id: ID do paciente
            user_id: ID do usuário a desvincular

        Returns:
            bool: True se desvinculado com sucesso
        """
        try:
            stmt = paciente_responsavel.delete().where(
                paciente_responsavel.c.paciente_id == paciente_id,
                paciente_responsavel.c.user_id == user_id
            )
            db.session.execute(stmt)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao desvincular responsável: {e}")
            return False

    @staticmethod
    def compartilhar_paciente(paciente_id, compartilhou_user_id, recebeu_user_id,
                              tipo_acesso='leitura', motivo=None):
        """
        Compartilha um paciente com outro usuário

        Args:
            paciente_id: ID do paciente
            compartilhou_user_id: ID de quem está compartilhando
            recebeu_user_id: ID de quem vai receber o acesso
            tipo_acesso: Tipo de acesso ('leitura', 'edicao', 'completo')
            motivo: Motivo do compartilhamento

        Returns:
            CompartilhamentoPaciente ou None se falhar
        """
        try:
            compartilhamento = CompartilhamentoPaciente(
                paciente_id=paciente_id,
                compartilhou_user_id=compartilhou_user_id,
                recebeu_user_id=recebeu_user_id,
                tipo_acesso=tipo_acesso,
                motivo=motivo,
                ativo=True
            )
            db.session.add(compartilhamento)
            db.session.commit()
            return compartilhamento
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao compartilhar paciente: {e}")
            return None

    @staticmethod
    def revogar_compartilhamento(compartilhamento_id):
        """
        Revoga um compartilhamento

        Args:
            compartilhamento_id: ID do compartilhamento

        Returns:
            bool: True se revogado com sucesso
        """
        try:
            from datetime import datetime
            compartilhamento = CompartilhamentoPaciente.query.get(compartilhamento_id)
            if compartilhamento:
                compartilhamento.ativo = False
                compartilhamento.data_revogacao = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao revogar compartilhamento: {e}")
            return False
