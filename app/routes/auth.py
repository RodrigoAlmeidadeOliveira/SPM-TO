"""
Blueprint de autenticação
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms.auth_forms import LoginForm
from app import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Se já estiver logado, redireciona para dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data) and user.ativo:
            # Atualizar último acesso
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Bem-vindo(a), {user.nome_completo}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Usuário ou senha inválidos, ou usuário inativo', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('main.index'))
