"""
Decorators personalizados para controle de acesso
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.services.permission_service import PermissionService


def can_view_patient(f):
    """
    Decorator que verifica se o usuário pode visualizar um paciente

    Uso:
        @can_view_patient
        def visualizar(id):
            ...

    O decorator espera que a função tenha um parâmetro 'id' ou 'paciente_id'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscar tanto por 'id' quanto por 'paciente_id'
        paciente_id = kwargs.get('id') or kwargs.get('paciente_id')

        if not paciente_id:
            flash('Paciente não especificado', 'danger')
            return redirect(url_for('pacientes.listar'))

        if not PermissionService.pode_acessar_paciente(current_user, paciente_id):
            PermissionService.registrar_acesso(
                current_user, 'paciente', paciente_id, 'acesso_negado'
            )
            flash('Você não tem permissão para acessar este paciente', 'danger')
            abort(403)

        # Registrar acesso autorizado
        PermissionService.registrar_acesso(
            current_user, 'paciente', paciente_id, 'visualizar'
        )

        return f(*args, **kwargs)

    return decorated_function


def can_edit_patient(f):
    """
    Decorator que verifica se o usuário pode editar um paciente

    Uso:
        @can_edit_patient
        def editar(id):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscar tanto por 'id' quanto por 'paciente_id'
        paciente_id = kwargs.get('id') or kwargs.get('paciente_id')

        if not paciente_id:
            flash('Paciente não especificado', 'danger')
            return redirect(url_for('pacientes.listar'))

        if not PermissionService.pode_editar_paciente(current_user, paciente_id):
            PermissionService.registrar_acesso(
                current_user, 'paciente', paciente_id, 'edicao_negada'
            )
            flash('Você não tem permissão para editar este paciente', 'danger')
            abort(403)

        # Registrar tentativa de edição
        PermissionService.registrar_acesso(
            current_user, 'paciente', paciente_id, 'editar'
        )

        return f(*args, **kwargs)

    return decorated_function


def can_delete_patient(f):
    """
    Decorator que verifica se o usuário pode excluir um paciente

    Uso:
        @can_delete_patient
        def excluir(id):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscar tanto por 'id' quanto por 'paciente_id'
        paciente_id = kwargs.get('id') or kwargs.get('paciente_id')

        if not paciente_id:
            flash('Paciente não especificado', 'danger')
            return redirect(url_for('pacientes.listar'))

        if not PermissionService.pode_excluir_paciente(current_user, paciente_id):
            PermissionService.registrar_acesso(
                current_user, 'paciente', paciente_id, 'exclusao_negada'
            )
            flash('Você não tem permissão para excluir este paciente', 'danger')
            abort(403)

        # Registrar tentativa de exclusão
        PermissionService.registrar_acesso(
            current_user, 'paciente', paciente_id, 'excluir'
        )

        return f(*args, **kwargs)

    return decorated_function


def can_view_avaliacao(f):
    """
    Decorator que verifica se o usuário pode visualizar uma avaliação

    Uso:
        @can_view_avaliacao
        def visualizar(id):
            ...

    O decorator espera que a função tenha um parâmetro 'id' que é o avaliacao_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        avaliacao_id = kwargs.get('id')

        if not avaliacao_id:
            flash('Avaliação não especificada', 'danger')
            return redirect(url_for('avaliacoes.listar'))

        if not PermissionService.pode_acessar_avaliacao(current_user, avaliacao_id):
            PermissionService.registrar_acesso(
                current_user, 'avaliacao', avaliacao_id, 'acesso_negado'
            )
            flash('Você não tem permissão para acessar esta avaliação', 'danger')
            abort(403)

        # Registrar acesso autorizado
        PermissionService.registrar_acesso(
            current_user, 'avaliacao', avaliacao_id, 'visualizar'
        )

        return f(*args, **kwargs)

    return decorated_function


def can_edit_avaliacao(f):
    """
    Decorator que verifica se o usuário pode editar uma avaliação

    Uso:
        @can_edit_avaliacao
        def responder(id):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        avaliacao_id = kwargs.get('id')

        if not avaliacao_id:
            flash('Avaliação não especificada', 'danger')
            return redirect(url_for('avaliacoes.listar'))

        if not PermissionService.pode_editar_avaliacao(current_user, avaliacao_id):
            PermissionService.registrar_acesso(
                current_user, 'avaliacao', avaliacao_id, 'edicao_negada'
            )
            flash('Você não tem permissão para editar esta avaliação', 'danger')
            abort(403)

        # Registrar tentativa de edição
        PermissionService.registrar_acesso(
            current_user, 'avaliacao', avaliacao_id, 'editar'
        )

        return f(*args, **kwargs)

    return decorated_function


def admin_or_owner_required(resource_type='paciente'):
    """
    Decorator parametrizado que verifica se o usuário é admin ou dono do recurso

    Uso:
        @admin_or_owner_required('paciente')
        def alguma_acao(id):
            ...

    Args:
        resource_type: Tipo de recurso ('paciente', 'avaliacao')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar autenticado', 'warning')
                return redirect(url_for('auth.login'))

            # Admin sempre pode
            if current_user.is_admin():
                return f(*args, **kwargs)

            resource_id = kwargs.get('id')

            if not resource_id:
                flash(f'{resource_type.capitalize()} não especificado', 'danger')
                return redirect(url_for(f'{resource_type}s.listar'))

            # Verificar propriedade baseado no tipo
            if resource_type == 'paciente':
                pode = PermissionService.pode_editar_paciente(current_user, resource_id)
            elif resource_type == 'avaliacao':
                pode = PermissionService.pode_editar_avaliacao(current_user, resource_id)
            else:
                pode = False

            if not pode:
                flash(f'Você não tem permissão para esta ação', 'danger')
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
