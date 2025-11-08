"""
Script de seed para o Módulo GMFM (Gross Motor Function Measure)

Este script popula o banco de dados com:
- 1 módulo (GMFM)
- 1 instrumento (GMFM-88)
- 5 dimensões
- 88 itens

Uso:
    PYTHONPATH=. python scripts/seed_gmfm.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_gmfm():
    """Cria o módulo GMFM"""
    print("Criando módulo GMFM...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='GMFM').first()
    if modulo_existente:
        print("Módulo GMFM já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='GMFM',
        nome='GMFM - Gross Motor Function Measure',
        descricao='Medida da Função Motora Grossa - Avalia habilidades motoras grossas em crianças com paralisia cerebral e outras condições neurológicas',
        categoria='motor',
        icone='person-walking',
        cor='#dc3545',  # Vermelho
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=90
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_gmfm(modulo):
    """Cria o instrumento para GMFM"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='GMFM_88',
        nome='GMFM-88 - Medida da Função Motora Grossa (88 itens)',
        modulo_id=modulo.id,
        idade_minima=0,
        idade_maxima=18,
        contexto='clinica',
        descricao='Instrumento de 88 itens que avalia função motora grossa em crianças com disfunções motoras',
        instrucoes="""
INSTRUÇÕES GMFM-88:

Avalie a capacidade da criança em INICIAR e COMPLETAR cada item usando a escala de 4 pontos:

ESCALA DE PONTUAÇÃO:
0 = NÃO INICIA - Criança não inicia a atividade ou não consegue manter a posição inicial
1 = INICIA - Criança inicia a atividade mas completa menos de 10% da tarefa
2 = COMPLETA PARCIALMENTE - Criança completa de 10% a menos de 100% da tarefa
3 = COMPLETA - Criança completa 100% da tarefa

IMPORTANTE:
- Observe a qualidade e a capacidade funcional
- Não use dispositivos auxiliares a menos que especificado no item
- Permita 3 tentativas para cada item
- Pontue o melhor desempenho observado

DIMENSÕES:
A. Deitar e Rolar (17 itens)
B. Sentar (20 itens)
C. Engatinhar e Ajoelhar (14 itens)
D. Ficar em Pé (13 itens)
E. Andar, Correr e Pular (24 itens)

PONTUAÇÃO:
- Por dimensão: % = (total obtido / total possível) × 100
- Total GMFM: Média das 5 dimensões
        """
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_gmfm(instrumento):
    """Cria as 5 dimensões do GMFM"""
    print("\nCriando dimensões...")

    dominios_dados = [
        {
            'codigo': 'DIM_A',
            'nome': 'A - Deitar e Rolar',
            'ordem': 1,
            'descricao': 'Habilidades em decúbito e rolamento',
            'itens': 17
        },
        {
            'codigo': 'DIM_B',
            'nome': 'B - Sentar',
            'ordem': 2,
            'descricao': 'Habilidades de sentar',
            'itens': 20
        },
        {
            'codigo': 'DIM_C',
            'nome': 'C - Engatinhar e Ajoelhar',
            'ordem': 3,
            'descricao': 'Habilidades de engatinhar e ajoelhar',
            'itens': 14
        },
        {
            'codigo': 'DIM_D',
            'nome': 'D - Ficar em Pé',
            'ordem': 4,
            'descricao': 'Habilidades de ficar em pé',
            'itens': 13
        },
        {
            'codigo': 'DIM_E',
            'nome': 'E - Andar, Correr e Pular',
            'ordem': 5,
            'descricao': 'Habilidades de locomoção avançada',
            'itens': 24
        }
    ]

    dominios = {}
    for dado in dominios_dados:
        dominio = Dominio(
            codigo=dado['codigo'],
            nome=dado['nome'],
            instrumento_id=instrumento.id,
            ordem=dado['ordem'],
            descricao=dado['descricao']
        )
        db.session.add(dominio)
        db.session.flush()
        dominios[dado['codigo']] = dominio
        print(f"  ✓ Dimensão: {dominio.nome} ({dado['itens']} itens)")

    return dominios


def criar_questoes_gmfm(dominios):
    """Cria os 88 itens do GMFM"""
    print("\nCriando itens GMFM...")

    # Opcoes de resposta padrão (escala de 0-3)
    opcoes_padrao = [
        '0|0 - Não inicia',
        '1|1 - Inicia (< 10%)',
        '2|2 - Completa parcialmente (10-99%)',
        '3|3 - Completa (100%)'
    ]

    # Itens por dimensão
    itens_dados = {
        'DIM_A': [  # Deitar e Rolar (17 itens)
            'Supino (barriga para cima), cabeça na linha média: vira cabeça com membros simétricos',
            'Supino: leva as mãos à linha média, dedos entre si',
            'Supino: eleva cabeça 45°',
            'Supino: flexão de cabeça com queixo na faixa esternal',
            'Supino: atinge um brinquedo com braço direito',
            'Supino: atinge um brinquedo com braço esquerdo',
            'Supino: rola para prono (barriga para baixo) sobre lado direito',
            'Supino: rola para prono sobre lado esquerdo',
            'Prono: eleva cabeça ereto',
            'Prono em antebraços: eleva cabeça ereto, cotovelos estendidos, peito elevado',
            'Prono em mãos: eleva cabeça ereto, braços estendidos, peito elevado',
            'Prono: rola para supino sobre lado direito',
            'Prono: rola para supino sobre lado esquerdo',
            'Prono: pivoteia 90° usando extremidades',
            'Supino: atinge um brinquedo acima do peito com ambas as mãos',
            'Supino: flexiona perna direita e esquerda independentemente',
            'Supino para sentado sobre lado direito'
        ],
        'DIM_B': [  # Sentar (20 itens)
            'Supino puxado para sentar: flexão de cabeça',
            'Supino puxado para sentar: flexão de cabeça com auxílio dos membros superiores',
            'Sentado apoiado: mantém cabeça ereta 3 segundos',
            'Sentado apoiado: mantém cabeça ereta 10 segundos',
            'Sentado (apoio de mãos para frente): mantém posição 5 segundos',
            'Sentado sem apoio de mãos: mantém posição 3 segundos',
            'Sentado sem apoio: mantém posição 5 segundos',
            'Sentado: toca brinquedo colocado à frente',
            'Sentado: toca brinquedo colocado à esquerda',
            'Sentado: toca brinquedo colocado à direita',
            'Sentado: pega brinquedo do chão à direita e volta a sentar',
            'Sentado: pega brinquedo do chão à esquerda e volta a sentar',
            'Sentado: pega brinquedo do chão à frente e volta a sentar',
            'Sentado: toca brinquedo colocado 45° atrás à direita',
            'Sentado: toca brinquedo colocado 45° atrás à esquerda',
            'Sentado no banco: mantém posição, pés apoiados, braços livres 5 segundos',
            'Sentado no chão: atinge brinquedo acima da cabeça',
            'Sentado no banco: atinge brinquedo colocado no chão, volta a sentar',
            'Ajoelhado alto: senta no chão com controle',
            'Sentado no banco pequeno: levanta-se para ficar em pé, mantém 3 segundos'
        ],
        'DIM_C': [  # Engatinhar e Ajoelhar (14 itens)
            'Prono: arrasta 1,8 metros',
            'Quatro apoios: mantém peso em mãos e joelhos 10 segundos',
            'Quatro apoios: atinge brinquedo colocado à frente com braço direito',
            'Quatro apoios: atinge brinquedo colocado à frente com braço esquerdo',
            'Quatro apoios: engatinha ou desliza para frente 1,8 metros',
            'Quatro apoios: engatinha reciprocamente para frente 1,8 metros',
            'Quatro apoios: engatinha para cima 4 degraus',
            'Quatro apoios: engatinha para baixo 4 degraus',
            'Sentado: assume ajoelhado, mantém posição com braços livres 10 segundos',
            'Ajoelhado alto: atinge brinquedo à frente acima da cabeça',
            'Ajoelhado alto: atinge brinquedo colocado 45° à direita',
            'Ajoelhado alto: atinge brinquedo colocado 45° à esquerda',
            'Ajoelhado alto: caminha para frente 10 passos',
            'Meio ajoelhado sobre perna direita: assume posição, mantém 10 segundos'
        ],
        'DIM_D': [  # Ficar em Pé (13 itens)
            'No chão: puxa para ficar em pé em um banco grande',
            'Sentado em banco pequeno: assume posição em pé, mantém 3 segundos',
            'Em pé: mantém-se, segurando em banco grande, braços livres 3 segundos',
            'Em pé: mantém-se sem segurar, braços livres 3 segundos',
            'Em pé: segurando com uma das mãos, eleva perna direita 10 segundos',
            'Em pé: segurando com uma das mãos, eleva perna esquerda 10 segundos',
            'Em pé: eleva perna direita sem apoio 10 segundos',
            'Em pé: eleva perna esquerda sem apoio 10 segundos',
            'Em pé: senta no chão com controle',
            'Em pé: abaixa-se agachado e retorna',
            'Em pé: pega objeto no chão e retorna a ficar em pé',
            'Em pé: atinge brinquedo acima da cabeça com ambas as mãos, braços estendidos',
            'Em pé: atinge brinquedo acima da cabeça com braço direito, braço estendido'
        ],
        'DIM_E': [  # Andar, Correr e Pular (24 itens)
            'Em pé, segurando em banco grande: dá 5 passos para direita, segurando com ambas as mãos',
            'Em pé, segurando em banco grande: dá 5 passos para esquerda, segurando com ambas as mãos',
            'Em pé: duas mãos seguradas, anda para frente 10 passos',
            'Em pé: uma mão segurada, anda para frente 10 passos',
            'Em pé: anda para frente 10 passos',
            'Em pé: anda para frente 10 passos, para e volta',
            'Em pé: anda para trás 10 passos',
            'Em pé: anda para frente 10 passos, carregando objeto grande com ambas as mãos',
            'Em pé: caminha para frente 10 passos consecutivos entre linhas paralelas de 20cm',
            'Em pé: caminha para frente 10 passos consecutivos em linha reta de 2cm',
            'Em pé: passa sobre pau (altura 5cm) perna direita conduzindo',
            'Em pé: passa sobre pau (altura 5cm) perna esquerda conduzindo',
            'Em pé: corre 4,5 metros, para e volta',
            'Em pé: chuta bola com pé direito',
            'Em pé: chuta bola com pé esquerdo',
            'Em pé: pula 30cm para frente, ambos os pés simultaneamente',
            'Em pé: pula 30cm para frente, perna direita',
            'Em pé: pula 30cm para frente, perna esquerda',
            'Em pé em pé direito: pula, pé direito, 10 vezes dentro círculo de 60cm',
            'Em pé em pé esquerdo: pula, pé esquerdo, 10 vezes dentro círculo de 60cm',
            'Em pé: sobe 4 degraus, segurando-se, pé direito, depois esquerdo',
            'Em pé: desce 4 degraus, segurando-se, pé direito, depois esquerdo',
            'Em pé: sobe e desce 4 degraus, pés alternados, sem se segurar',
            'Em pé: segurando em corrimão, sobe e desce 4 degraus, pés alternados'
        ]
    }

    questoes_criadas = 0
    numero_global = 0

    for dim_codigo, itens in itens_dados.items():
        dominio = dominios[dim_codigo]

        for i, texto in enumerate(itens, start=1):
            numero_global += 1

            questao = Questao(
                codigo=f'GMFM_{numero_global:03d}',
                texto=texto,
                dominio_id=dominio.id,
                ordem=i,
                numero=i,
                numero_global=numero_global,
                tipo_resposta='ESCALA_LIKERT',
                obrigatoria=True,
                opcoes_resposta=opcoes_padrao,
                metadados={
                    'numero': i,
                    'numero_global': numero_global,
                    'dimensao': dim_codigo,
                    'escala_min': 0,
                    'escala_max': 3
                }
            )

            db.session.add(questao)
            questoes_criadas += 1

        if questoes_criadas % 20 == 0:
            print(f"  ✓ {questoes_criadas} itens criados...")

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} itens criados!")

    return questoes_criadas


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - GMFM-88 (Gross Motor Function Measure)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_gmfm()

            # Criar instrumento
            instrumento = criar_instrumento_gmfm(modulo)

            # Criar domínios
            dominios = criar_dominios_gmfm(instrumento)

            # Criar questões
            total_questoes = criar_questoes_gmfm(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: GMFM-88")
            print(f"Instrumento: 1")
            print(f"Dimensões: 5")
            print(f"Itens: {total_questoes}")
            print("=" * 80)
            print("\nCOMPOSIÇÃO DAS DIMENSÕES:")
            print("- A: Deitar e Rolar (17 itens)")
            print("- B: Sentar (20 itens)")
            print("- C: Engatinhar e Ajoelhar (14 itens)")
            print("- D: Ficar em Pé (13 itens)")
            print("- E: Andar, Correr e Pular (24 itens)")
            print("=" * 80)

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
