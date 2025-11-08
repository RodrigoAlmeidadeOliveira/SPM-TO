"""
Script de seed para o Módulo Perfil Sensorial - Bebê (0-6 meses)

Este script popula o banco de dados com:
- 1 módulo (Perfil Sensorial - Bebê)
- 1 instrumento (Bebê 0-6 meses)
- 5 domínios/seções sensoriais
- 36 questões distribuídas pelas seções

Uso:
    PYTHONPATH=. python scripts/seed_perfil_sensorial_infant.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_perfil_sensorial_infant():
    """Cria o módulo Perfil Sensorial - Bebê"""
    print("Criando módulo Perfil Sensorial - Bebê...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='PERFIL_SENS_INFANT').first()
    if modulo_existente:
        print("Módulo Perfil Sensorial - Bebê já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='PERFIL_SENS_INFANT',
        nome='Perfil Sensorial - Bebê',
        categoria='sensorial',
        icone='baby',
        cor='#e74c3c',  # Vermelho claro
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=60  # Reavaliar a cada 2 meses (desenvolvimento rápido)
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_perfil_sensorial_infant(modulo):
    """Cria o instrumento para Perfil Sensorial - Bebê"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='PERFIL_SENS_INFANT_0_6',
        nome='Perfil Sensorial - Bebê (0-6 meses)',
        modulo_id=modulo.id,
        idade_minima=0,
        idade_maxima=0,  # 0 representa 6 meses
        contexto='casa',
        descricao='Questionário do cuidador para avaliação de processamento sensorial em bebês de 0 a 6 meses'
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_perfil_sensorial_infant(instrumento):
    """Cria os 5 domínios/seções do Perfil Sensorial - Bebê"""
    print("\nCriando domínios (seções sensoriais)...")

    dominios_dados = [
        {'codigo': 'GERAL', 'nome': 'Processamento GERAL', 'ordem': 1},
        {'codigo': 'AUDITIVO', 'nome': 'Processamento AUDITIVO', 'ordem': 2},
        {'codigo': 'VISUAL', 'nome': 'Processamento VISUAL', 'ordem': 3},
        {'codigo': 'TATIL', 'nome': 'Processamento TÁTIL', 'ordem': 4},
        {'codigo': 'VESTIBULAR', 'nome': 'Processamento VESTIBULAR e PROPRIOCEPTIVO', 'ordem': 5}
    ]

    dominios = {}
    for dado in dominios_dados:
        dominio = Dominio(
            codigo=dado['codigo'],
            nome=dado['nome'],
            instrumento_id=instrumento.id,
            ordem=dado['ordem']
        )
        db.session.add(dominio)
        db.session.flush()
        dominios[dado['codigo']] = dominio
        print(f"  ✓ Domínio: {dominio.nome}")

    return dominios


def criar_questoes_perfil_sensorial_infant(dominios):
    """Cria todas as 36 questões do Perfil Sensorial - Bebê"""
    print("\nCriando questões...")

    # Estrutura: (dominio_codigo, numero, codigo_icone, texto_questao)
    questoes_dados = [
        # GERAL (1-10)
        ('GERAL', 1, 'ES', 'tem dificuldade para se acalmar quando chateado(a).'),
        ('GERAL', 2, 'RB', 'dorme profundamente e por longos períodos.'),
        ('GERAL', 3, 'SS', 'acorda facilmente com sons ou movimentos.'),
        ('GERAL', 4, 'BS', 'parece gostar de muito estímulo e atividade.'),
        ('GERAL', 5, 'ES', 'fica irritado(a) facilmente com mudanças de rotina.'),
        ('GERAL', 6, 'RB', 'parece não reagir quando as coisas ao redor mudam.'),
        ('GERAL', 7, 'SS', 'nota pequenas mudanças no ambiente (luz, som, temperatura).'),
        ('GERAL', 8, 'BS', 'acalma-se com movimento constante (balançar, embalar).'),
        ('GERAL', 9, 'ES', 'chora frequentemente sem motivo aparente.'),
        ('GERAL', 10, 'RB', 'tem expressões faciais neutras, mesmo em situações estimulantes.'),

        # AUDITIVO (11-17)
        ('AUDITIVO', 11, 'SS', 'assusta-se ou chora com sons inesperados.'),
        ('AUDITIVO', 12, 'BS', 'vira a cabeça em direção a sons interessantes.'),
        ('AUDITIVO', 13, 'ES', 'chora com sons altos (aspirador, liquidificador).'),
        ('AUDITIVO', 14, 'RB', 'não reage a sons ao redor, mesmo altos.'),
        ('AUDITIVO', 15, 'SS', 'acorda facilmente com ruídos durante o sono.'),
        ('AUDITIVO', 16, 'BS', 'acalma-se ao ouvir música ou voz do cuidador.'),
        ('AUDITIVO', 17, 'ES', 'fica irritado(a) em ambientes barulhentos.'),

        # VISUAL (18-24)
        ('VISUAL', 18, 'SS', 'fecha os olhos ou desvia o olhar de luzes brilhantes.'),
        ('VISUAL', 19, 'BS', 'acompanha objetos em movimento com os olhos.'),
        ('VISUAL', 20, 'ES', 'fica irritado(a) com luzes fortes ou sol direto.'),
        ('VISUAL', 21, 'RB', 'olha vagamente, sem focar em rostos ou objetos.'),
        ('VISUAL', 22, 'SS', 'nota pequenas mudanças visuais no ambiente.'),
        ('VISUAL', 23, 'BS', 'fixa o olhar em rostos familiares e sorri.'),
        ('VISUAL', 24, 'ES', 'evita contato visual prolongado.'),

        # TATIL (25-31)
        ('TATIL', 25, 'SS', 'reage intensamente quando tocado(a) inesperadamente.'),
        ('TATIL', 26, 'BS', 'gosta de ser tocado(a) e massageado(a).'),
        ('TATIL', 27, 'ES', 'chora ou fica irritado(a) durante o banho.'),
        ('TATIL', 28, 'RB', 'parece não sentir quando está molhado(a) ou sujo(a).'),
        ('TATIL', 29, 'SS', 'não gosta de certas texturas de roupa.'),
        ('TATIL', 30, 'BS', 'explora objetos levando-os à boca.'),
        ('TATIL', 31, 'ES', 'fica desconfortável com mudanças de temperatura.'),

        # VESTIBULAR (32-36)
        ('VESTIBULAR', 32, 'SS', 'fica desconfortável ou chora ao ser movimentado(a).'),
        ('VESTIBULAR', 33, 'BS', 'gosta de ser balançado(a) vigorosamente.'),
        ('VESTIBULAR', 34, 'ES', 'não gosta de mudanças de posição (deitar/sentar).'),
        ('VESTIBULAR', 35, 'RB', 'parece não reagir a movimentos ou mudanças de posição.'),
        ('VESTIBULAR', 36, 'BS', 'acalma-se quando embalado(a) ou em movimento.')
    ]

    questoes_criadas = 0
    numero_global = 0

    for dominio_codigo, numero, icone, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        numero_global += 1
        questao = Questao(
            codigo=f'PSI_{numero:03d}',  # PSI_001, PSI_002, etc.
            texto=f'Meu bebê... {texto}',
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
                'icone': icone,  # BS, ES, SS, RB
                'secao': dominio_codigo
            }
        )

        db.session.add(questao)
        questoes_criadas += 1

        if questoes_criadas % 10 == 0:
            print(f"  ✓ {questoes_criadas} questões criadas...")

    db.session.flush()
    print(f"✓ Total de {questoes_criadas} questões criadas!")

    return questoes_criadas


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - Perfil Sensorial - Bebê (0-6 meses)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_perfil_sensorial_infant()

            # Criar instrumento
            instrumento = criar_instrumento_perfil_sensorial_infant(modulo)

            # Criar domínios
            dominios = criar_dominios_perfil_sensorial_infant(instrumento)

            # Criar questões
            total_questoes = criar_questoes_perfil_sensorial_infant(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: Perfil Sensorial - Bebê")
            print(f"Instrumento: 1 (0-6 meses)")
            print(f"Domínios: 5 seções sensoriais")
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
