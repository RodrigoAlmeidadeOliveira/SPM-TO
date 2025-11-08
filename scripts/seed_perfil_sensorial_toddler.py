"""
Script de seed para o Módulo Perfil Sensorial - Criança Pequena (7-35 meses)

Este script popula o banco de dados com:
- 1 módulo (Perfil Sensorial - Criança Pequena)
- 1 instrumento (Criança Pequena 7-35 meses)
- 7 domínios/seções sensoriais
- 54 questões distribuídas pelas seções

Uso:
    PYTHONPATH=. python scripts/seed_perfil_sensorial_toddler.py
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Modulo, Instrumento, Dominio, Questao


def criar_modulo_perfil_sensorial_toddler():
    """Cria o módulo Perfil Sensorial - Criança Pequena"""
    print("Criando módulo Perfil Sensorial - Criança Pequena...")

    # Verificar se já existe
    modulo_existente = Modulo.query.filter_by(codigo='PERFIL_SENS_TODDLER').first()
    if modulo_existente:
        print("Módulo Perfil Sensorial - Criança Pequena já existe. Pulando...")
        return modulo_existente

    modulo = Modulo(
        codigo='PERFIL_SENS_TODDLER',
        nome='Perfil Sensorial - Criança Pequena',
        categoria='sensorial',
        icone='child',
        cor='#f39c12',  # Laranja
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=180  # Reavaliar a cada 6 meses
    )

    db.session.add(modulo)
    db.session.flush()

    print(f"✓ Módulo criado: {modulo.nome}")
    return modulo


def criar_instrumento_perfil_sensorial_toddler(modulo):
    """Cria o instrumento para Perfil Sensorial - Criança Pequena"""
    print("\nCriando instrumento...")

    instrumento = Instrumento(
        codigo='PERFIL_SENS_TODDLER_7_35',
        nome='Perfil Sensorial - Criança Pequena (7-35 meses)',
        modulo_id=modulo.id,
        idade_minima=0,  # 7 meses
        idade_maxima=2,  # 35 meses = 2 anos 11 meses
        contexto='casa',
        descricao='Questionário do cuidador para avaliação de processamento sensorial em crianças de 7 a 35 meses'
    )

    db.session.add(instrumento)
    db.session.flush()

    print(f"✓ Instrumento criado: {instrumento.nome}")
    return instrumento


def criar_dominios_perfil_sensorial_toddler(instrumento):
    """Cria os 7 domínios/seções do Perfil Sensorial - Criança Pequena"""
    print("\nCriando domínios (seções sensoriais)...")

    dominios_dados = [
        {'codigo': 'GERAL', 'nome': 'Processamento GERAL', 'ordem': 1},
        {'codigo': 'AUDITIVO', 'nome': 'Processamento AUDITIVO', 'ordem': 2},
        {'codigo': 'VISUAL', 'nome': 'Processamento VISUAL', 'ordem': 3},
        {'codigo': 'TATO', 'nome': 'Processamento do TATO', 'ordem': 4},
        {'codigo': 'MOVIMENTOS', 'nome': 'Processamento de MOVIMENTOS', 'ordem': 5},
        {'codigo': 'POSICAO_CORPO', 'nome': 'Processamento da POSIÇÃO DO CORPO', 'ordem': 6},
        {'codigo': 'ORAL', 'nome': 'Processamento ORAL/Sensibilidade', 'ordem': 7}
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


def criar_questoes_perfil_sensorial_toddler(dominios):
    """Cria todas as 54 questões do Perfil Sensorial - Criança Pequena"""
    print("\nCriando questões...")

    # Estrutura: (dominio_codigo, numero, codigo_icone, texto_questao)
    questoes_dados = [
        # GERAL (1-9)
        ('GERAL', 1, 'ES', 'tem dificuldade para se acalmar depois de uma atividade estimulante.'),
        ('GERAL', 2, 'RB', 'não reage a mudanças na rotina diária.'),
        ('GERAL', 3, 'SS', 'fica incomodado(a) com pequenas mudanças no ambiente.'),
        ('GERAL', 4, 'BS', 'procura constantemente por coisas para fazer ou tocar.'),
        ('GERAL', 5, 'ES', 'tem dificuldade para adormecer ou manter o sono.'),
        ('GERAL', 6, 'RB', 'dorme profundamente e por longos períodos sem acordar.'),
        ('GERAL', 7, 'SS', 'acorda facilmente com pequenos sons ou movimentos.'),
        ('GERAL', 8, 'BS', 'está sempre em movimento, não para quieto(a).'),
        ('GERAL', 9, 'ES', 'fica irritado(a) ou chora em lugares novos.'),

        # AUDITIVO (10-17)
        ('AUDITIVO', 10, 'ES', 'cobre os ouvidos ou chora com sons altos.'),
        ('AUDITIVO', 11, 'SS', 'para o que está fazendo quando ouve sons ao redor.'),
        ('AUDITIVO', 12, 'BS', 'procura sons interessantes e se aproxima deles.'),
        ('AUDITIVO', 13, 'RB', 'não responde quando o chamam pelo nome.'),
        ('AUDITIVO', 14, 'ES', 'fica irritado(a) em ambientes barulhentos (shopping, festas).'),
        ('AUDITIVO', 15, 'SS', 'distrai-se facilmente com sons de fundo.'),
        ('AUDITIVO', 16, 'BS', 'gosta de fazer barulhos ou ouvir sons altos.'),
        ('AUDITIVO', 17, 'RB', 'parece não ouvir instruções simples.'),

        # VISUAL (18-25)
        ('VISUAL', 18, 'ES', 'fecha os olhos ou se afasta de luzes brilhantes.'),
        ('VISUAL', 19, 'SS', 'prefere brincar em ambientes com pouca luz.'),
        ('VISUAL', 20, 'BS', 'observa tudo ao redor com atenção.'),
        ('VISUAL', 21, 'RB', 'não nota quando pessoas entram na sala.'),
        ('VISUAL', 22, 'ES', 'fica irritado(a) com luz solar direta.'),
        ('VISUAL', 23, 'SS', 'nota pequenos detalhes visuais que outros não veem.'),
        ('VISUAL', 24, 'BS', 'gosta de brinquedos com luzes piscantes ou cores vivas.'),
        ('VISUAL', 25, 'RB', 'tem dificuldade para encontrar brinquedos à vista.'),

        # TATO (26-34)
        ('TATO', 26, 'ES', 'não gosta de ser tocado(a) ou abraçado(a).'),
        ('TATO', 27, 'SS', 'reclama de roupas que estão "apertadas" ou "ásperas".'),
        ('TATO', 28, 'BS', 'toca tudo e todos ao redor.'),
        ('TATO', 29, 'RB', 'não percebe quando está com as mãos ou rosto sujos.'),
        ('TATO', 30, 'ES', 'resiste a tomar banho, cortar unhas ou cabelo.'),
        ('TATO', 31, 'SS', 'fica incomodado(a) ao andar descalço(a) em certas superfícies.'),
        ('TATO', 32, 'BS', 'procura tocar diferentes texturas (areia, água, massinha).'),
        ('TATO', 33, 'RB', 'parece não sentir dor quando se machuca.'),
        ('TATO', 34, 'ES', 'fica irritado(a) quando outras crianças ficam muito próximas.'),

        # MOVIMENTOS (35-42)
        ('MOVIMENTOS', 35, 'ES', 'fica com medo em brinquedos de parquinho (balanço, escorregador).'),
        ('MOVIMENTOS', 36, 'SS', 'fica ansioso(a) quando os pés saem do chão.'),
        ('MOVIMENTOS', 37, 'BS', 'busca atividades de movimento constantemente (pular, girar).'),
        ('MOVIMENTOS', 38, 'RB', 'esbarra em móveis e pessoas frequentemente.'),
        ('MOVIMENTOS', 39, 'ES', 'resiste a ser movimentado(a) ou girado(a).'),
        ('MOVIMENTOS', 40, 'SS', 'prefere atividades calmas a atividades de movimento.'),
        ('MOVIMENTOS', 41, 'BS', 'gosta de ser balançado(a) vigorosamente.'),
        ('MOVIMENTOS', 42, 'RB', 'move-se de forma descoordenada ou desajeitada.'),

        # POSICAO_CORPO (43-49)
        ('POSICAO_CORPO', 43, 'RB', 'parece ter músculos fracos ou "moles".'),
        ('POSICAO_CORPO', 44, 'SS', 'cansa-se facilmente durante atividades físicas.'),
        ('POSICAO_CORPO', 45, 'BS', 'apoia-se ou empurra objetos e pessoas.'),
        ('POSICAO_CORPO', 46, 'RB', 'move-se de forma rígida ou tensa.'),
        ('POSICAO_CORPO', 47, 'ES', 'resiste a atividades que exigem força ou esforço.'),
        ('POSICAO_CORPO', 48, 'BS', 'gosta de atividades que envolvem empurrar ou puxar.'),
        ('POSICAO_CORPO', 49, 'RB', 'tropeça ou cai com frequência sem motivo aparente.'),

        # ORAL (50-54)
        ('ORAL', 50, 'ES', 'recusa muitos alimentos ou tem paladar muito seletivo.'),
        ('ORAL', 51, 'SS', 'fica com ânsia ou vomita facilmente com certas texturas de comida.'),
        ('ORAL', 52, 'BS', 'coloca objetos na boca constantemente.'),
        ('ORAL', 53, 'RB', 'não percebe quando tem comida ao redor da boca.'),
        ('ORAL', 54, 'BS', 'procura ativamente por sabores fortes (doce, salgado, azedo).')
    ]

    questoes_criadas = 0
    numero_global = 0

    for dominio_codigo, numero, icone, texto in questoes_dados:
        dominio = dominios[dominio_codigo]

        numero_global += 1
        questao = Questao(
            codigo=f'PST_{numero:03d}',  # PST_001, PST_002, etc.
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
    print("SEED - Perfil Sensorial - Criança Pequena (7-35 meses)")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        try:
            # Criar módulo
            modulo = criar_modulo_perfil_sensorial_toddler()

            # Criar instrumento
            instrumento = criar_instrumento_perfil_sensorial_toddler(modulo)

            # Criar domínios
            dominios = criar_dominios_perfil_sensorial_toddler(instrumento)

            # Criar questões
            total_questoes = criar_questoes_perfil_sensorial_toddler(dominios)

            # Commit
            db.session.commit()

            print("\n" + "=" * 80)
            print("✓ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"Módulo: Perfil Sensorial - Criança Pequena")
            print(f"Instrumento: 1 (7-35 meses)")
            print(f"Domínios: 7 seções sensoriais")
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
