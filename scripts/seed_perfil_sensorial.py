"""Seed do módulo Perfil Sensorial 2 usando arquivos estruturados."""
from __future__ import annotations
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'perfil_sensorial')

sys.path.insert(0, BASE_DIR)

from app import create_app, db  # noqa: E402
from app.models import Modulo, Instrumento, Dominio, Questao  # noqa: E402

INSTRUMENT_FILES = [
    'perfil_sens_cuidador.json',
    'perfil_sens_bebe.json',
    'perfil_sens_peq.json',
    'perfil_sens_escola.json',
    'perfil_sens_abrev.json'
]

ESCALA_PADRAO = [
    'QUASE_NUNCA|Quase nunca (10% ou menos)',
    'OCASIONALMENTE|Ocasionalmente (25%)',
    'METADE_TEMPO|Metade do tempo (50%)',
    'FREQUENTEMENTE|Frequentemente (75%)',
    'QUASE_SEMPRE|Quase sempre (90% ou mais)',
    'NAO_APLICA|Não se aplica'
]


def criar_modulo_perfil_sensorial() -> Modulo:
    print("Criando módulo Perfil Sensorial 2...")
    modulo = Modulo.query.filter_by(codigo='PERFIL_SENS').first()
    if modulo:
        print("Módulo Perfil Sensorial já existe. Pulando...")
        return modulo

    modulo = Modulo(
        codigo='PERFIL_SENS',
        nome='Perfil Sensorial 2',
        categoria='sensorial',
        icone='eye',
        cor='#9b59b6',
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=180
    )
    db.session.add(modulo)
    db.session.flush()
    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def carregar_instrumento(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as fp:
        return json.load(fp)


def criar_instrumento(modulo: Modulo, data: dict) -> Instrumento:
    print(f"\nProcessando instrumento {data['codigo']} ...")
    instrumento = Instrumento.query.filter_by(codigo=data['codigo']).first()
    if instrumento:
        instrumento.nome = data['nome']
        instrumento.idade_minima = data['idade_minima']
        instrumento.idade_maxima = data['idade_maxima']
        instrumento.contexto = data.get('contexto', 'casa')
        instrumento.modulo_id = modulo.id
        instrumento.ativo = True
        print("✓ Instrumento já existia, atualizado")
    else:
        instrumento = Instrumento(
            codigo=data['codigo'],
            nome=data['nome'],
            idade_minima=data['idade_minima'],
            idade_maxima=data['idade_maxima'],
            contexto=data.get('contexto', 'casa'),
            modulo_id=modulo.id,
            ativo=True
        )
        db.session.add(instrumento)
        db.session.flush()
        print(f"✓ Instrumento criado: {instrumento.nome}")

    dominios = {}
    for ordem, dominio_data in enumerate(data['dominios'], start=1):
        dominio = Dominio.query.filter_by(
            instrumento_id=instrumento.id,
            codigo=dominio_data['codigo']
        ).first()
        if dominio:
            dominio.nome = dominio_data['nome']
            dominio.ordem = ordem
        else:
            dominio = Dominio(
                instrumento_id=instrumento.id,
                codigo=dominio_data['codigo'],
                nome=dominio_data['nome'],
                ordem=ordem
            )
            db.session.add(dominio)
            db.session.flush()
        dominios[dominio_data['codigo']] = dominio

        for questao_data in dominio_data['questoes']:
            questao = Questao.query.filter_by(codigo=questao_data['codigo']).first()
            metadados = {
                'numero': questao_data['numero'],
                'icone': questao_data.get('icone', 'SEM_QUADRANTE'),
                'secao': dominio_data['codigo']
            }
            if questao:
                questao.texto = questao_data['texto']
                questao.numero = questao_data['numero']
                questao.numero_global = questao_data['numero_global']
                questao.dominio_id = dominio.id
                questao.metadados = metadados
                questao.opcoes_resposta = ESCALA_PADRAO
            else:
                questao = Questao(
                    codigo=questao_data['codigo'],
                    texto=questao_data['texto'],
                    dominio_id=dominio.id,
                    numero=questao_data['numero'],
                    numero_global=questao_data['numero_global'],
                    tipo_resposta='ESCALA_LIKERT',
                    obrigatoria=True,
                    opcoes_resposta=ESCALA_PADRAO,
                    metadados=metadados
                )
                db.session.add(questao)

    total = sum(len(d['questoes']) for d in data['dominios'])
    print(f"  -> {len(dominios)} domínios, {total} questões")
    return instrumento


def seed_perfil_sensorial():
    modulo = criar_modulo_perfil_sensorial()
    instrumentos = []

    for filename in INSTRUMENT_FILES:
        try:
            data = carregar_instrumento(filename)
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado em {DATA_DIR}, pulando...")
            continue
        instrumento = criar_instrumento(modulo, data)
        instrumentos.append(instrumento)

    db.session.commit()
    return {'modulo': modulo, 'instrumentos': instrumentos}


def main():
    print("=" * 80)
    print("SEED - Perfil Sensorial 2")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            resultado = seed_perfil_sensorial()
            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: {resultado['modulo'].nome}")
            extras = ', '.join(inst.codigo for inst in resultado['instrumentos'])
            print(f"Instrumentos carregados: {extras}")
            print("=" * 80)
        except Exception as exc:
            db.session.rollback()
            print(f"\n✗ ERRO: {exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
