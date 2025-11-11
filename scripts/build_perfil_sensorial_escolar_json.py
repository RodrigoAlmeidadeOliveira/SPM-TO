"""Extrai dados estruturados da planilha Perfil sensorial Escolar.xlsx."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / 'DOCTOS' / 'Perfil sensorial Escolar.xlsx'
OUTPUT_PATH = BASE_DIR / 'data' / 'perfil_sensorial' / 'perfil_sens_escolar.json'
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

DOMINIO_MAP = {
    'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
    'Processamento Visual': ('VISUAL', 'Processamento Visual'),
    'Processamento do Tato': ('TATO', 'Processamento do Tato'),
    'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
    'Processamento da Posição do Corpo': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
    'Processamento de Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral'),
    'Respostas Comportamentais': ('CONDUTA', 'Respostas Comportamentais')
}


def main():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(EXCEL_PATH)

    df = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1', header=None)

    dominios = {code: {'codigo': code, 'nome': nome, 'questoes': []}
                for code, nome in DOMINIO_MAP.values()}

    current_dom = None
    numero_global = 0

    for _, row in df.iterrows():
        section = str(row[0]).strip() if not pd.isna(row[0]) else ''
        item = row[1]
        descricao = str(row[2]).strip() if not pd.isna(row[2]) else ''

        if section in DOMINIO_MAP:
            current_dom = DOMINIO_MAP[section][0]

        if pd.isna(item) or not descricao or not current_dom:
            continue

        try:
            numero = int(item)
        except (ValueError, TypeError):
            continue

        numero_global += 1
        questao = {
            'codigo': f'PERFIL_SENS_ESCOLA_{numero:03d}',
            'numero': numero,
            'numero_global': numero_global,
            'texto': descricao,
            'icone': 'SEM_QUADRANTE'
        }
        dominios[current_dom]['questoes'].append(questao)

    instrumento = {
        'codigo': 'PERFIL_SENS_ESCOLA',
        'nome': 'Perfil Sensorial 2 - Escolar (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'escola',
        'dominios': [dom for dom in dominios.values() if dom['questoes']]
    }

    OUTPUT_PATH.write_text(json.dumps(instrumento, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Gerado {OUTPUT_PATH} com {numero_global} questões")


if __name__ == '__main__':
    main()
