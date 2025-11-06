#!/usr/bin/env python3
"""
Arquivo principal para executar a aplicação SPM-TO
"""
import os
from app import create_app, db
from app.models import User, Paciente, Instrumento, Dominio, Questao, TabelaReferencia, Avaliacao, Resposta

# Criar aplicação
app = create_app()


# Shell context
@app.shell_context_processor
def make_shell_context():
    """Disponibiliza modelos no shell"""
    return {
        'db': db,
        'User': User,
        'Paciente': Paciente,
        'Instrumento': Instrumento,
        'Dominio': Dominio,
        'Questao': Questao,
        'TabelaReferencia': TabelaReferencia,
        'Avaliacao': Avaliacao,
        'Resposta': Resposta
    }


# CLI Commands
@app.cli.command()
def initdb():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado!')


@app.cli.command()
def createadmin():
    """Cria usuário administrador"""
    admin = User(
        username='admin',
        email='admin@spmto.com',
        nome_completo='Administrador',
        tipo='admin'
    )
    admin.set_password('admin123')

    db.session.add(admin)
    db.session.commit()

    print('Usuário administrador criado!')
    print('Username: admin')
    print('Password: admin123')


@app.cli.command()
def seed():
    """Popula banco com dados das planilhas"""
    from scripts.seed_database import seed_database
    seed_database()
    print('Banco de dados populado com sucesso!')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
