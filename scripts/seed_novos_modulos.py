"""
Seed para novos módulos de avaliação: PEDI, Cognitiva e AVD
"""
from app import db, create_app
from app.models import Modulo, Instrumento, Dominio, Questao, TabelaReferencia

def criar_modulo_pedi():
    """Cria módulo PEDI - Pediatric Evaluation of Disability Inventory"""

    # Criar módulo
    modulo_pedi = Modulo(
        codigo='PEDI',
        nome='PEDI - Pediatric Evaluation of Disability Inventory',
        descricao='Avaliação pediátrica de incapacidade funcional',
        categoria='funcional',
        icone='person-wheelchair',
        cor='#0dcaf0',
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=90
    )
    db.session.add(modulo_pedi)
    db.session.flush()

    # Criar instrumento PEDI
    instrumento_pedi = Instrumento(
        codigo='PEDI_1_7',
        nome='PEDI - 1 a 7 anos',
        modulo_id=modulo_pedi.id,
        idade_minima=1,
        idade_maxima=7,
        contexto='casa',
        instrucoes='Avaliação de habilidades funcionais e assistência do cuidador em atividades do dia a dia.',
        ativo=True
    )
    db.session.add(instrumento_pedi)
    db.session.flush()

    # Domínios do PEDI
    dominios_pedi = [
        {
            'codigo': 'AUTO',
            'nome': 'Autocuidado',
            'ordem': 1,
            'descricao': 'Habilidades de autocuidado (alimentação, higiene, vestuário)'
        },
        {
            'codigo': 'MOB',
            'nome': 'Mobilidade',
            'ordem': 2,
            'descricao': 'Habilidades de mobilidade (transferências, locomoção)'
        },
        {
            'codigo': 'SOC',
            'nome': 'Função Social',
            'ordem': 3,
            'descricao': 'Habilidades sociais e comunicação funcional'
        }
    ]

    for dom_data in dominios_pedi:
        dominio = Dominio(
            instrumento_id=instrumento_pedi.id,
            codigo=dom_data['codigo'],
            nome=dom_data['nome'],
            ordem=dom_data['ordem'],
            escala_invertida=False
        )
        db.session.add(dominio)
        db.session.flush()

        # Questões de Autocuidado
        if dom_data['codigo'] == 'AUTO':
            questoes = [
                "Come alimentos sólidos",
                "Usa utensílios para comer",
                "Bebe em copo ou xícara",
                "Abre recipientes",
                "Escova os dentes",
                "Lava as mãos",
                "Lava o rosto",
                "Veste camisa",
                "Tira camisa",
                "Veste calça",
                "Tira calça",
                "Veste sapatos",
                "Tira sapatos",
                "Usa o banheiro de forma independente",
                "Controla a bexiga durante o dia",
                "Controla a bexiga durante a noite"
            ]
        # Questões de Mobilidade
        elif dom_data['codigo'] == 'MOB':
            questoes = [
                "Senta-se sem apoio",
                "Fica em pé sem apoio",
                "Anda 15 metros sem ajuda",
                "Anda 15 metros com equipamento adaptativo",
                "Sobe escadas (com corrimão)",
                "Desce escadas (com corrimão)",
                "Pula com os dois pés",
                "Corre 4,5 metros",
                "Transfere-se de cadeira para cama",
                "Transfere-se para o chão e retorna",
                "Entra e sai do carro",
                "Move-se pela casa",
                "Move-se fora de casa (50 metros)",
                "Sobe meio-fio",
                "Desce meio-fio"
            ]
        # Questões de Função Social
        else:
            questoes = [
                "Compreende significado de palavras",
                "Compreende sentenças",
                "Expressa necessidades usando palavras ou gestos",
                "Fala em sentenças",
                "Participa de brincadeiras com outras crianças",
                "Brinca jogos de cooperação",
                "Segue regras de jogos",
                "Interage com adultos conhecidos",
                "Brinca de faz de conta",
                "Ajuda em tarefas simples",
                "Completa tarefas designadas",
                "Toma decisões simples",
                "Resolve problemas do dia a dia",
                "Mantém atenção em atividades",
                "Organiza suas próprias coisas"
            ]

        for i, texto in enumerate(questoes, start=1):
            questao = Questao(
                dominio_id=dominio.id,
                numero=i,
                numero_global=i + (dom_data['ordem'] - 1) * 16,
                texto=texto,
                ativo=True
            )
            db.session.add(questao)

    print(f"✓ Módulo PEDI criado com {len(dominios_pedi)} domínios")
    return modulo_pedi, instrumento_pedi


def criar_modulo_cognitiva():
    """Cria módulo de Avaliação Cognitiva"""

    # Criar módulo
    modulo_cog = Modulo(
        codigo='COG',
        nome='Avaliação Cognitiva',
        descricao='Avaliação de funções cognitivas (atenção, memória, funções executivas)',
        categoria='cognitivo',
        icone='brain',
        cor='#ffc107',
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=60
    )
    db.session.add(modulo_cog)
    db.session.flush()

    # Criar instrumento Cognitivo
    instrumento_cog = Instrumento(
        codigo='COG_5_18',
        nome='Avaliação Cognitiva - 5 a 18 anos',
        modulo_id=modulo_cog.id,
        idade_minima=5,
        idade_maxima=18,
        contexto='escola',
        instrucoes='Avaliação das funções cognitivas: atenção, memória, funções executivas, orientação e linguagem.',
        ativo=True
    )
    db.session.add(instrumento_cog)
    db.session.flush()

    # Domínios Cognitivos
    dominios_cog = [
        {
            'codigo': 'ATENC',
            'nome': 'Atenção e Concentração',
            'ordem': 1,
            'descricao': 'Capacidade de focar e manter a atenção'
        },
        {
            'codigo': 'MEM',
            'nome': 'Memória',
            'ordem': 2,
            'descricao': 'Memória de curto e longo prazo'
        },
        {
            'codigo': 'EXEC',
            'nome': 'Funções Executivas',
            'ordem': 3,
            'descricao': 'Planejamento, organização, flexibilidade mental'
        },
        {
            'codigo': 'ORIENT',
            'nome': 'Orientação',
            'ordem': 4,
            'descricao': 'Orientação temporal, espacial e pessoal'
        },
        {
            'codigo': 'LING',
            'nome': 'Linguagem',
            'ordem': 5,
            'descricao': 'Compreensão e expressão verbal'
        }
    ]

    for dom_data in dominios_cog:
        dominio = Dominio(
            instrumento_id=instrumento_cog.id,
            codigo=dom_data['codigo'],
            nome=dom_data['nome'],
            ordem=dom_data['ordem'],
            escala_invertida=False
        )
        db.session.add(dominio)
        db.session.flush()

        # Questões de Atenção
        if dom_data['codigo'] == 'ATENC':
            questoes = [
                "Mantém atenção em atividades por 10+ minutos",
                "Foca em tarefas mesmo com distrações",
                "Alterna atenção entre diferentes tarefas",
                "Segue instruções com múltiplos passos",
                "Completa tarefas sem se distrair",
                "Ignora estímulos irrelevantes",
                "Mantém foco em conversas longas",
                "Resiste a distrações visuais",
                "Resiste a distrações auditivas",
                "Retoma tarefa após interrupção"
            ]
        # Questões de Memória
        elif dom_data['codigo'] == 'MEM':
            questoes = [
                "Lembra eventos recentes (últimas horas)",
                "Lembra eventos de dias atrás",
                "Lembra eventos de semanas atrás",
                "Recorda informações após interferência",
                "Lembra nomes de pessoas conhecidas",
                "Lembra onde guardou objetos",
                "Segue rotinas diárias sem lembretes",
                "Lembra compromissos agendados",
                "Reconta histórias com detalhes",
                "Aprende informações novas facilmente"
            ]
        # Questões de Funções Executivas
        elif dom_data['codigo'] == 'EXEC':
            questoes = [
                "Planeja atividades com antecedência",
                "Organiza materiais e pertences",
                "Gerencia tempo adequadamente",
                "Adapta-se a mudanças de planos",
                "Resolve problemas de forma criativa",
                "Toma decisões adequadas à idade",
                "Controla impulsos apropriadamente",
                "Inicia tarefas sem necessitar comando",
                "Persiste em tarefas desafiadoras",
                "Avalia consequências de ações"
            ]
        # Questões de Orientação
        elif dom_data['codigo'] == 'ORIENT':
            questoes = [
                "Sabe que dia da semana é",
                "Sabe qual mês estamos",
                "Conhece sua idade",
                "Sabe sua data de nascimento",
                "Orienta-se em lugares familiares",
                "Encontra caminhos em lugares novos",
                "Reconhece esquerda e direita",
                "Identifica pontos de referência"
            ]
        # Questões de Linguagem
        else:
            questoes = [
                "Compreende instruções complexas",
                "Segue conversas em grupo",
                "Expressa ideias claramente",
                "Usa vocabulário adequado à idade",
                "Forma sentenças gramaticalmente corretas",
                "Participa de conversas bidirecionais",
                "Narra eventos em sequência lógica",
                "Compreende metáforas e expressões idiomáticas",
                "Lê com compreensão (se alfabetizado)",
                "Escreve textos coerentes (se alfabetizado)"
            ]

        for i, texto in enumerate(questoes, start=1):
            questao = Questao(
                dominio_id=dominio.id,
                numero=i,
                numero_global=i + sum([10, 10, 10, 8, 10][:dom_data['ordem']-1]),
                texto=texto,
                ativo=True
            )
            db.session.add(questao)

    print(f"✓ Módulo Cognitivo criado com {len(dominios_cog)} domínios")
    return modulo_cog, instrumento_cog


def criar_modulo_avd():
    """Cria módulo AVD - Atividades de Vida Diária"""

    # Criar módulo
    modulo_avd = Modulo(
        codigo='AVD',
        nome='AVD - Atividades de Vida Diária',
        descricao='Avaliação de independência em atividades cotidianas',
        categoria='funcional',
        icone='house-check',
        cor='#198754',
        tipo='avaliacao',
        permite_reavaliacao=True,
        intervalo_reavaliacao_dias=30
    )
    db.session.add(modulo_avd)
    db.session.flush()

    # Criar instrumento AVD
    instrumento_avd = Instrumento(
        codigo='AVD_ADULTO',
        nome='AVD - Avaliação Funcional Adultos',
        modulo_id=modulo_avd.id,
        idade_minima=18,
        idade_maxima=100,
        contexto='casa',
        instrucoes='Avaliação do nível de independência em atividades básicas e instrumentais de vida diária. Escala: 0=Dependente Total, 1=Necessita Assistência, 2=Independente com Adaptações, 3=Totalmente Independente.',
        ativo=True
    )
    db.session.add(instrumento_avd)
    db.session.flush()

    # Domínios AVD
    dominios_avd = [
        {
            'codigo': 'ALIM',
            'nome': 'Alimentação',
            'ordem': 1,
            'descricao': 'Habilidades relacionadas à alimentação'
        },
        {
            'codigo': 'HIG',
            'nome': 'Higiene',
            'ordem': 2,
            'descricao': 'Cuidados pessoais e higiene'
        },
        {
            'codigo': 'VEST',
            'nome': 'Vestuário',
            'ordem': 3,
            'descricao': 'Vestir-se e despir-se'
        },
        {
            'codigo': 'TRANSF',
            'nome': 'Transferências',
            'ordem': 4,
            'descricao': 'Mobilidade e transferências'
        },
        {
            'codigo': 'INDEP',
            'nome': 'Independência Funcional',
            'ordem': 5,
            'descricao': 'Atividades instrumentais de vida diária'
        }
    ]

    for dom_data in dominios_avd:
        dominio = Dominio(
            instrumento_id=instrumento_avd.id,
            codigo=dom_data['codigo'],
            nome=dom_data['nome'],
            ordem=dom_data['ordem'],
            escala_invertida=False
        )
        db.session.add(dominio)
        db.session.flush()

        # Questões de Alimentação
        if dom_data['codigo'] == 'ALIM':
            questoes = [
                "Leva alimento à boca",
                "Bebe líquidos em copo",
                "Usa talheres adequadamente",
                "Corta alimentos com faca",
                "Prepara refeições simples (sanduíche, café)",
                "Prepara refeições quentes",
                "Serve-se sozinho",
                "Come em ritmo adequado"
            ]
        # Questões de Higiene
        elif dom_data['codigo'] == 'HIG':
            questoes = [
                "Lava as mãos e o rosto",
                "Escova os dentes",
                "Penteia/escova os cabelos",
                "Faz a barba ou maquiagem",
                "Toma banho de chuveiro",
                "Toma banho de banheira",
                "Usa o vaso sanitário",
                "Controla esfíncteres",
                "Cuida das unhas",
                "Mantém aparência adequada"
            ]
        # Questões de Vestuário
        elif dom_data['codigo'] == 'VEST':
            questoes = [
                "Veste camisa/blusa",
                "Tira camisa/blusa",
                "Veste calças/saias",
                "Tira calças/saias",
                "Calça sapatos/meias",
                "Tira sapatos/meias",
                "Abotoa botões",
                "Usa zíperes",
                "Amarra cadarços",
                "Escolhe roupas apropriadas"
            ]
        # Questões de Transferências
        elif dom_data['codigo'] == 'TRANSF':
            questoes = [
                "Senta e levanta de cadeira",
                "Deita e levanta da cama",
                "Transfere-se para o vaso sanitário",
                "Transfere-se para banheira/chuveiro",
                "Transfere-se para o carro",
                "Caminha em superfícies planas",
                "Caminha em terrenos irregulares",
                "Sobe e desce escadas",
                "Abre e fecha portas",
                "Alcança objetos em prateleiras"
            ]
        # Questões de Independência Funcional
        else:
            questoes = [
                "Usa telefone/celular",
                "Faz compras básicas",
                "Gerencia dinheiro (troco, pagamentos)",
                "Usa transporte público",
                "Toma medicações corretamente",
                "Organiza a casa (limpeza leve)",
                "Lava roupas",
                "Administra finanças pessoais",
                "Cumpre compromissos/horários",
                "Resolve problemas do cotidiano"
            ]

        for i, texto in enumerate(questoes, start=1):
            questao = Questao(
                dominio_id=dominio.id,
                numero=i,
                numero_global=i + sum([8, 10, 10, 10, 10][:dom_data['ordem']-1]),
                texto=texto,
                ativo=True
            )
            db.session.add(questao)

    print(f"✓ Módulo AVD criado com {len(dominios_avd)} domínios")
    return modulo_avd, instrumento_avd


def main():
    """Executa a criação de todos os módulos"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*50)
        print("CRIANDO NOVOS MÓDULOS DE AVALIAÇÃO")
        print("="*50 + "\n")

        try:
            # Verificar se módulos já existem
            if Modulo.query.filter_by(codigo='PEDI').first():
                print("⚠ Módulo PEDI já existe. Pulando...")
            else:
                criar_modulo_pedi()

            if Modulo.query.filter_by(codigo='COG').first():
                print("⚠ Módulo Cognitivo já existe. Pulando...")
            else:
                criar_modulo_cognitiva()

            if Modulo.query.filter_by(codigo='AVD').first():
                print("⚠ Módulo AVD já existe. Pulando...")
            else:
                criar_modulo_avd()

            db.session.commit()

            print("\n" + "="*50)
            print("✓ TODOS OS MÓDULOS CRIADOS COM SUCESSO!")
            print("="*50)

            # Exibir resumo
            print("\nRESUMO:")
            modulos = Modulo.query.all()
            for modulo in modulos:
                print(f"\n{modulo.nome}")
                print(f"  - Código: {modulo.codigo}")
                print(f"  - Categoria: {modulo.categoria}")
                instrumentos = modulo.instrumentos.count()
                print(f"  - Instrumentos: {instrumentos}")

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ ERRO: {e}")
            raise


if __name__ == '__main__':
    main()
