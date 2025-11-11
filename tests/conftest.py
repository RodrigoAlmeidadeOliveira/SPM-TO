"""
Fixtures compartilhadas para todos os testes
"""
import pytest
import os
import tempfile
from datetime import datetime, date

from app import create_app, db
from app.models import (
    User, Paciente, Instrumento, Dominio, Questao,
    Avaliacao, Resposta, TabelaReferencia, AnexoAvaliacao, Modulo
)


@pytest.fixture(scope='session')
def app():
    """Cria app Flask para testes"""
    # Criar banco temporário
    db_fd, db_path = tempfile.mkstemp()

    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """CLI runner para testes"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Sessão de banco com rollback automático"""
    with app.app_context():
        # Limpar tabelas antes de cada teste
        db.session.query(Resposta).delete()
        db.session.query(Avaliacao).delete()
        db.session.query(AnexoAvaliacao).delete()
        db.session.query(Questao).delete()
        db.session.query(Dominio).delete()
        db.session.query(TabelaReferencia).delete()
        db.session.query(Instrumento).delete()
        db.session.query(Modulo).delete()
        db.session.query(Paciente).delete()
        db.session.query(User).delete()
        db.session.commit()

        yield db.session


@pytest.fixture
def admin_user(db_session):
    """Usuário admin para testes"""
    user = User(
        username='admin',
        email='admin@test.com',
        nome_completo='Admin Teste',
        tipo='admin',
        ativo=True
    )
    user.set_password('admin123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def terapeuta_user(db_session):
    """Usuário terapeuta para testes"""
    user = User(
        username='terapeuta',
        email='terapeuta@test.com',
        nome_completo='Terapeuta Teste',
        tipo='terapeuta',
        ativo=True
    )
    user.set_password('terapeuta123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def professor_user(db_session):
    """Usuário professor para testes"""
    user = User(
        username='professor',
        email='professor@test.com',
        nome_completo='Professor Teste',
        tipo='professor',
        ativo=True
    )
    user.set_password('prof123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def paciente(db_session, terapeuta_user):
    """Paciente para testes"""
    paciente = Paciente(
        nome='João da Silva',
        identificacao='JOAO001',
        data_nascimento=date(2015, 5, 15),  # 8 anos
        sexo='M',
        raca_etnia='Branco',
        observacoes='Paciente de teste',
        ativo=True,
        criador_id=terapeuta_user.id
    )
    db_session.add(paciente)
    db_session.commit()
    return paciente


@pytest.fixture
def instrumento(db_session):
    """Instrumento SPM para testes"""
    instrumento = Instrumento(
        codigo='SPM_5_12_CASA',
        nome='SPM 5-12 anos (Casa)',
        contexto='casa',
        idade_minima=5,
        idade_maxima=12,
        ativo=True
    )
    db_session.add(instrumento)
    db_session.commit()
    return instrumento


@pytest.fixture
def dominio(db_session, instrumento):
    """Domínio SOC para testes"""
    dominio = Dominio(
        instrumento_id=instrumento.id,
        codigo='SOC',
        nome='Participação Social',
        ordem=1,
        escala_invertida=False
    )
    db_session.add(dominio)
    db_session.commit()
    return dominio


@pytest.fixture
def questoes(db_session, dominio):
    """Lista de questões para testes"""
    questoes = []
    for i in range(1, 6):  # 5 questões
        questao = Questao(
            dominio_id=dominio.id,
            numero=i,
            numero_global=i,  # Adicionar numero_global
            texto=f'Questão {i} de teste',
            ativo=True
        )
        db_session.add(questao)
        questoes.append(questao)
    db_session.commit()
    return questoes


@pytest.fixture
def tabela_referencia(db_session, instrumento, dominio):
    """Tabela de referência para testes"""
    # Exemplo: pontuação bruta 20-25 = T-score 60
    tabela = TabelaReferencia(
        instrumento_id=instrumento.id,
        dominio_codigo=dominio.codigo,
        pontuacao_bruta_min=20,
        pontuacao_bruta_max=25,
        t_score=60,
        percentil=84,
        classificacao='TIPICO'
    )
    db_session.add(tabela)
    db_session.commit()
    return tabela


@pytest.fixture
def avaliacao(db_session, paciente, instrumento, terapeuta_user):
    """Avaliação para testes"""
    avaliacao = Avaliacao(
        paciente_id=paciente.id,
        instrumento_id=instrumento.id,
        avaliador_id=terapeuta_user.id,
        data_avaliacao=datetime.now().date(),
        relacionamento_respondente='Mãe',
        status='em_andamento'
    )
    db_session.add(avaliacao)
    db_session.commit()
    return avaliacao


@pytest.fixture
def perfil_sensorial_instrumento(db_session):
    """Instrumento Perfil Sensorial 2 populado via seed."""
    from scripts.seed_perfil_sensorial import seed_perfil_sensorial
    seed_perfil_sensorial()
    instrumento = Instrumento.query.filter_by(codigo='PERFIL_SENS_CRIANCA').first()
    return instrumento


@pytest.fixture
def avaliacao_perfil_sensorial(db_session, paciente, terapeuta_user, perfil_sensorial_instrumento):
    """Avaliação preenchida para o Perfil Sensorial 2."""
    avaliacao = Avaliacao(
        paciente_id=paciente.id,
        instrumento_id=perfil_sensorial_instrumento.id,
        avaliador_id=terapeuta_user.id,
        data_avaliacao=datetime.now().date(),
        relacionamento_respondente='Mãe',
        status='concluida'
    )
    db_session.add(avaliacao)
    db_session.flush()

    def responder(numero, valor):
        questao = Questao.query.filter_by(codigo=f'PS_{numero:03d}').first()
        resposta = Resposta.query.filter_by(
            avaliacao_id=avaliacao.id,
            questao_id=questao.id
        ).first()

        if resposta:
            resposta.valor = valor
        else:
            resposta = Resposta(
                avaliacao_id=avaliacao.id,
                questao_id=questao.id,
                valor=valor,
                pontuacao=0
            )
            db_session.add(resposta)

    # Tornar seções auditivo e visual altas, demais baixas
    for numero in range(1, 9):
        responder(numero, 'QUASE_SEMPRE')
    for numero in range(9, 16):
        responder(numero, 'FREQUENTEMENTE')
    for numero in range(16, 27):
        responder(numero, 'QUASE_NUNCA')
    # Alguns itens para quadrantes
    for numero in [21, 22, 25, 27, 48]:
        responder(numero, 'QUASE_SEMPRE')
    for numero in [63, 64, 65, 66]:
        responder(numero, 'QUASE_NUNCA')

    db_session.commit()
    return avaliacao


@pytest.fixture
def avaliacao_completa(db_session, avaliacao, questoes):
    """Avaliação com todas as questões respondidas"""
    # Responder todas as questões
    for questao in questoes:
        resposta = Resposta(
            avaliacao_id=avaliacao.id,
            questao_id=questao.id,
            valor='SEMPRE',
            pontuacao=1
        )
        db_session.add(resposta)

    # Marcar como concluída
    avaliacao.status = 'concluida'
    avaliacao.escore_soc = 5  # Soma das pontuações
    avaliacao.t_score_soc = 60
    avaliacao.classificacao_soc = 'TIPICO'

    db_session.commit()
    return avaliacao


def login(client, username, password):
    """Helper para fazer login"""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def logout(client):
    """Helper para fazer logout"""
    return client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def logged_admin(client, admin_user):
    """Cliente com admin logado"""
    login(client, 'admin', 'admin123')
    yield client
    logout(client)


@pytest.fixture
def logged_terapeuta(client, terapeuta_user):
    """Cliente com terapeuta logado"""
    login(client, 'terapeuta', 'terapeuta123')
    yield client
    logout(client)


@pytest.fixture
def logged_professor(client, professor_user):
    """Cliente com professor logado"""
    login(client, 'professor', 'prof123')
    yield client
    logout(client)
