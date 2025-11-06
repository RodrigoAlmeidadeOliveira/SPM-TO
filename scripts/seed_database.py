"""
Script para popular o banco de dados com instrumentos e questões das planilhas SPM
"""
import openpyxl
from pathlib import Path
from app import db
from app.models import Instrumento, Dominio, Questao, TabelaReferencia


def seed_database():
    """Popula o banco de dados com dados das planilhas"""
    doctos_path = Path(__file__).parent.parent / 'DOCTOS'

    # Definição dos instrumentos
    instrumentos_config = [
        {
            'codigo': 'SPM_5_12_CASA',
            'nome': 'SPM 5-12 anos - Casa',
            'idade_minima': 5,
            'idade_maxima': 12,
            'contexto': 'casa',
            'planilha': 'Planilha PEI SPM 5-12 - casa.xlsx'
        },
        {
            'codigo': 'SPM_5_12_ESCOLA',
            'nome': 'SPM 5-12 anos - Escola',
            'idade_minima': 5,
            'idade_maxima': 12,
            'contexto': 'escola',
            'planilha': 'Planilha PEI SPM 5-12 - escola.xlsx'
        },
        {
            'codigo': 'SPM_P_3_5_CASA',
            'nome': 'SPM-P 3-5 anos - Casa',
            'idade_minima': 3,
            'idade_maxima': 5,
            'contexto': 'casa',
            'planilha': 'Planilha PEI SPM-P 3-5 - casa.xlsx'
        },
        {
            'codigo': 'SPM_P_3_5_ESCOLA',
            'nome': 'SPM-P 3-5 anos - Escola',
            'idade_minima': 3,
            'idade_maxima': 5,
            'contexto': 'escola',
            'planilha': 'Planilha PEI SPM-P 3-5 - escola.xlsx'
        }
    ]

    # Definição dos domínios (ordem e características)
    dominios_config = {
        'SPM_5_12': [
            {'codigo': 'SOC', 'nome': 'Participação Social', 'ordem': 1, 'escala_invertida': False},
            {'codigo': 'VIS', 'nome': 'Visão', 'ordem': 2, 'escala_invertida': True},
            {'codigo': 'HEA', 'nome': 'Audição', 'ordem': 3, 'escala_invertida': True},
            {'codigo': 'TOU', 'nome': 'Tato', 'ordem': 4, 'escala_invertida': True},
            {'codigo': 'BOD', 'nome': 'Consciência Corporal', 'ordem': 5, 'escala_invertida': True},
            {'codigo': 'BAL', 'nome': 'Equilíbrio e Movimento', 'ordem': 6, 'escala_invertida': True},
            {'codigo': 'PLA', 'nome': 'Planejamento e Ideação', 'ordem': 7, 'escala_invertida': True}
        ],
        'SPM_P_3_5': [
            {'codigo': 'SOC', 'nome': 'Participação Social', 'ordem': 1, 'escala_invertida': False},
            {'codigo': 'VIS', 'nome': 'Visão', 'ordem': 2, 'escala_invertida': True},
            {'codigo': 'HEA', 'nome': 'Audição', 'ordem': 3, 'escala_invertida': True},
            {'codigo': 'OLF', 'nome': 'Olfato e Paladar', 'ordem': 4, 'escala_invertida': True},
            {'codigo': 'TOU', 'nome': 'Tato', 'ordem': 5, 'escala_invertida': True},
            {'codigo': 'BOD', 'nome': 'Consciência Corporal', 'ordem': 6, 'escala_invertida': True},
            {'codigo': 'BAL', 'nome': 'Equilíbrio e Movimento', 'ordem': 7, 'escala_invertida': True},
            {'codigo': 'PLA', 'nome': 'Planejamento e Ideação', 'ordem': 8, 'escala_invertida': True}
        ]
    }

    print('Iniciando população do banco de dados...')

    # Criar instrumentos
    for config in instrumentos_config:
        print(f"\nProcessando {config['nome']}...")

        # Criar instrumento
        instrumento = Instrumento(
            codigo=config['codigo'],
            nome=config['nome'],
            idade_minima=config['idade_minima'],
            idade_maxima=config['idade_maxima'],
            contexto=config['contexto'],
            instrucoes='Por favor, responda as perguntas deste formulário de acordo com a frequência.'
        )
        db.session.add(instrumento)
        db.session.flush()

        # Determinar conjunto de domínios
        dominio_set = 'SPM_P_3_5' if 'SPM_P_3_5' in config['codigo'] else 'SPM_5_12'

        # Criar domínios
        for dom_config in dominios_config[dominio_set]:
            dominio = Dominio(
                instrumento_id=instrumento.id,
                codigo=dom_config['codigo'],
                nome=dom_config['nome'],
                ordem=dom_config['ordem'],
                escala_invertida=dom_config['escala_invertida']
            )
            db.session.add(dominio)
            db.session.flush()

            print(f"  - Domínio criado: {dom_config['nome']}")

        # Ler questões da planilha
        try:
            planilha_path = doctos_path / config['planilha']
            extrair_questoes_planilha(planilha_path, instrumento)
        except Exception as e:
            print(f"  AVISO: Erro ao ler questões da planilha: {e}")

    db.session.commit()
    print('\n✓ Banco de dados populado com sucesso!')


def extrair_questoes_planilha(planilha_path, instrumento):
    """
    Extrai questões da planilha Excel

    Args:
        planilha_path: Caminho para a planilha
        instrumento: Instância de Instrumento
    """
    wb = openpyxl.load_workbook(planilha_path)
    ws = wb['Entrada de Dados']

    # Mapeamento de domínios
    dominios = {d.codigo: d for d in instrumento.dominios}

    # Variáveis de controle
    dominio_atual = None
    numero_questao = 1
    numero_questao_dominio = 1

    # Percorrer linhas da planilha (aproximadamente linhas 31 em diante)
    for row_idx in range(31, min(200, ws.max_row)):
        row = ws[row_idx]
        celula_b = row[1].value  # Coluna B

        if celula_b:
            celula_b_str = str(celula_b).strip()

            # Detectar início de domínio (ex: "1. Participação Social")
            if celula_b_str and celula_b_str[0].isdigit() and '.' in celula_b_str[:3]:
                # É um cabeçalho de domínio
                nome_dominio = celula_b_str.split('.', 1)[1].strip()

                # Encontrar domínio correspondente
                for codigo, dom in dominios.items():
                    if dom.nome.lower() in nome_dominio.lower():
                        dominio_atual = dom
                        numero_questao_dominio = 1
                        print(f"    Processando questões do domínio: {dom.nome}")
                        break

            # Linha SCORE indica fim do domínio
            elif celula_b_str.upper() == 'SCORE':
                dominio_atual = None

            # Se tem domínio atual e a célula contém texto de questão
            elif dominio_atual and len(celula_b_str) > 20:
                # Extrair número da questão se houver (ex: "1.Brinca com amigos...")
                texto_questao = celula_b_str

                # Verificar se já não é um cabeçalho (linhas como "Esta criança:")
                if not texto_questao.lower().startswith('esta criança'):
                    questao = Questao(
                        dominio_id=dominio_atual.id,
                        numero=numero_questao_dominio,
                        numero_global=numero_questao,
                        texto=texto_questao
                    )
                    db.session.add(questao)

                    numero_questao += 1
                    numero_questao_dominio += 1

    print(f"    Total de questões extraídas: {numero_questao - 1}")
