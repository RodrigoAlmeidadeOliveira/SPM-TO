"""
Script de seed para o Módulo ABC Scale (Activities-specific Balance Confidence Scale)

Este script popula o banco de dados com:
- 1 módulo (ABC Scale)
- 1 instrumento (Adultos/Idosos)
- 1 domínio (Confiança no Equilíbrio)
- 16 questões sobre confiança em atividades específicas

Uso:
    PYTHONPATH=. python scripts/seed_abc_scale.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_abc():
    """Cria o módulo ABC Scale"""
    print("Criando módulo ABC Scale...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='ABC').first()
    if modulo_existente:
        print("Módulo ABC Scale já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='ABC',
        nome='ABC Scale - Activities-specific Balance Confidence',
        descricao='Escala de Confiança no Equilíbrio Específica por Atividade - Avalia o nível de confiança em manter o equilíbrio durante atividades diárias',
        categoria='motor',
        icone='person-walking',
        cor='#dc3545',  # Vermelho
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=30
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_abc(modulo):
    """Cria o instrumento para ABC Scale"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='ABC_ADULTO',
        nome='ABC Scale - Escala de Confiança no Equilíbrio (Adultos/Idosos)',
        modulo_id=modulo.id,
        idade_minima=18,
        idade_maxima=120,
        contexto='geral',
        descricao='Questionário de 16 itens que avalia a confiança no equilíbrio durante atividades da vida diária',
        instrucoes="""
INSTRUÇÕES ABC SCALE:

Para cada uma das seguintes atividades, indique seu nível de CONFIANÇA em fazer a atividade SEM PERDER O EQUILÍBRIO ou ficar instável, escolhendo um número correspondente entre 0% e 100%.

Se você atualmente não faz a atividade em questão, tente imaginar o quão confiante você seria se TIVESSE que fazer a atividade.

ESCALA:
0%   = Nenhuma confiança
50%  = Moderadamente confiante
100% = Completamente confiante

INTERPRETAÇÃO:
- Escore Total: Média dos 16 itens (0-100%)
- > 80%: Alta confiança no equilíbrio (baixo risco de queda)
- 50-80%: Confiança moderada (risco moderado)
- < 50%: Baixa confiança (alto risco de queda)
        """
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_abc(instrumento):
    """Cria o domínio do ABC Scale"""
    print("\nCriando domínio...")

    dominio = Dominio(
        codigo='CONF_EQUIL',
        nome='Confiança no Equilíbrio',
        instrumento_id=instrumento.id,
        ordem=1,
        descricao='Nível de confiança em manter o equilíbrio durante atividades específicas'
    )

    db.session.add(dominio)
    db.session.flush()

    print(f"  ✓ Domínio: {dominio.nome}")
    return dominio


def criar_questoes_abc(dominio):
    """Cria as 16 questões do ABC Scale"""
    print("\nCriando questões...")

    # Questões oficiais do ABC Scale (traduzidas)
    questoes_dados = [
        (1, 'Caminhar pela casa'),
        (2, 'Subir ou descer escadas'),
        (3, 'Abaixar-se e pegar um chinelo na frente do armário de sapatos'),
        (4, 'Alcançar um objeto pequeno (por exemplo, uma lata de sopa) em uma prateleira na altura dos olhos'),
        (5, 'Ficar na ponta dos pés e alcançar algo acima da cabeça'),
        (6, 'Ficar em uma cadeira e alcançar algo'),
        (7, 'Varrer o chão'),
        (8, 'Caminhar fora de casa até um carro estacionado próximo'),
        (9, 'Entrar ou sair de um carro'),
        (10, 'Caminhar por um estacionamento até um shopping center'),
        (11, 'Subir ou descer uma rampa'),
        (12, 'Caminhar em um shopping center cheio de pessoas onde as pessoas passam rapidamente por você'),
        (13, 'Ser esbarrado por pessoas enquanto caminha pelo shopping'),
        (14, 'Subir ou descer em uma escada rolante segurando nos corrimãos'),
        (15, 'Subir ou descer em uma escada rolante segurando pacotes de tal forma que você não pode segurar nos corrimãos'),
        (16, 'Caminhar em calçadas escorregadias')
    ]

    questoes_criadas = 0
    numero_global = 0

    for numero, texto in questoes_dados:
        numero_global += 1
        questao = Questao(
            codigo=f'ABC_{numero:02d}',
            texto=f'Quão CONFIANTE você está de que não perderá o equilíbrio ou ficará instável quando você... {texto}?',
            dominio_id=dominio.id,
            ordem=numero,
            numero=numero,
            numero_global=numero_global,
            tipo_resposta='ESCALA_PERCENTUAL',
            obrigatoria=True,
            opcoes_resposta=[
                '0|0% - Nenhuma confiança',
                '10|10%',
                '20|20%',
                '30|30%',
                '40|40%',
                '50|50% - Moderadamente confiante',
                '60|60%',
                '70|70%',
                '80|80%',
                '90|90%',
                '100|100% - Completamente confiante'
            ],
            metadados={
                'numero': numero,
                'atividade': texto,
                'escala_min': 0,
                'escala_max': 100,
                'tipo': 'CONFIANCA_EQUILIBRIO'
            }
        )

        db.session.add(questao)
        questoes_criadas += 1

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} questões criadas!")

    return questoes_criadas


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - ABC Scale (Activities-specific Balance Confidence)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_abc()

            # Criar instrumento
            instrumento = criar_instrumento_abc(modulo)

            # Criar domínio
            dominio = criar_dominios_abc(instrumento)

            # Criar questões
            total_questoes = criar_questoes_abc(dominio)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: ABC Scale")
            print(f"Instrumento: 1")
            print(f"Domínios: 1 (Confiança no Equilíbrio)")
            print(f"Questões: {total_questoes}")
            print("=" * 80)

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
