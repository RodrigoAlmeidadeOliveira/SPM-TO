"""Gera arquivos JSON estruturados a partir das planilhas Perfil Sensorial (bebê, criança pequena, escolar)."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import unicodedata
import re

BASE_DIR = Path(__file__).resolve().parents[1]
DOCTOS_DIR = BASE_DIR / 'DOCTOS'
OUTPUT_DIR = BASE_DIR / 'data' / 'perfil_sensorial'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def canonical(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\s+', ' ', text).strip().upper()
    return text


CONFIGS = [
    {
        'arquivo': 'Perfil Sensorial Bebê.xlsx',
        'sheet': 'Sheet1',
        'codigo': 'PERFIL_SENS_BEBE',
        'nome': 'Perfil Sensorial 2 - Bebê (0-6 meses)',
        'idade_minima': 0,
        'idade_maxima': 1,
        'contexto': 'casa',
        'dominios': {
            'Processamento Geral': ('GERAL', 'Processamento Geral'),
            'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
            'Processamento Visual': ('VISUAL', 'Processamento Visual'),
            'Processamento do Tato': ('TATO', 'Processamento do Tato'),
            'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral')
        }
    },
    {
        'arquivo': 'Perfil Sensorial Criança Pequena.xlsx',
        'sheet': 'Sheet1',
        'codigo': 'PERFIL_SENS_PEQ',
        'nome': 'Perfil Sensorial 2 - Criança Pequena (7-35 meses)',
        'idade_minima': 1,
        'idade_maxima': 3,
        'contexto': 'casa',
        'dominios': {
            'Processamento Geral': ('GERAL', 'Processamento Geral'),
            'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
            'Processamento Visual': ('VISUAL', 'Processamento Visual'),
            'Processamento do Tato': ('TATO', 'Processamento do Tato'),
            'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral')
        }
    },
    {
        'arquivo': 'Perfil sensorial Escolar.xlsx',
        'sheet': 'Sheet1',
        'codigo': 'PERFIL_SENS_ESCOLA',
        'nome': 'Perfil Sensorial 2 - Escolar (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'escola',
        'dominios': {
            'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
            'Processamento Visual': ('VISUAL', 'Processamento Visual'),
            'Processamento do Tato': ('TATO', 'Processamento do Tato'),
            'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'Processamento da Posição do Corpo': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'Processamento de Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'Respostas Comportamentais': ('CONDUTA', 'Respostas Comportamentais')
        }
    }
    ,
    {
        'arquivo': 'Perfil Sensorial 3 a 14 anos.xlsx',
        'sheet': 'Sheet1',
        'codigo': 'PERFIL_SENS_CUIDADOR',
        'nome': 'Perfil Sensorial 2 - Questionário do Cuidador (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'casa',
        'dominios': {
            'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
            'Processamento Visual': ('VISUAL', 'Processamento Visual'),
            'Processamento do Tato': ('TATO', 'Processamento do Tato'),
            'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'Processamento da Posição do Corpo': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'Processamento de Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'Conduta associada ao processamento sensorial': ('CONDUTA', 'Conduta associada ao processamento sensorial'),
            'Respostas SOCIOEMOCIONAIS': ('SOCIOEMOCIONAL', 'Respostas Socioemocionais'),
            'Respostas de ATENÇÃO': ('ATENCAO', 'Respostas de Atenção')
        }
    },
    {
        'arquivo': 'perfil sensorial abreviado.xlsx',
        'sheet': 'Sheet1',
        'codigo': 'PERFIL_SENS_ABREV',
        'nome': 'Perfil Sensorial 2 - Questionário Abreviado (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'casa',
        'dominios': {
            'Processamento Auditivo': ('AUDITIVO', 'Processamento Auditivo'),
            'Processamento Visual': ('VISUAL', 'Processamento Visual'),
            'Processamento do Tato': ('TATO', 'Processamento do Tato'),
            'Processamento de Movimentos': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'Processamento da Posição do Corpo': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'Processamento de Sensibilidade Oral': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'Conduta associada ao processamento sensorial': ('CONDUTA', 'Conduta associada ao processamento sensorial'),
            'Respostas SOCIOEMOCIONAIS': ('SOCIOEMOCIONAL', 'Respostas Socioemocionais'),
            'Respostas de ATENÇÃO': ('ATENCAO', 'Respostas de Atenção')
        }
    }
]


def build_from_config(cfg):
    path = DOCTOS_DIR / cfg['arquivo']
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_excel(path, sheet_name=cfg['sheet'], header=None)

    dominios = {code: {'codigo': code, 'nome': nome, 'questoes': []}
                for code, nome in cfg['dominios'].values()}

    canonical_map = {canonical(name): value for name, value in cfg['dominios'].items()}

    current_dom = None
    numero_global = 0

    for _, row in df.iterrows():
        section = str(row[0]).strip() if pd.notna(row[0]) else ''
        item = row[1]
        descricao = str(row[2]).strip() if pd.notna(row[2]) else ''

        canon = canonical(section) if section else ''
        if canon in canonical_map:
            current_dom = canonical_map[canon][0]
            continue

        if pd.isna(item) or not descricao or not current_dom:
            continue

        try:
            numero = int(item)
        except (ValueError, TypeError):
            continue

        numero_global += 1
        questao = {
            'codigo': f"{cfg['codigo']}_{numero:03d}",
            'numero': numero,
            'numero_global': numero_global,
            'texto': descricao,
            'icone': 'SEM_QUADRANTE'
        }
        dominios[current_dom]['questoes'].append(questao)

    instrumento = {
        'codigo': cfg['codigo'],
        'nome': cfg['nome'],
        'idade_minima': cfg['idade_minima'],
        'idade_maxima': cfg['idade_maxima'],
        'contexto': cfg['contexto'],
        'dominios': [dom for dom in dominios.values() if dom['questoes']]
    }

    output = OUTPUT_DIR / f"{cfg['codigo'].lower()}.json"
    output.write_text(json.dumps(instrumento, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Gerado {output} com {sum(len(dom['questoes']) for dom in instrumento['dominios'])} questões")


def main():
    for cfg in CONFIGS:
        build_from_config(cfg)


if __name__ == '__main__':
    main()
