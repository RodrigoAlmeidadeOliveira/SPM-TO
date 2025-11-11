"""
Script de seed para o Módulo Perfil Sensorial 2 (Criança 3-14 anos)

Este script popula o banco de dados com:
- 1 módulo (Perfil Sensorial 2)
- 1 instrumento (Criança 3-14 anos)
- 9 domínios/seções sensoriais
- 86 questões distribuídas pelas seções

Uso:
    PYTHONPATH=. python scripts/seed_perfil_sensorial.py
"""

import sys
import os
import json

# Adicionar o diretório raiz ao PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data', 'perfil_sensorial')

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_perfil_sensorial():
    """Cria o módulo Perfil Sensorial 2"""
    print("Criando módulo Perfil Sensorial 2...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='PERFIL_SENS').first()
    if modulo_existente:
        print("Módulo Perfil Sensorial já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='PERFIL_SENS',
        nome='Perfil Sensorial 2 - Criança',
        categoria='sensorial',
        icone='eye',
        cor='#9b59b6',  # Roxo
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=180  # Reavaliar a cada 6 meses
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_perfil_sensorial(modulo):
    """Cria o instrumento para Perfil Sensorial 2 - Criança"""
    print("\nCriando instrumento...")

    instrumento = Instrumento.query.filter_by(codigo='PERFIL_SENS_CRIANCA').first()

    if instrumento:
        instrumento.nome = 'Perfil Sensorial 2 - Questionário do Cuidador (3-14 anos)'
        instrumento.modulo_id = modulo.id
        instrumento.idade_minima = 3
        instrumento.idade_maxima = 14
        instrumento.contexto = 'casa'
        instrumento.descricao = 'Questionário do cuidador para avaliação de processamento sensorial em crianças de 3 a 14 anos'
        print("✓ Instrumento já existia, atualizado")
    else:
        instrumento = Instrumento(
            codigo='PERFIL_SENS_CRIANCA',
            nome='Perfil Sensorial 2 - Questionário do Cuidador (3-14 anos)',
            modulo_id=modulo.id,
            idade_minima=3,
            idade_maxima=14,
            contexto='casa',
            descricao='Questionário do cuidador para avaliação de processamento sensorial em crianças de 3 a 14 anos'
        )

        db.session.add(instrumento)
        db.session.flush()
        print(f"✓ Instrumento criado: {instrumento.nome}")

    return instrumento


def criar_dominios_perfil_sensorial(instrumento):
    """Cria os 9 domínios/seções do Perfil Sensorial 2"""
    print("\nCriando domínios (seções sensoriais)...")

    dominios_dados = [
        {'codigo': 'AUDITIVO', 'nome': 'Processamento AUDITIVO', 'ordem': 1},
        {'codigo': 'VISUAL', 'nome': 'Processamento VISUAL', 'ordem': 2},
        {'codigo': 'TATO', 'nome': 'Processamento do TATO', 'ordem': 3},
        {'codigo': 'MOVIMENTOS', 'nome': 'Processamento de MOVIMENTOS', 'ordem': 4},
        {'codigo': 'POSICAO_CORPO', 'nome': 'Processamento da POSIÇÃO DO CORPO', 'ordem': 5},
        {'codigo': 'ORAL', 'nome': 'Processamento de SENSIBILIDADE ORAL', 'ordem': 6},
        {'codigo': 'CONDUTA', 'nome': 'CONDUTA associada ao processamento sensorial', 'ordem': 7},
        {'codigo': 'SOCIOEMOCIONAL', 'nome': 'Respostas SOCIOEMOCIONAIS associadas ao processamento sensorial', 'ordem': 8},
        {'codigo': 'ATENCAO', 'nome': 'Respostas de ATENÇÃO associadas ao processamento sensorial', 'ordem': 9}
    ]

    dominios = {}
    for dado in dominios_dados:
        dominio = Dominio.query.filter_by(
            instrumento_id=instrumento.id,
            codigo=dado['codigo']
        ).first()

        if dominio:
            dominio.nome = dado['nome']
            dominio.ordem = dado['ordem']
            print(f"  ✓ Domínio atualizado: {dominio.nome}")
        else:
            dominio = Dominio(
                codigo=dado['codigo'],
                nome=dado['nome'],
                instrumento_id=instrumento.id,
                ordem=dado['ordem']
            )
            db.session.add(dominio)
            db.session.flush()
            print(f"  ✓ Domínio criado: {dominio.nome}")

        dominios[dado['codigo']] = dominio

    return dominios


def criar_questoes_perfil_sensorial(dominios):
    """Cria todas as 86 questões do Perfil Sensorial 2"""
    print("\nCriando questões...")

    # Estrutura: (dominio_codigo, numero, codigo_icone, texto_questao)
    questoes_dados = [
        # AUDITIVO (1-8)
        ('AUDITIVO', 1, 'EV', 'reage intensamente a sons inesperados ou barulhentos (por exemplo, sirenes, cachorro latindo, secador de cabelo).'),
        ('AUDITIVO', 2, 'EV', 'coloca as mãos sobre os ouvidos para protegê-los do som.'),
        ('AUDITIVO', 3, 'SN', 'tem dificuldade em concluir tarefas quando há música tocando ou a TV está ligada.'),
        ('AUDITIVO', 4, 'SN', 'se distrai quando há muito barulho ao redor.'),
        ('AUDITIVO', 5, 'EV', 'torna-se improdutivo(a) com ruídos de fundo (por exemplo, ventilador, geladeira).'),
        ('AUDITIVO', 6, 'SN', 'para de prestar atenção em mim ou parece que me ignora.'),
        ('AUDITIVO', 7, 'SN', 'parece não ouvir quando eu o(a) chamo por seu nome (mesmo com sua audição sendo normal).'),
        ('AUDITIVO', 8, 'OB', 'gosta de barulhos estranhos ou faz barulho(s) para se divertir.'),

        # VISUAL (9-15)
        ('VISUAL', 9, 'SN', 'prefere brincar ou fazer tarefas em condições de pouca luz.'),
        ('VISUAL', 10, '', 'prefere vestir-se com roupas de cores brilhantes ou estampadas.'),
        ('VISUAL', 11, '', 'se diverte ao olhar para detalhes visuais em objetos.'),
        ('VISUAL', 12, 'OB', 'precisa de ajuda para encontrar objetos que são óbvios para outros.'),
        ('VISUAL', 13, 'SN', 'se incomoda mais com luzes brilhantes do que outras crianças da mesma idade.'),
        ('VISUAL', 14, 'EX', 'observa as pessoas conforme elas se movem ao redor da sala.'),
        ('VISUAL', 15, 'EV', 'se incomoda com luzes brilhantes (por exemplo, se esconde da luz solar que reluz através da janela do carro).*'),

        # TATO (16-26)
        ('TATO', 16, 'SN', 'mostra desconforto durante momentos de cuidado pessoal (por exemplo, briga ou chora durante o corte de cabelo, lavagem do rosto, corte das unhas das mãos).'),
        ('TATO', 17, '', 'se irrita com o uso de sapatos ou meias.'),
        ('TATO', 18, 'EV', 'mostra uma resposta emocional ou agressiva ao ser tocado(a).'),
        ('TATO', 19, 'SN', 'fica ansioso(a) quando fica de pé em proximidade a outros (por exemplo, em uma fila).'),
        ('TATO', 20, 'SN', 'esfrega ou coça uma parte do corpo que foi tocada.'),
        ('TATO', 21, 'EX', 'toca as pessoas ou objetos a ponto de incomodar outros.'),
        ('TATO', 22, 'EX', 'exibe a necessidade de tocar brinquedos, superfícies ou texturas (por exemplo, quer obter a sensação de tudo ao redor).'),
        ('TATO', 23, 'OB', 'parece não ter consciência quanto à dor.'),
        ('TATO', 24, 'OB', 'parece não ter consciência quanto a mudanças de temperatura.'),
        ('TATO', 25, 'EX', 'toca pessoas e objetos mais do que crianças da mesma idade.'),
        ('TATO', 26, 'OB', 'parece alheio(a) quanto ao fato de suas mãos ou face estarem sujas.'),

        # MOVIMENTOS (27-34)
        ('MOVIMENTOS', 27, 'EX', 'busca movimentar-se até o ponto que interfere com rotinas diárias (por exemplo, não consegue ficar quieto, demonstra inquietude).'),
        ('MOVIMENTOS', 28, 'EX', 'faz movimento de balançar na cadeira, no chão ou enquanto está em pé.'),
        ('MOVIMENTOS', 29, '', 'hesita subir ou descer calçadas ou degraus (por exemplo, é cauteloso, para antes de se movimentar).'),
        ('MOVIMENTOS', 30, 'EX', 'fica animado(a) durante tarefas que envolvem movimento.'),
        ('MOVIMENTOS', 31, 'EX', 'se arrisca ao se movimentar ou escalar de modo perigoso.'),
        ('MOVIMENTOS', 32, 'EX', 'procura oportunidades para cair sem se importar com a própria segurança (por exemplo, cai de propósito).'),
        ('MOVIMENTOS', 33, 'OB', 'perde o equilíbrio inesperadamente ao caminhar sobre uma superfície irregular.'),
        ('MOVIMENTOS', 34, 'OB', 'esbarra em coisas, sem conseguir notar objetos ou pessoas no caminho.'),

        # POSICAO_CORPO (35-42)
        ('POSICAO_CORPO', 35, 'OB', 'move-se de modo rígido.'),
        ('POSICAO_CORPO', 36, 'OB', 'fica cansado(a) facilmente, principalmente quando está em pé ou mantendo o corpo em uma posição.'),
        ('POSICAO_CORPO', 37, 'OB', 'parece ter músculos fracos.'),
        ('POSICAO_CORPO', 38, 'OB', 'se apoia para se sustentar (por exemplo, segura a cabeça com as mãos, apoia-se em uma parede).'),
        ('POSICAO_CORPO', 39, 'OB', 'se segura a objetos, paredes ou corrimões mais do que as crianças da mesma idade.'),
        ('POSICAO_CORPO', 40, 'OB', 'ao andar, faz barulho, como se os pés fossem pesados.'),
        ('POSICAO_CORPO', 41, 'EX', 'se inclina para se apoiar em móveis ou em outras pessoas.'),
        ('POSICAO_CORPO', 42, '', 'precisa de cobertores pesados para dormir.'),

        # ORAL (43-52)
        ('ORAL', 43, '', 'fica com ânsia de vômito facilmente com certas texturas de alimentos ou utensílios alimentares na boca.'),
        ('ORAL', 44, 'SN', 'rejeita certos gostos ou cheiros de comida que são, normalmente, parte de dietas de crianças.'),
        ('ORAL', 45, 'SN', 'se alimenta somente de certos sabores (por exemplo, doce, salgado).'),
        ('ORAL', 46, 'SN', 'limita-se quanto a certas texturas de alimentos.'),
        ('ORAL', 47, 'SN', 'é exigente para comer, principalmente com relação às texturas de alimentos.'),
        ('ORAL', 48, 'EX', 'cheira objetos não comestíveis.'),
        ('ORAL', 49, 'EX', 'mostra uma forte preferência por certos sabores.'),
        ('ORAL', 50, 'EX', 'deseja intensamente certos alimentos, gostos ou cheiros.'),
        ('ORAL', 51, 'EX', 'coloca objetos na boca (por exemplo, lápis, mãos).'),
        ('ORAL', 52, 'SN', 'morde a língua ou lábios mais do que as crianças da mesma idade.'),

        # CONDUTA (53-61)
        ('CONDUTA', 53, 'OB', 'parece propenso(a) a acidentes.'),
        ('CONDUTA', 54, 'OB', 'se apressa em atividades de colorir, escrever ou desenhar.'),
        ('CONDUTA', 55, 'EX', 'se expõe a riscos excessivos (por exemplo, sobe alto em uma árvore, salta de móveis altos) que comprometem sua própria segurança.'),
        ('CONDUTA', 56, 'EX', 'parece ser mais ativo(a) do que crianças da mesma idade.'),
        ('CONDUTA', 57, 'OB', 'faz as coisas de uma maneira mais difícil do que necessário (por exemplo, perde tempo, move-se lentamente).'),
        ('CONDUTA', 58, 'EV', 'pode ser teimoso(a) e não cooperativo(a).'),
        ('CONDUTA', 59, 'EV', 'faz birra.'),
        ('CONDUTA', 60, 'EX', 'parece se divertir quando cai.'),
        ('CONDUTA', 61, 'EV', 'resiste ao contato visual comigo ou com outros.'),

        # SOCIOEMOCIONAL (62-75)
        ('SOCIOEMOCIONAL', 62, 'OB', 'parece ter baixa autoestima (por exemplo, dificuldade de gostar de si mesmo(a)).'),
        ('SOCIOEMOCIONAL', 63, 'EV', 'precisa de apoio positivo para enfrentar situações desafiadoras.'),
        ('SOCIOEMOCIONAL', 64, 'EV', 'é sensível às críticas.'),
        ('SOCIOEMOCIONAL', 65, 'EV', 'possui medos definidos e previsíveis.'),
        ('SOCIOEMOCIONAL', 66, 'EV', 'se expressa sentindo-se como um fracasso.'),
        ('SOCIOEMOCIONAL', 67, 'EV', 'é demasiadamente sério(a).'),
        ('SOCIOEMOCIONAL', 68, 'EV', 'tem fortes explosões emocionais quando não consegue concluir uma tarefa.'),
        ('SOCIOEMOCIONAL', 69, 'SN', 'tem dificuldade de interpretar linguagem corporal ou expressões faciais.'),
        ('SOCIOEMOCIONAL', 70, 'EV', 'fica frustrado(a) facilmente.'),
        ('SOCIOEMOCIONAL', 71, 'EV', 'possui medos que interferem nas rotinas diárias.'),
        ('SOCIOEMOCIONAL', 72, 'EV', 'fica angustiado(a) com mudanças nos planos, rotinas ou expectativas.'),
        ('SOCIOEMOCIONAL', 73, 'SN', 'precisa de mais proteção contra acontecimentos da vida do que crianças da mesma idade (por exemplo, é indefeso(a) física ou emocionalmente).'),
        ('SOCIOEMOCIONAL', 74, 'EV', 'interage ou participa em grupos menos que crianças da mesma idade.'),
        ('SOCIOEMOCIONAL', 75, 'EV', 'tem dificuldade com amizades (por exemplo, fazer ou manter amigos).'),

        # ATENCAO (76-86)
        ('ATENCAO', 76, 'OB', 'não faz contato visual comigo durante interações no dia a dia.'),
        ('ATENCAO', 77, 'SN', 'tem dificuldade para prestar atenção.'),
        ('ATENCAO', 78, 'SN', 'se desvia de tarefas para observar todas as ações na sala.'),
        ('ATENCAO', 79, 'OB', 'parece alheio(a) dentro de um ambiente ativo (por exemplo, não tem consciência quanto à atividade).'),
        ('ATENCAO', 80, 'OB', 'olha fixamente, de maneira intensa, para objetos.'),
        ('ATENCAO', 81, 'EV', 'olha fixamente, de maneira intensa, para as pessoas.'),
        ('ATENCAO', 82, 'EX', 'observa a todos conforme se movem ao redor da sala.'),
        ('ATENCAO', 83, 'EX', 'muda de uma coisa para outra de modo a interferir com as atividades.'),
        ('ATENCAO', 84, 'SN', 'se perde facilmente.'),
        ('ATENCAO', 85, 'OB', 'tem dificuldade para encontrar objetos em espaços cheios de coisas (por exemplo, sapatos em um quarto bagunçado, lápis na "gaveta de bagunças").'),
        ('ATENCAO', 86, 'OB', 'parece não se dar conta quando pessoas entram na sala.*')
    ]

    questoes_criadas = 0
    numero_global = 0

    for dominio_codigo, numero, icone, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        numero_global += 1
        questao = Questao.query.filter_by(codigo=f'PS_{numero:03d}').first()

        dados_questao = dict(
            texto=f'Meu/minha filho(a)... {texto}',
            dominio_id=dominio.id,
            ordem=numero,
            numero=numero,
            numero_global=numero_global,
            tipo_resposta='ESCALA_LIKERT',
            obrigatoria=True,
            opcoes_resposta=[
                'QUASE_NUNCA|Quase nunca (10% ou menos)',
                'OCASIONALMENTE|Ocasionalmente (25%)',
                'METADE_TEMPO|Metade do tempo (50%)',
                'FREQUENTEMENTE|Frequentemente (75%)',
                'QUASE_SEMPRE|Quase sempre (90% ou mais)',
                'NAO_APLICA|Não se aplica'
            ],
            metadados={
                'numero': numero,
                'icone': icone if icone else 'SEM_QUADRANTE',
                'secao': dominio_codigo
            }
        )

        if questao:
            for campo, valor in dados_questao.items():
                setattr(questao, campo, valor)
            print(f"  - Questão atualizada: PS_{numero:03d}")
        else:
            questao = Questao(codigo=f'PS_{numero:03d}', **dados_questao)
            db.session.add(questao)
            questoes_criadas += 1
            if questoes_criadas % 10 == 0:
                print(f"  ✓ {questoes_criadas} questões criadas...")

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} questões novas adicionadas/atualizadas!")

    return questoes_criadas


def carregar_instrumento_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f'Arquivo não encontrado: {path}')
    with open(path, 'r', encoding='utf-8') as fp:
        return json.load(fp)


def criar_instrumento_from_json(modulo, data):
    print(f"\nCriando instrumento {data['codigo']} a partir de JSON...")

    instrumento = Instrumento.query.filter_by(codigo=data['codigo']).first()
    if instrumento:
        instrumento.nome = data['nome']
        instrumento.idade_minima = data['idade_minima']
        instrumento.idade_maxima = data['idade_maxima']
        instrumento.contexto = data.get('contexto', 'casa')
        instrumento.modulo_id = modulo.id
        print("✓ Instrumento já existia, atualizado")
    else:
        instrumento = Instrumento(
            codigo=data['codigo'],
            nome=data['nome'],
            idade_minima=data['idade_minima'],
            idade_maxima=data['idade_maxima'],
            contexto=data.get('contexto', 'casa'),
            modulo_id=modulo.id
        )
        db.session.add(instrumento)
        db.session.flush()
        print(f"✓ Instrumento criado: {instrumento.nome}")

    opcoes = [
        'QUASE_NUNCA|Quase nunca (10% ou menos)',
        'OCASIONALMENTE|Ocasionalmente (25%)',
        'METADE_TEMPO|Metade do tempo (50%)',
        'FREQUENTEMENTE|Frequentemente (75%)',
        'QUASE_SEMPRE|Quase sempre (90% ou mais)',
        'NAO_APLICA|Não se aplica'
    ]

    codigo_para_dominio = {}
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
        codigo_para_dominio[dominio_data['codigo']] = dominio

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
                questao.opcoes_resposta = opcoes
            else:
                questao = Questao(
                    codigo=questao_data['codigo'],
                    texto=questao_data['texto'],
                    dominio_id=dominio.id,
                    numero=questao_data['numero'],
                    numero_global=questao_data['numero_global'],
                    tipo_resposta='ESCALA_LIKERT',
                    obrigatoria=True,
                    opcoes_resposta=opcoes,
                    metadados=metadados
                )
                db.session.add(questao)

    return instrumento


def seed_perfil_sensorial():
    """Executa o seed do Perfil Sensorial dentro de um app context ativo."""
    modulo = criar_modulo_perfil_sensorial()
    instrumento = criar_instrumento_perfil_sensorial(modulo)
    dominios = criar_dominios_perfil_sensorial(instrumento)
    total_questoes = criar_questoes_perfil_sensorial(dominios)

    adicionais = []
    for filename in ['perfil_sens_bebe.json', 'perfil_sens_peq.json', 'perfil_sens_escola.json', 'perfil_sens_abrev.json']:
        try:
            data = carregar_instrumento_json(filename)
        except FileNotFoundError:
            continue
        instrumento_extra = criar_instrumento_from_json(modulo, data)
        adicionais.append(instrumento_extra)

    db.session.commit()
    return {
        'modulo': modulo,
        'instrumento': instrumento,
        'instrumentos_adicionais': adicionais,
        'dominios': dominios,
        'total_questoes': total_questoes
    }


def main():
    """Função principal para execução via linha de comando"""
    print("=" * 80)
    print("SEED - Perfil Sensorial 2 (Criança 3-14 anos)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            resultado = seed_perfil_sensorial()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: {resultado['modulo'].nome}")
            print("Instrumento base: Perfil Sensorial 2 - Criança")
            print("Domínios: 9 seções sensoriais")
            print(f"Questões (novas ou atualizadas): {resultado['total_questoes']}")
            if resultado['instrumentos_adicionais']:
                extras = ', '.join(inst.codigo for inst in resultado['instrumentos_adicionais'])
                print(f"Instrumentos adicionais carregados: {extras}")
            print("=" * 80)

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
