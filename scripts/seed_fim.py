"""
Script de seed para o Módulo FIM (Functional Independence Measure)

Este script popula o banco de dados com:
- 1 módulo (FIM)
- 1 instrumento (Adultos)
- 6 domínios
- 18 itens

Uso:
    PYTHONPATH=. python scripts/seed_fim.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_fim():
    """Cria o módulo FIM"""
    print("Criando módulo FIM...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='FIM').first()
    if modulo_existente:
        print("Módulo FIM já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='FIM',
        nome='FIM - Functional Independence Measure',
        descricao='Medida de Independência Funcional - Avalia o nível de assistência necessária para um indivíduo realizar atividades da vida diária',
        categoria='funcional',
        icone='list-check',
        cor='#0dcaf0',  # Cyan
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=30
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_fim(modulo):
    """Cria o instrumento para FIM"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='FIM_ADULTO',
        nome='FIM - Medida de Independência Funcional (Adultos)',
        modulo_id=modulo.id,
        idade_minima=18,
        idade_maxima=120,
        contexto='hospital',
        descricao='Instrumento de 18 itens que avalia independência funcional em atividades motoras e cognitivas',
        instrucoes="""
INSTRUÇÕES FIM:

Avalie o nível de INDEPENDÊNCIA do paciente em cada item usando a escala de 7 pontos:

NÍVEIS DE INDEPENDÊNCIA:
7 - Independência completa (em segurança, em tempo normal)
6 - Independência modificada (ajuda técnica)

NÍVEIS DE DEPENDÊNCIA MODIFICADA (Necessita de OUTRA PESSOA):
5 - Supervisão ou preparação
4 - Ajuda com contato mínimo (paciente realiza ≥75%)
3 - Ajuda moderada (paciente realiza 50-74%)

NÍVEIS DE DEPENDÊNCIA COMPLETA:
2 - Ajuda máxima (paciente realiza 25-49%)
1 - Ajuda total (paciente realiza <25%)

PONTUAÇÃO:
- Motor (13 itens): 13-91 pontos
- Cognitivo (5 itens): 5-35 pontos
- Total FIM: 18-126 pontos
        """
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_fim(instrumento):
    """Cria os 6 domínios do FIM"""
    print("\nCriando domínios...")

    dominios_dados = [
        {
            'codigo': 'AUTOCUIDADO',
            'nome': 'Autocuidado',
            'ordem': 1,
            'descricao': 'Alimentação, higiene, banho, vestuário superior/inferior, uso do vaso sanitário',
            'categoria': 'MOTOR'
        },
        {
            'codigo': 'ESFINCT',
            'nome': 'Controle de Esfíncteres',
            'ordem': 2,
            'descricao': 'Controle de bexiga e intestino',
            'categoria': 'MOTOR'
        },
        {
            'codigo': 'TRANSF',
            'nome': 'Transferências',
            'ordem': 3,
            'descricao': 'Leito/cadeira/cadeira de rodas, vaso sanitário, banheira/chuveiro',
            'categoria': 'MOTOR'
        },
        {
            'codigo': 'LOCOMO',
            'nome': 'Locomoção',
            'ordem': 4,
            'descricao': 'Marcha/cadeira de rodas, escadas',
            'categoria': 'MOTOR'
        },
        {
            'codigo': 'COMUNIC',
            'nome': 'Comunicação',
            'ordem': 5,
            'descricao': 'Compreensão e expressão',
            'categoria': 'COGNITIVO'
        },
        {
            'codigo': 'COGN_SOC',
            'nome': 'Cognição Social',
            'ordem': 6,
            'descricao': 'Interação social, resolução de problemas, memória',
            'categoria': 'COGNITIVO'
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
        print(f"  ✓ Domínio: {dominio.nome} ({dado['categoria']})")

    return dominios


def criar_questoes_fim(dominios):
    """Cria os 18 itens do FIM"""
    print("\nCriando itens FIM...")

    # Opcoes de resposta padrão (escala de 7 pontos)
    opcoes_padrao = [
        '1|1 - Ajuda total (< 25%)',
        '2|2 - Ajuda máxima (25-49%)',
        '3|3 - Ajuda moderada (50-74%)',
        '4|4 - Ajuda mínima (≥ 75%)',
        '5|5 - Supervisão/Preparação',
        '6|6 - Independência modificada (com ajuda técnica)',
        '7|7 - Independência completa'
    ]

    # Estrutura: (dominio_codigo, numero, texto)
    questoes_dados = [
        # AUTOCUIDADO (6 itens)
        ('AUTOCUIDADO', 1, 'Alimentação (uso de utensílios, levar comida à boca, mastigar, engolir)'),
        ('AUTOCUIDADO', 2, 'Higiene pessoal (cuidados bucais, lavar rosto/mãos, pentear cabelo, barbear/maquiar)'),
        ('AUTOCUIDADO', 3, 'Banho (lavar e secar o corpo do pescoço para baixo, excluindo costas)'),
        ('AUTOCUIDADO', 4, 'Vestuário - Parte superior (roupas acima da cintura, órteses/próteses)'),
        ('AUTOCUIDADO', 5, 'Vestuário - Parte inferior (roupas abaixo da cintura, órteses/próteses, calçados)'),
        ('AUTOCUIDADO', 6, 'Uso do vaso sanitário (higiene íntima, ajustar roupas, usar papel higiênico)'),

        # CONTROLE DE ESFÍNCTERES (2 itens)
        ('ESFINCT', 7, 'Controle de bexiga (controle intencional da micção, uso de equipamentos/agentes)'),
        ('ESFINCT', 8, 'Controle intestinal (controle intencional da evacuação, uso de equipamentos/agentes)'),

        # TRANSFERÊNCIAS (3 itens)
        ('TRANSF', 9, 'Transferência leito/cadeira/cadeira de rodas (aproximar-se, sentar-se, levantar-se, movimentar-se)'),
        ('TRANSF', 10, 'Transferência para o vaso sanitário (aproximar-se, sentar-se, levantar-se)'),
        ('TRANSF', 11, 'Transferência para banheira/chuveiro (entrar e sair da banheira/box)'),

        # LOCOMOÇÃO (2 itens)
        ('LOCOMO', 12, 'Marcha/Cadeira de rodas (caminhar 50 metros OU cadeira de rodas 50 metros)'),
        ('LOCOMO', 13, 'Escadas (subir/descer 12 a 14 degraus)'),

        # COMUNICAÇÃO (2 itens)
        ('COMUNIC', 14, 'Compreensão (auditiva ou visual - entender linguagem falada ou escrita)'),
        ('COMUNIC', 15, 'Expressão (verbal ou não-verbal - expressar-se através de fala ou escrita)'),

        # COGNIÇÃO SOCIAL (3 itens)
        ('COGN_SOC', 16, 'Interação social (relacionar-se com outras pessoas - familiares, profissionais, público)'),
        ('COGN_SOC', 17, 'Resolução de problemas (tomar decisões apropriadas e razoáveis em situações cotidianas)'),
        ('COGN_SOC', 18, 'Memória (reconhecer e lembrar atividades diárias, executar solicitações sem necessitar de lembretes)')
    ]

    questoes_criadas = 0

    for dominio_codigo, numero, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        questao = Questao(
            codigo=f'FIM_{numero:02d}',
            texto=texto,
            dominio_id=dominio.id,
            ordem=numero,
            tipo_resposta='ESCALA_LIKERT',
            obrigatoria=True,
            opcoes_resposta=opcoes_padrao,
            metadados={
                'numero': numero,
                'categoria': 'MOTOR' if numero <= 13 else 'COGNITIVO',
                'escala_min': 1,
                'escala_max': 7
            }
        )

        db.session.add(questao)
        questoes_criadas += 1

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} itens criados!")

    return questoes_criadas


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - FIM (Functional Independence Measure)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_fim()

            # Criar instrumento
            instrumento = criar_instrumento_fim(modulo)

            # Criar domínios
            dominios = criar_dominios_fim(instrumento)

            # Criar questões
            total_questoes = criar_questoes_fim(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: FIM")
            print(f"Instrumento: 1")
            print(f"Domínios: 6 (4 motores + 2 cognitivos)")
            print(f"Itens: {total_questoes}")
            print("=" * 80)
            print("\nCOMPOSIÇÃO:")
            print("- Motor (13 itens): Autocuidado (6) + Esfíncteres (2) + Transferências (3) + Locomoção (2)")
            print("- Cognitivo (5 itens): Comunicação (2) + Cognição Social (3)")
            print("=" * 80)

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
