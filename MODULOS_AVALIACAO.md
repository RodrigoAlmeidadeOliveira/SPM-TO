# MÓDULOS DE AVALIAÇÃO - SPM-TO

Documentação dos módulos de avaliação implementados no sistema SPM-TO.

---

## 📋 MÓDULO PEDI
**Pediatric Evaluation of Disability Inventory**

### Descrição
Avaliação pediátrica de incapacidade funcional para crianças de 1 a 7 anos, medindo habilidades funcionais e o nível de assistência do cuidador.

### Informações Gerais
- **Código:** `PEDI`
- **Categoria:** Funcional
- **Faixa Etária:** 1 a 7 anos
- **Contexto:** Casa
- **Intervalo de Reavaliação:** 90 dias

### Domínios Avaliados

#### 1. Autocuidado (`AUTO`)
**16 itens** avaliando:
- Alimentação (comer, beber, usar utensílios)
- Higiene pessoal (lavar mãos/rosto, escovar dentes)
- Vestuário (vestir/tirar roupas, calçados)
- Controle de esfíncteres

**Exemplos de itens:**
- Come alimentos sólidos
- Usa utensílios para comer
- Escova os dentes
- Veste/tira roupas
- Usa o banheiro de forma independente

#### 2. Mobilidade (`MOB`)
**15 itens** avaliando:
- Posturas e transferências
- Locomoção
- Subir/descer escadas
- Habilidades motoras básicas

**Exemplos de itens:**
- Senta-se/fica em pé sem apoio
- Anda 15 metros
- Sobe/desce escadas
- Pula com os dois pés
- Move-se dentro e fora de casa

#### 3. Função Social (`SOC`)
**15 itens** avaliando:
- Compreensão
- Expressão
- Interação social
- Resolução de problemas
- Jogos e brincadeiras

**Exemplos de itens:**
- Compreende palavras e sentenças
- Expressa necessidades
- Participa de brincadeiras
- Segue regras de jogos
- Toma decisões simples

### Escala de Pontuação

| Valor | Pontos | Significado |
|-------|--------|-------------|
| NUNCA | 0 | Incapaz de realizar |
| OCASIONAL | 1 | Com ajuda máxima |
| FREQUENTE | 2 | Com ajuda moderada |
| SEMPRE | 3 | Independente |

### Classificação Funcional

| Porcentagem | Classificação | Interpretação |
|-------------|---------------|---------------|
| 80-100% | FUNCIONAL | Bom desempenho funcional, maioria das atividades independentes |
| 60-79% | MODERADAMENTE_FUNCIONAL | Desempenho moderado, assistência ocasional |
| 40-59% | DEPENDENCIA_MODERADA | Necessita suporte frequente |
| 20-39% | DEPENDENCIA_SEVERA | Requer assistência substancial |
| 0-19% | DEPENDENCIA_TOTAL | Necessita assistência máxima |

### Aplicação Clínica
- Identificar áreas de maior dependência
- Estabelecer metas terapêuticas realistas
- Monitorar progresso funcional ao longo do tempo
- Planejar intervenções específicas por domínio
- Comunicar com equipe multidisciplinar e família

---

## 🧠 MÓDULO COGNITIVA
**Avaliação Cognitiva**

### Descrição
Avaliação abrangente de funções cognitivas para crianças e adolescentes de 5 a 18 anos.

### Informações Gerais
- **Código:** `COG`
- **Categoria:** Cognitivo
- **Faixa Etária:** 5 a 18 anos
- **Contexto:** Escola
- **Intervalo de Reavaliação:** 60 dias

### Domínios Avaliados

#### 1. Atenção e Concentração (`ATENC`)
**10 itens** avaliando:
- Atenção sustentada
- Atenção seletiva
- Atenção alternada
- Resistência a distrações

**Exemplos de itens:**
- Mantém atenção em atividades por 10+ minutos
- Foca em tarefas mesmo com distrações
- Alterna atenção entre diferentes tarefas
- Ignora estímulos irrelevantes
- Retoma tarefa após interrupção

#### 2. Memória (`MEM`)
**10 itens** avaliando:
- Memória de curto prazo
- Memória de longo prazo
- Memória de trabalho
- Recordação de eventos e informações

**Exemplos de itens:**
- Lembra eventos recentes (horas, dias, semanas)
- Recorda informações após interferência
- Lembra nomes de pessoas
- Segue rotinas sem lembretes
- Aprende informações novas facilmente

#### 3. Funções Executivas (`EXEC`)
**10 itens** avaliando:
- Planejamento
- Organização
- Flexibilidade cognitiva
- Controle inibitório
- Tomada de decisões

**Exemplos de itens:**
- Planeja atividades com antecedência
- Organiza materiais e pertences
- Adapta-se a mudanças de planos
- Resolve problemas de forma criativa
- Controla impulsos apropriadamente

#### 4. Orientação (`ORIENT`)
**8 itens** avaliando:
- Orientação temporal
- Orientação espacial
- Orientação pessoal

**Exemplos de itens:**
- Sabe dia da semana e mês
- Conhece idade e data de nascimento
- Orienta-se em lugares familiares
- Reconhece esquerda e direita

#### 5. Linguagem (`LING`)
**10 itens** avaliando:
- Compreensão verbal
- Expressão verbal
- Comunicação funcional
- Habilidades de leitura e escrita (quando aplicável)

**Exemplos de itens:**
- Compreende instruções complexas
- Expressa ideias claramente
- Usa vocabulário adequado
- Participa de conversas
- Narra eventos em sequência lógica

### Escala de Pontuação

| Valor | Pontos | Significado |
|-------|--------|-------------|
| NUNCA | 0 | Nunca consegue |
| OCASIONAL | 1 | Raramente consegue |
| FREQUENTE | 2 | Frequentemente consegue |
| SEMPRE | 3 | Sempre consegue |

### Classificação Cognitiva

| Porcentagem | Classificação | Perfil |
|-------------|---------------|--------|
| 90-100% | SUPERIOR | Desempenho cognitivo acima da média |
| 75-89% | ADEQUADO | Desempenho cognitivo dentro da média esperada |
| 50-74% | ABAIXO_DA_MEDIA | Dificuldades leves a moderadas |
| 25-49% | SIGNIFICATIVAMENTE_ABAIXO | Dificuldades significativas |
| 0-24% | DEFICITARIO | Comprometimento severo |

### Aplicação Clínica
- Triagem de dificuldades cognitivas
- Identificar perfil de forças e fraquezas
- Planejamento de intervenções educacionais
- Acompanhamento de tratamentos
- Orientação para professores e família

---

## 🏠 MÓDULO AVD
**Atividades de Vida Diária**

### Descrição
Avaliação funcional de independência em atividades cotidianas para adultos.

### Informações Gerais
- **Código:** `AVD`
- **Categoria:** Funcional
- **Faixa Etária:** 18 anos ou mais
- **Contexto:** Casa
- **Intervalo de Reavaliação:** 30 dias

### Domínios Avaliados

#### 1. Alimentação (`ALIM`)
**8 itens** avaliando:
- Capacidade de se alimentar
- Uso de utensílios
- Preparo de refeições

**Exemplos de itens:**
- Leva alimento à boca
- Usa talheres adequadamente
- Corta alimentos com faca
- Prepara refeições simples e quentes

#### 2. Higiene (`HIG`)
**10 itens** avaliando:
- Cuidados pessoais
- Banho
- Higiene oral
- Uso do banheiro

**Exemplos de itens:**
- Lava mãos e rosto
- Escova os dentes
- Toma banho
- Usa o vaso sanitário
- Mantém aparência adequada

#### 3. Vestuário (`VEST`)
**10 itens** avaliando:
- Vestir-se e despir-se
- Manipulação de fechos
- Escolha de roupas

**Exemplos de itens:**
- Veste/tira camisas e calças
- Calça sapatos e meias
- Abotoa, usa zíperes e amarra cadarços
- Escolhe roupas apropriadas

#### 4. Transferências (`TRANSF`)
**10 itens** avaliando:
- Mobilidade funcional
- Transferências posturais
- Locomoção

**Exemplos de itens:**
- Senta e levanta de cadeira
- Transfere-se para cama e banheiro
- Caminha em superfícies variadas
- Sobe e desce escadas
- Alcança objetos

#### 5. Independência Funcional (`INDEP`)
**10 itens** avaliando:
- Atividades instrumentais de vida diária
- Gestão doméstica
- Gerenciamento de compromissos

**Exemplos de itens:**
- Usa telefone/celular
- Faz compras
- Gerencia dinheiro
- Usa transporte
- Toma medicações corretamente
- Organiza a casa e lava roupas

### Escala de Pontuação

| Valor | Pontos | Significado |
|-------|--------|-------------|
| NUNCA | 0 | Dependente total |
| OCASIONAL | 1 | Necessita assistência |
| FREQUENTE | 2 | Independente com adaptações |
| SEMPRE | 3 | Totalmente independente |

### Classificação de Independência

| Média por Item | Nível | Descrição | Cor |
|----------------|-------|-----------|-----|
| 2.5 - 3.0 | INDEPENDENTE | Realiza atividades de forma independente | Verde |
| 1.5 - 2.4 | INDEPENDENCIA_MODIFICADA | Independente com adaptações ou dispositivos | Azul |
| 0.5 - 1.4 | DEPENDENCIA_PARCIAL | Requer assistência em algumas atividades | Amarelo |
| 0.0 - 0.4 | DEPENDENCIA_TOTAL | Requer assistência em quase todas atividades | Vermelho |

### Aplicação Clínica
- Determinar necessidade de assistência
- Planejar alta hospitalar
- Indicar dispositivos de tecnologia assistiva
- Estabelecer metas de reabilitação
- Avaliar eficácia de intervenções
- Orientar cuidadores e familiares

---

## 🔧 INTEGRAÇÃO COM O SISTEMA

### Estrutura de Dados

Todos os módulos compartilham a mesma estrutura:

```
Modulo
  └── Instrumento
       └── Domínio
            └── Questão
                 └── Resposta
```

### Cálculo de Escores

O service `ModulosService` (`app/services/modulos_service.py`) fornece:

- `calcular_escores_pedi(avaliacao_id)` - Escores do PEDI
- `calcular_escores_cognitiva(avaliacao_id)` - Escores Cognitivos
- `calcular_escores_avd(avaliacao_id)` - Escores de AVD
- `gerar_relatorio_pedi(avaliacao_id)` - Relatório interpretativo PEDI

### Uso no Sistema

```python
from app.services.modulos_service import ModulosService

# Calcular escores
escores_pedi = ModulosService.calcular_escores_pedi(avaliacao_id)
escores_cog = ModulosService.calcular_escores_cognitiva(avaliacao_id)
escores_avd = ModulosService.calcular_escores_avd(avaliacao_id)

# Gerar relatório
relatorio = ModulosService.gerar_relatorio_pedi(avaliacao_id)
```

### Seed dos Dados

Para popular o banco de dados com os módulos:

```bash
cd /caminho/para/SPM-TO
PYTHONPATH=. python scripts/seed_novos_modulos.py
```

O script cria:
- 3 Módulos (PEDI, COG, AVD)
- 3 Instrumentos (um por módulo)
- 13 Domínios (total)
- 143 Questões (total)

---

## 📊 RESUMO ESTATÍSTICO

| Módulo | Domínios | Questões | Faixa Etária | Tempo Estimado |
|--------|----------|----------|--------------|----------------|
| PEDI | 3 | 46 | 1-7 anos | 20-30 min |
| Cognitiva | 5 | 48 | 5-18 anos | 25-35 min |
| AVD | 5 | 48 | 18+ anos | 15-25 min |
| **TOTAL** | **13** | **142** | - | - |

---

## 🎯 PRÓXIMAS EXPANSÕES

Módulos adicionais planejados:
- **COPM** - Canadian Occupational Performance Measure
- **ABC Scale** - Activities-specific Balance Confidence
- **FIM** - Functional Independence Measure
- **WeeFIM** - Functional Independence Measure for Children
- **GMFM** - Gross Motor Function Measure

---

**Última Atualização:** 2025-11-07
**Versão:** 1.0
**Autor:** Claude AI / SPM-TO Development Team
