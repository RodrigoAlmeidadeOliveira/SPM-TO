"""
Script de seed para o Módulo WeeFIM (Functional Independence Measure for Children)

Este script popula o banco de dados com:
- 1 módulo (WeeFIM)
- 1 instrumento (Crianças 6 meses - 7 anos)
- 6 domínios
- 18 itens

Uso:
    PYTHONPATH=. python scripts/seed_weefim.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_weefim():
    """Cria o módulo WeeFIM"""
    print("Criando módulo WeeFIM...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='WEEFIM').first()
    if modulo_existente:
        print("Módulo WeeFIM já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='WEEFIM',
        nome='WeeFIM - Functional Independence Measure for Children',
        descricao='Medida de Independência Funcional para Crianças - Avalia independência funcional de crianças de 6 meses a 7 anos',
        categoria='funcional',
        icone='person-wheelchair',
        cor='#0dcaf0',  # Cyan
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=90
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_weefim(modulo):
    """Cria o instrumento para WeeFIM"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='WEEFIM_0_7',
        nome='WeeFIM - Medida de Independência Funcional Pediátrica (6 meses a 7 anos)',
        modulo_id=modulo.id,
        idade_minima=0,
        idade_maxima=7,
        contexto='casa',
        descricao='Instrumento de 18 itens que avalia independência funcional em crianças considerando desenvolvimento típico',
        instrucoes="""
INSTRUÇÕES WeeFIM:

Avalie o nível de INDEPENDÊNCIA da criança em cada item usando a escala de 7 pontos.
Compare com o desenvolvimento TÍPICO esperado para a idade.

NÍVEIS DE INDEPENDÊNCIA:
7 - Independência completa (apropriada para idade)
6 - Independência modificada (com ajuda técnica)

NÍVEIS DE DEPENDÊNCIA MODIFICADA (Necessita de OUTRA PESSOA):
5 - Supervisão ou orientação
4 - Ajuda com contato mínimo (criança realiza ≥75%)
3 - Ajuda moderada (criança realiza 50-74%)

NÍVEIS DE DEPENDÊNCIA COMPLETA:
2 - Ajuda máxima (criança realiza 25-49%)
1 - Ajuda total (criança realiza <25%)

IMPORTANTE: Considere o desenvolvimento típico para a idade da criança.
Uma criança de 1 ano não é esperada ter independência completa em muitas atividades.

PONTUAÇÃO:
- Motor (13 itens): 13-91 pontos
- Cognitivo (5 itens): 5-35 pontos
- Total WeeFIM: 18-126 pontos
        """
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_weefim(instrumento):
    """Cria os 6 domínios do WeeFIM"""
    print("\nCriando domínios...")

    dominios_dados = [
        {
            'codigo': 'AUTOCUIDADO',
            'nome': 'Autocuidado',
            'ordem': 1,
            'descricao': 'Alimentação, higiene, banho, vestuário, uso do vaso sanitário',
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
            'descricao': 'Cadeira, vaso sanitário, banheira',
            'categoria': 'MOTOR'
        },
        {
            'codigo': 'LOCOMO',
            'nome': 'Locomoção',
            'ordem': 4,
            'descricao': 'Locomoção e escadas',
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


def criar_questoes_weefim(dominios):
    """Cria os 18 itens do WeeFIM"""
    print("\nCriando itens WeeFIM...")

    # Opcoes de resposta padrão (escala de 7 pontos)
    opcoes_padrao = [
        '1|1 - Ajuda total (< 25%)',
        '2|2 - Ajuda máxima (25-49%)',
        '3|3 - Ajuda moderada (50-74%)',
        '4|4 - Ajuda mínima (≥ 75%)',
        '5|5 - Supervisão/Orientação',
        '6|6 - Independência modificada (com ajuda técnica)',
        '7|7 - Independência completa (apropriada para idade)'
    ]

    # Estrutura: (dominio_codigo, numero, texto)
    questoes_dados = [
        # AUTOCUIDADO (6 itens)
        ('AUTOCUIDADO', 1, 'Alimentação (comer com utensílios apropriados para idade, beber em copo)'),
        ('AUTOCUIDADO', 2, 'Higiene pessoal (lavar mãos e rosto, escovar dentes, pentear cabelo)'),
        ('AUTOCUIDADO', 3, 'Banho (lavar e secar o corpo, considerando habilidade apropriada para idade)'),
        ('AUTOCUIDADO', 4, 'Vestuário - Parte superior (colocar/tirar camisas, blusas, casacos)'),
        ('AUTOCUIDADO', 5, 'Vestuário - Parte inferior (colocar/tirar calças, fraldas, sapatos, meias)'),
        ('AUTOCUIDADO', 6, 'Uso do vaso sanitário (sentar, limpar-se, dar descarga, lavar as mãos após uso)'),

        # CONTROLE DE ESFÍNCTERES (2 itens)
        ('ESFINCT', 7, 'Controle de bexiga (controle da micção, considerando desenvolvimento para idade)'),
        ('ESFINCT', 8, 'Controle intestinal (controle da evacuação, considerando desenvolvimento para idade)'),

        # TRANSFERÊNCIAS (3 itens)
        ('TRANSF', 9, 'Transferência cadeira (sentar-se e levantar-se de cadeiras, cadeirão, cadeira de rodas)'),
        ('TRANSF', 10, 'Transferência vaso sanitário (sentar-se e levantar-se do vaso sanitário ou penico)'),
        ('TRANSF', 11, 'Transferência banheira (entrar e sair da banheira ou box do chuveiro)'),

        # LOCOMOÇÃO (2 itens)
        ('LOCOMO', 12, 'Locomoção (andar, engatinhar ou usar cadeira de rodas por 15 metros ou mais)'),
        ('LOCOMO', 13, 'Escadas (subir/descer 4 a 6 degraus, considerando habilidade para idade)'),

        # COMUNICAÇÃO (2 itens)
        ('COMUNIC', 14, 'Compreensão (entender comunicação verbal ou não-verbal apropriada para idade)'),
        ('COMUNIC', 15, 'Expressão (comunicar necessidades através de fala, gestos ou meios apropriados)'),

        # COGNIÇÃO SOCIAL (3 itens)
        ('COGN_SOC', 16, 'Interação social (responder e interagir com outras crianças e adultos)'),
        ('COGN_SOC', 17, 'Resolução de problemas (fazer escolhas, resolver problemas simples apropriados para idade)'),
        ('COGN_SOC', 18, 'Memória (lembrar pessoas, rotinas, objetos, apropriado para idade)')
    ]

    questoes_criadas = 0

    for dominio_codigo, numero, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        questao = Questao(
            codigo=f'WEEFIM_{numero:02d}',
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
                'escala_max': 7,
                'considera_idade': True
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
    print("SEED - WeeFIM (Functional Independence Measure for Children)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_weefim()

            # Criar instrumento
            instrumento = criar_instrumento_weefim(modulo)

            # Criar domínios
            dominios = criar_dominios_weefim(instrumento)

            # Criar questões
            total_questoes = criar_questoes_weefim(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: WeeFIM")
            print(f"Instrumento: 1 (6 meses a 7 anos)")
            print(f"Domínios: 6 (4 motores + 2 cognitivos)")
            print(f"Itens: {total_questoes}")
            print("=" * 80)
            print("\nCOMPOSIÇÃO:")
            print("- Motor (13 itens): Autocuidado (6) + Esfíncteres (2) + Transferências (3) + Locomoção (2)")
            print("- Cognitivo (5 itens): Comunicação (2) + Cognição Social (3)")
            print("\nIMPORTANTE: Avaliação considera desenvolvimento típico para cada faixa etária")
            print("=" * 80)

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
