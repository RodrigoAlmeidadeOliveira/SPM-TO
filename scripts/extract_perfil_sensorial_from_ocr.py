"""Extrai dados estruturados dos arquivos OCR do Perfil Sensorial."""
from __future__ import annotations
import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OCR_DIR = BASE_DIR / 'tmp' / 'ocr'
OUTPUT_DIR = BASE_DIR / 'data' / 'perfil_sensorial'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INSTRUMENTS = [
    {
        'codigo': 'PERFIL_SENS_BEBE',
        'nome': 'Perfil Sensorial 2 - Bebê (0-6 meses)',
        'idade_minima': 0,
        'idade_maxima': 1,
        'contexto': 'casa',
        'arquivo': 'Perfil_Sensorial_Bebê.txt',
        'dominios': {
            'PROCESSAMENTO GERAL': ('GERAL', 'Processamento Geral'),
            'PROCESSAMENTO AUDITIVO': ('AUDITIVO', 'Processamento Auditivo'),
            'PROCESSAMENTO VISUAL': ('VISUAL', 'Processamento Visual'),
            'PROCESSAMENTO DO TATO': ('TATO', 'Processamento do Tato'),
            'PROCESSAMENTO DE MOVIMENTOS': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'PROCESSAMENTO DE SENSIBILIDADE ORAL': ('ORAL', 'Processamento de Sensibilidade Oral')
        }
    },
    {
        'codigo': 'PERFIL_SENS_PEQ',
        'nome': 'Perfil Sensorial 2 - Criança Pequena (7-35 meses)',
        'idade_minima': 1,
        'idade_maxima': 3,
        'contexto': 'casa',
        'arquivo': 'Perfil_Sensorial_Criança_Pequena.txt',
        'dominios': {
            'PROCESSAMENTO GERAL': ('GERAL', 'Processamento Geral'),
            'PROCESSAMENTO AUDITIVO': ('AUDITIVO', 'Processamento Auditivo'),
            'PROCESSAMENTO VISUAL': ('VISUAL', 'Processamento Visual'),
            'PROCESSAMENTO DO TATO': ('TATO', 'Processamento do Tato'),
            'PROCESSAMENTO DE MOVIMENTOS': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'PROCESSAMENTO DE SENSIBILIDADE ORAL': ('ORAL', 'Processamento de Sensibilidade Oral')
        }
    },
    {
        'codigo': 'PERFIL_SENS_CUIDADOR',
        'nome': 'Perfil Sensorial 2 - Cuidador (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'casa',
        'arquivo': 'Perfil_Sensorial_3_a_14_anos.txt',
        'dominios': {
            'PROCESSAMENTO AUDITIVO': ('AUDITIVO', 'Processamento Auditivo'),
            'PROCESSAMENTO VISUAL': ('VISUAL', 'Processamento Visual'),
            'PROCESSAMENTO DO TATO': ('TATO', 'Processamento do Tato'),
            'PROCESSAMENTO DE MOVIMENTOS': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'PROCESSAMENTO DA POSICAO DO CORPO': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'PROCESSAMENTO DE SENSIBILIDADE ORAL': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'CONDUTA ASSOCIADA AO PROCESSAMENTO SENSORIAL': ('CONDUTA', 'Conduta associada ao processamento sensorial'),
            'RESPOSTAS SOCIOEMOCIONAIS': ('SOCIOEMOCIONAL', 'Respostas Socioemocionais'),
            'RESPOSTAS DE ATENCAO': ('ATENCAO', 'Respostas de Atenção')
        }
    },
    {
        'codigo': 'PERFIL_SENS_ESCOLA',
        'nome': 'Perfil Sensorial 2 - Escolar (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'escola',
        'arquivo': 'Perfil_sensorial_Escolar.txt',
        'dominios': {
            'PROCESSAMENTO AUDITIVO': ('AUDITIVO', 'Processamento Auditivo'),
            'PROCESSAMENTO VISUAL': ('VISUAL', 'Processamento Visual'),
            'PROCESSAMENTO DO TATO': ('TATO', 'Processamento do Tato'),
            'PROCESSAMENTO DE MOVIMENTOS': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'PROCESSAMENTO DA POSICAO DO CORPO': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'PROCESSAMENTO DE SENSIBILIDADE ORAL': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'CONDUTA ASSOCIADA AO PROCESSAMENTO SENSORIAL': ('CONDUTA', 'Conduta associada ao processamento sensorial'),
            'RESPOSTAS SOCIOEMOCIONAIS': ('SOCIOEMOCIONAL', 'Respostas Socioemocionais'),
            'RESPOSTAS DE ATENCAO': ('ATENCAO', 'Respostas de Atenção')
        }
    },
    {
        'codigo': 'PERFIL_SENS_ABREV',
        'nome': 'Perfil Sensorial 2 - Questionário abreviado (3-14 anos)',
        'idade_minima': 3,
        'idade_maxima': 14,
        'contexto': 'casa',
        'arquivo': 'perfil_sensorial_abreviado.txt',
        'dominios': {
            'PROCESSAMENTO AUDITIVO': ('AUDITIVO', 'Processamento Auditivo'),
            'PROCESSAMENTO VISUAL': ('VISUAL', 'Processamento Visual'),
            'PROCESSAMENTO DO TATO': ('TATO', 'Processamento do Tato'),
            'PROCESSAMENTO DE MOVIMENTOS': ('MOVIMENTOS', 'Processamento de Movimentos'),
            'PROCESSAMENTO DA POSICAO DO CORPO': ('POSICAO_CORPO', 'Processamento da Posição do Corpo'),
            'PROCESSAMENTO DE SENSIBILIDADE ORAL': ('ORAL', 'Processamento de Sensibilidade Oral'),
            'CONDUTA ASSOCIADA AO PROCESSAMENTO SENSORIAL': ('CONDUTA', 'Conduta associada ao processamento sensorial'),
            'RESPOSTAS SOCIOEMOCIONAIS': ('SOCIOEMOCIONAL', 'Respostas Socioemocionais'),
            'RESPOSTAS DE ATENCAO': ('ATENCAO', 'Respostas de Atenção')
        }
    },
]

ICONES = {'EX', 'EV', 'SN', 'OB'}


def normalize(text: str) -> str:
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').upper()


def canonical_domain(text: str) -> str:
    normalized = normalize(text)
    normalized = normalized.split('(')[0]
    normalized = re.sub(r'[^A-Z ]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r'[|_]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip(' .-')


def parse_instrument(cfg):
    path = OCR_DIR / cfg['arquivo']
    if not path.exists():
        raise FileNotFoundError(f'OCR file not found: {path}')

    raw_lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    lines = [line.rstrip() for line in raw_lines if line.strip()]

    domain_alias = {}
    for key, value in cfg['dominios'].items():
        domain_alias[canonical_domain(key)] = value

    current_domain = None
    numero_global = 0
    dominios_data = {code: {'codigo': code, 'nome': nome, 'questoes': []}
                      for code, nome in cfg['dominios'].values()}

    domain_regex = re.compile(r'^PROCESSAMENTO\s+[A-ZÇÃÕ ]+', re.IGNORECASE)
    question_regex = re.compile(r'^(?:([A-Z]{2})\s+)?(\d{1,3})(?:[\s._-]+)?(.+)$')

    for line in lines:
        dom_key = canonical_domain(line)
        if dom_key in domain_alias:
            current_domain = domain_alias[dom_key][0]
            continue

        match = question_regex.match(line)
        if match and current_domain:
            icone = match.group(1)
            numero = int(match.group(2))
            texto = clean_text(match.group(3))
            if len(texto) < 3:
                continue
            numero_global += 1
            questao = {
                'codigo': f"{cfg['codigo']}_{numero:03d}",
                'numero': numero,
                'numero_global': numero_global,
                'texto': texto,
                'icone': icone if icone in ICONES else 'SEM_QUADRANTE'
            }
            dominios_data[current_domain]['questoes'].append(questao)

    instrument_data = {
        'codigo': cfg['codigo'],
        'nome': cfg['nome'],
        'idade_minima': cfg['idade_minima'],
        'idade_maxima': cfg['idade_maxima'],
        'contexto': cfg['contexto'],
        'dominios': [dom for dom in dominios_data.values() if dom['questoes']]
    }

    output_path = OUTPUT_DIR / f"{cfg['codigo'].lower()}.json"
    output_path.write_text(json.dumps(instrument_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Gerado {output_path} ({sum(len(d['questoes']) for d in dominios_data.values())} questões)")


def main():
    for cfg in INSTRUMENTS:
        parse_instrument(cfg)


if __name__ == '__main__':
    main()
