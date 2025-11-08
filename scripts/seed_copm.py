"""
Script de seed para o Módulo COPM (Canadian Occupational Performance Measure)

Este script popula o banco de dados com:
- 1 módulo (COPM)
- 1 instrumento (Todas as idades)
- 3 áreas/domínios (Autocuidado, Produtividade, Lazer)
- Questões guiadas para identificação de problemas ocupacionais

Uso:
    PYTHONPATH=. python scripts/seed_copm.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_copm():
    """Cria o módulo COPM"""
    print("Criando módulo COPM...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='COPM').first()
    if modulo_existente:
        print("Módulo COPM já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='COPM',
        nome='COPM - Canadian Occupational Performance Measure',
        descricao='Medida Canadense de Desempenho Ocupacional - Avaliação centrada no cliente que identifica problemas de desempenho ocupacional',
        categoria='ocupacional',
        icone='clipboard-check',
        cor='#198754',  # Verde
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=90
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_copm(modulo):
    """Cria o instrumento para COPM"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='COPM_GERAL',
        nome='COPM - Medida Canadense de Desempenho Ocupacional',
        modulo_id=modulo.id,
        idade_minima=0,
        idade_maxima=120,
        contexto='geral',
        descricao='Avaliação centrada no cliente que identifica e prioriza problemas de desempenho ocupacional',
        instrucoes="""
INSTRUÇÕES COPM:

1. IDENTIFICAÇÃO: Identifique com o cliente/cuidador até 5 problemas ocupacionais mais importantes
2. CLASSIFICAÇÃO: Para cada problema, o cliente avalia:
   - DESEMPENHO: Como você avalia seu desempenho nesta atividade? (1 = não consegue fazer, 10 = consegue fazer muito bem)
   - SATISFAÇÃO: Quão satisfeito você está com seu desempenho? (1 = nada satisfeito, 10 = extremamente satisfeito)
3. REAVALIAÇÃO: Após intervenção, reavaliar os mesmos problemas para medir mudança clínica

MUDANÇA CLÍNICA SIGNIFICATIVA: Diferença de 2 ou mais pontos entre avaliação e reavaliação
        """
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_copm(instrumento):
    """Cria os 3 domínios/áreas do COPM"""
    print("\nCriando domínios (áreas ocupacionais)...")

    dominios_dados = [
        {
            'codigo': 'AUTOCUIDADO',
            'nome': 'Autocuidado',
            'ordem': 1,
            'descricao': 'Cuidado pessoal, mobilidade funcional, mobilidade comunitária'
        },
        {
            'codigo': 'PRODUTIVIDADE',
            'nome': 'Produtividade',
            'ordem': 2,
            'descricao': 'Trabalho remunerado/voluntário, tarefas domésticas, escola, brincar'
        },
        {
            'codigo': 'LAZER',
            'nome': 'Lazer',
            'ordem': 3,
            'descricao': 'Recreação tranquila, recreação ativa, socialização'
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
        print(f"  ✓ Domínio: {dominio.nome}")

    return dominios


def criar_questoes_copm(dominios):
    """Cria questões guiadas para identificação de problemas no COPM"""
    print("\nCriando questões guiadas...")

    # Estrutura: (dominio_codigo, numero, texto_questao)
    questoes_dados = [
        # AUTOCUIDADO
        ('AUTOCUIDADO', 1, 'Cuidado Pessoal - Há dificuldade em atividades como vestir-se, tomar banho, alimentar-se, higiene pessoal, cuidados com aparência?'),
        ('AUTOCUIDADO', 2, 'Mobilidade Funcional - Há dificuldade em transferências (cadeira, cama, vaso sanitário), mobilidade interna (casa/trabalho)?'),
        ('AUTOCUIDADO', 3, 'Mobilidade Comunitária - Há dificuldade em usar transporte público, dirigir, deslocar-se pela comunidade?'),

        # PRODUTIVIDADE
        ('PRODUTIVIDADE', 4, 'Trabalho Remunerado/Voluntário - Há dificuldade em conseguir/manter emprego, desempenho no trabalho, trabalho voluntário?'),
        ('PRODUTIVIDADE', 5, 'Tarefas Domésticas - Há dificuldade em limpeza, preparo de refeições, manutenção da casa, lavar roupas, fazer compras?'),
        ('PRODUTIVIDADE', 6, 'Brincar/Escola - Há dificuldade em brincar, fazer tarefas escolares, frequentar escola, desempenho acadêmico?'),

        # LAZER
        ('LAZER', 7, 'Recreação Tranquila - Há dificuldade em hobbies, artesanato, leitura, assistir TV, ouvir música, jogos?'),
        ('LAZER', 8, 'Recreação Ativa - Há dificuldade em esportes, passeios, atividades ao ar livre, exercícios físicos?'),
        ('LAZER', 9, 'Socialização - Há dificuldade em visitar amigos/família, festas, telefonemas, atividades sociais, relacionamentos?'),
    ]

    questoes_criadas = 0
    numero_global = 0

    for dominio_codigo, numero, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        numero_global += 1
        questao = Questao(
            codigo=f'COPM_{numero:02d}',
            texto=texto,
            dominio_id=dominio.id,
            ordem=numero,
            numero=numero,
            numero_global=numero_global,
            tipo_resposta='TEXTO_LONGO',
            obrigatoria=False,
            opcoes_resposta=None,
            metadados={
                'numero': numero,
                'area': dominio_codigo,
                'tipo': 'IDENTIFICACAO_PROBLEMA',
                'permite_multiplos': True,
                'escala_desempenho': '1-10',
                'escala_satisfacao': '1-10'
            }
        )

        db.session.add(questao)
        questoes_criadas += 1

    # Adicionar questões de avaliação (desempenho e satisfação)
    # Estas serão usadas após identificação dos problemas
    for i in range(1, 6):  # Até 5 problemas
        # Questão de desempenho
        numero_global += 1
        questao_desemp = Questao(
            codigo=f'COPM_DESEMP_{i}',
            texto=f'Problema {i} - Como você avalia seu DESEMPENHO nesta atividade?',
            dominio_id=dominios['AUTOCUIDADO'].id,  # Domínio será determinado dinamicamente
            ordem=100 + i,
            numero=100 + i,
            numero_global=numero_global,
            tipo_resposta='ESCALA_NUMERICA',
            obrigatoria=False,
            opcoes_resposta=[
                '1|Não consegue fazer',
                '2|Consegue fazer muito mal',
                '3|Consegue fazer mal',
                '4|Consegue fazer razoavelmente',
                '5|Consegue fazer de forma mediana',
                '6|Consegue fazer de forma adequada',
                '7|Consegue fazer bem',
                '8|Consegue fazer muito bem',
                '9|Consegue fazer excelentemente',
                '10|Consegue fazer perfeitamente'
            ],
            metadados={
                'numero_problema': i,
                'tipo': 'AVALIACAO_DESEMPENHO',
                'escala_min': 1,
                'escala_max': 10
            }
        )
        db.session.add(questao_desemp)
        questoes_criadas += 1

        # Questão de satisfação
        numero_global += 1
        questao_satis = Questao(
            codigo=f'COPM_SATIS_{i}',
            texto=f'Problema {i} - Quão SATISFEITO você está com seu desempenho?',
            dominio_id=dominios['AUTOCUIDADO'].id,
            ordem=200 + i,
            numero=200 + i,
            numero_global=numero_global,
            tipo_resposta='ESCALA_NUMERICA',
            obrigatoria=False,
            opcoes_resposta=[
                '1|Nada satisfeito',
                '2|Muito insatisfeito',
                '3|Insatisfeito',
                '4|Um pouco insatisfeito',
                '5|Neutro',
                '6|Um pouco satisfeito',
                '7|Satisfeito',
                '8|Muito satisfeito',
                '9|Extremamente satisfeito',
                '10|Completamente satisfeito'
            ],
            metadados={
                'numero_problema': i,
                'tipo': 'AVALIACAO_SATISFACAO',
                'escala_min': 1,
                'escala_max': 10
            }
        )
        db.session.add(questao_satis)
        questoes_criadas += 1

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} questões criadas!")

    return questoes_criadas


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - COPM (Canadian Occupational Performance Measure)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_copm()

            # Criar instrumento
            instrumento = criar_instrumento_copm(modulo)

            # Criar domínios
            dominios = criar_dominios_copm(instrumento)

            # Criar questões
            total_questoes = criar_questoes_copm(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: COPM")
            print(f"Instrumento: 1")
            print(f"Domínios: 3 áreas ocupacionais")
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
