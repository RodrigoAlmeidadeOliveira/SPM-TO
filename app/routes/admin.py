"""
Blueprint de Administração
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.forms.user_forms import UserCreateForm, UserEditForm

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator para exigir que o usuário seja admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Você precisa ser administrador para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard administrativo"""
    total_usuarios = User.query.filter_by(ativo=True).count()
    total_admins = User.query.filter_by(ativo=True, tipo='admin').count()
    total_terapeutas = User.query.filter_by(ativo=True, tipo='terapeuta').count()

    return render_template('admin/dashboard.html',
                         total_usuarios=total_usuarios,
                         total_admins=total_admins,
                         total_terapeutas=total_terapeutas)


@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """Listar todos os usuários"""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '', type=str)
    tipo = request.args.get('tipo', '', type=str)

    query = User.query

    # Filtro de busca
    if busca:
        query = query.filter(db.or_(
            User.username.ilike(f'%{busca}%'),
            User.email.ilike(f'%{busca}%'),
            User.nome_completo.ilike(f'%{busca}%')
        ))

    # Filtro por tipo
    if tipo:
        query = query.filter_by(tipo=tipo)

    # Ordenar e paginar
    usuarios = query.order_by(User.nome_completo).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('admin/usuarios.html',
                         usuarios=usuarios,
                         busca=busca,
                         tipo_filtro=tipo)


@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    """Cadastrar novo usuário"""
    form = UserCreateForm()

    if form.validate_on_submit():
        usuario = User(
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data,
            tipo=form.tipo.data,
            ativo=form.ativo.data
        )
        usuario.set_password(form.password.data)

        db.session.add(usuario)
        db.session.commit()

        flash(f'Usuário {usuario.username} cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/usuario_form.html', form=form, titulo='Novo Usuário')


@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    """Editar usuário existente"""
    usuario = User.query.get_or_404(id)
    form = UserEditForm(
        original_username=usuario.username,
        original_email=usuario.email
    )

    if form.validate_on_submit():
        usuario.username = form.username.data
        usuario.email = form.email.data
        usuario.nome_completo = form.nome_completo.data
        usuario.tipo = form.tipo.data
        usuario.ativo = form.ativo.data

        # Só atualiza senha se foi fornecida
        if form.password.data:
            usuario.set_password(form.password.data)

        db.session.commit()

        flash(f'Usuário {usuario.username} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.listar_usuarios'))

    # Preenche o formulário com dados do usuário
    if request.method == 'GET':
        form.username.data = usuario.username
        form.email.data = usuario.email
        form.nome_completo.data = usuario.nome_completo
        form.tipo.data = usuario.tipo
        form.ativo.data = usuario.ativo

    return render_template('admin/usuario_form.html',
                         form=form,
                         titulo='Editar Usuário',
                         usuario=usuario)


@admin_bp.route('/usuarios/<int:id>/detalhes')
@login_required
@admin_required
def detalhes_usuario(id):
    """Ver detalhes do usuário"""
    usuario = User.query.get_or_404(id)
    return render_template('admin/usuario_detalhes.html', usuario=usuario)


@admin_bp.route('/usuarios/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def deletar_usuario(id):
    """Desativar usuário (soft delete)"""
    usuario = User.query.get_or_404(id)

    # Não permite deletar a si mesmo
    if usuario.id == current_user.id:
        flash('Você não pode desativar seu próprio usuário!', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    # Não permite deletar o último admin
    if usuario.tipo == 'admin':
        admins_ativos = User.query.filter_by(ativo=True, tipo='admin').count()
        if admins_ativos <= 1:
            flash('Não é possível desativar o último administrador do sistema!', 'danger')
            return redirect(url_for('admin.listar_usuarios'))

    usuario.ativo = False
    db.session.commit()

    flash(f'Usuário {usuario.username} desativado com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/usuarios/<int:id>/ativar', methods=['POST'])
@login_required
@admin_required
def ativar_usuario(id):
    """Reativar usuário"""
    usuario = User.query.get_or_404(id)

    usuario.ativo = True
    db.session.commit()

    flash(f'Usuário {usuario.username} reativado com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/configuracoes')
@login_required
@admin_required
def configuracoes():
    """Configurações do sistema"""
    return render_template('admin/configuracoes.html')
