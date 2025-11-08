# NOVOS MÓDULOS DE AVALIAÇÃO - SPM-TO

Documentação dos 5 novos módulos implementados no sistema SPM-TO.

---

## 📋 MÓDULO COPM
**Canadian Occupational Performance Measure**

### Descrição
Medida Canadense de Desempenho Ocupacional - Avaliação centrada no cliente que identifica e prioriza problemas de desempenho ocupacional.

### Informações Gerais
- **Código:** `COPM`
- **Categoria:** Ocupacional
- **Faixa Etária:** Todas as idades
- **Contexto:** Geral
- **Intervalo de Reavaliação:** 90 dias

### Áreas Avaliadas

#### 1. Autocuidado
- Cuidado pessoal
- Mobilidade funcional
- Mobilidade comunitária

#### 2. Produtividade
- Trabalho remunerado/voluntário
- Tarefas domésticas
- Escola/Brincar

#### 3. Lazer
- Recreação tranquila
- Recreação ativa
- Socialização

### Escala de Pontuação

**Desempenho (1-10):**
- 1 = Não consegue fazer
- 5 = Consegue fazer de forma mediana
- 10 = Consegue fazer perfeitamente

**Satisfação (1-10):**
- 1 = Nada satisfeito
- 5 = Neutro
- 10 = Completamente satisfeito

### Mudança Clínica
- **Significativa:** Diferença de 2 ou mais pontos entre avaliação e reavaliação
- **Cálculo:** Média de desempenho e satisfação dos problemas identificados

### Aplicação Clínica
- Estabelecer metas centradas no cliente
- Priorizar intervenções
- Medir mudança clínica ao longo do tempo
- Facilitar comunicação terapeuta-cliente
- Documentar eficácia da intervenção

---

## ⚖️ MÓDULO ABC SCALE
**Activities-specific Balance Confidence Scale**

### Descrição
Escala de Confiança no Equilíbrio Específica por Atividade - Avalia o nível de confiança em manter o equilíbrio durante atividades da vida diária.

### Informações Gerais
- **Código:** `ABC`
- **Categoria:** Motor
- **Faixa Etária:** 18 anos ou mais
- **Contexto:** Geral
- **Intervalo de Reavaliação:** 30 dias
- **Total de Itens:** 16

### Domínio Avaliado

#### Confiança no Equilíbrio (16 itens)
Exemplos de atividades:
- Caminhar pela casa
- Subir ou descer escadas
- Alcançar objetos em prateleiras
- Caminhar em shopping lotado
- Usar escada rolante
- Caminhar em calçadas escorregadias

### Escala de Pontuação

| Valor | Significado |
|-------|-------------|
| 0% | Nenhuma confiança |
| 50% | Moderadamente confiante |
| 100% | Completamente confiante |

### Classificação de Risco de Queda

| Escore | Risco | Interpretação |
|--------|-------|---------------|
| > 80% | BAIXO | Alta confiança no equilíbrio |
| 50-80% | MODERADO | Confiança moderada |
| < 50% | ALTO | Baixa confiança - necessita intervenção |

### Aplicação Clínica
- Avaliar risco de queda em idosos
- Monitorar progresso em reabilitação
- Identificar atividades com baixa confiança
- Planejar intervenções específicas
- Avaliar eficácia de treino de equilíbrio

---

## 🏥 MÓDULO FIM
**Functional Independence Measure**

### Descrição
Medida de Independência Funcional - Avalia o nível de assistência necessária para um indivíduo realizar atividades da vida diária.

### Informações Gerais
- **Código:** `FIM`
- **Categoria:** Funcional
- **Faixa Etária:** 18 anos ou mais
- **Contexto:** Hospital/Reabilitação
- **Intervalo de Reavaliação:** 30 dias
- **Total de Itens:** 18

### Domínios Avaliados

#### 1. Autocuidado (6 itens)
- Alimentação
- Higiene pessoal
- Banho
- Vestuário superior e inferior
- Uso do vaso sanitário

#### 2. Controle de Esfíncteres (2 itens)
- Controle de bexiga
- Controle intestinal

#### 3. Transferências (3 itens)
- Leito/cadeira/cadeira de rodas
- Vaso sanitário
- Banheira/chuveiro

#### 4. Locomoção (2 itens)
- Marcha/cadeira de rodas (50 metros)
- Escadas (12-14 degraus)

#### 5. Comunicação (2 itens)
- Compreensão (auditiva ou visual)
- Expressão (verbal ou não-verbal)

#### 6. Cognição Social (3 itens)
- Interação social
- Resolução de problemas
- Memória

### Escala de Pontuação (1-7)

| Nível | Pontos | Descrição |
|-------|--------|-----------|
| Independência Completa | 7 | Sem ajuda, seguro, tempo normal |
| Independência Modificada | 6 | Com ajuda técnica |
| Supervisão/Preparação | 5 | Necessita supervisão |
| Ajuda Mínima | 4 | Paciente realiza ≥75% |
| Ajuda Moderada | 3 | Paciente realiza 50-74% |
| Ajuda Máxima | 2 | Paciente realiza 25-49% |
| Ajuda Total | 1 | Paciente realiza <25% |

### Pontuação

- **Motor (13 itens):** 13-91 pontos
- **Cognitivo (5 itens):** 5-35 pontos
- **Total FIM:** 18-126 pontos

### Interpretação

| Escore Total | Nível de Independência |
|--------------|------------------------|
| 108-126 | Independência completa/modificada |
| 90-107 | Dependência mínima |
| 54-89 | Dependência moderada |
| 18-53 | Dependência completa |

### Aplicação Clínica
- Avaliar necessidade de assistência
- Planejar alta hospitalar
- Determinar recursos necessários
- Monitorar progresso em reabilitação
- Documentar melhora funcional

---

## 👶 MÓDULO WeeFIM
**Functional Independence Measure for Children**

### Descrição
Medida de Independência Funcional para Crianças - Avalia independência funcional de crianças de 6 meses a 7 anos, considerando o desenvolvimento típico.

### Informações Gerais
- **Código:** `WEEFIM`
- **Categoria:** Funcional
- **Faixa Etária:** 6 meses a 7 anos
- **Contexto:** Casa/Clínica
- **Intervalo de Reavaliação:** 90 dias
- **Total de Itens:** 18

### Domínios Avaliados

#### Estrutura Idêntica ao FIM Adulto:
1. **Autocuidado** (6 itens)
2. **Controle de Esfíncteres** (2 itens)
3. **Transferências** (3 itens)
4. **Locomoção** (2 itens)
5. **Comunicação** (2 itens)
6. **Cognição Social** (3 itens)

### Escala de Pontuação (1-7)

**Mesma escala do FIM adulto, mas considerando desenvolvimento típico:**
- 7 = Independência completa **apropriada para idade**
- 6 = Independência modificada (com ajuda técnica)
- 5 = Supervisão/orientação
- 4 = Ajuda mínima (criança realiza ≥75%)
- 3 = Ajuda moderada (criança realiza 50-74%)
- 2 = Ajuda máxima (criança realiza 25-49%)
- 1 = Ajuda total (criança realiza <25%)

### Pontuação

- **Motor:** 13-91 pontos
- **Cognitivo:** 5-35 pontos
- **Total WeeFIM:** 18-126 pontos

### Diferença do FIM Adulto

**IMPORTANTE:** O WeeFIM considera o desenvolvimento **típico** para cada faixa etária.
- Uma criança de 1 ano não é esperada ter independência completa em muitas atividades
- A pontuação deve refletir capacidade em relação a pares da mesma idade
- Útil para identificar atrasos no desenvolvimento funcional

### Aplicação Clínica
- Avaliar desenvolvimento funcional
- Identificar atrasos em relação a pares
- Planejar intervenção precoce
- Monitorar progresso ao longo do tempo
- Comunicar com equipe e família

---

## 🏃 MÓDULO GMFM
**Gross Motor Function Measure - 88 itens**

### Descrição
Medida da Função Motora Grossa - Avalia habilidades motoras grossas em crianças com paralisia cerebral e outras condições neurológicas.

### Informações Gerais
- **Código:** `GMFM`
- **Categoria:** Motor
- **Faixa Etária:** 0 a 18 anos
- **Contexto:** Clínica/Hospital
- **Intervalo de Reavaliação:** 90 dias
- **Total de Itens:** 88

### Dimensões Avaliadas

#### Dimensão A: Deitar e Rolar (17 itens)
- Controle de cabeça
- Rolamentos
- Alcance em supino e prono
- Pivoteamento

#### Dimensão B: Sentar (20 itens)
- Manutenção de postura sentada
- Alcance em diferentes direções
- Transferências para sentado
- Equilíbrio sentado

#### Dimensão C: Engatinhar e Ajoelhar (14 itens)
- Posição de quatro apoios
- Engatinhar
- Subir/descer degraus engatinhando
- Ajoelhar alto e meio ajoelhar

#### Dimensão D: Ficar em Pé (13 itens)
- Assumir posição em pé
- Manutenção de postura em pé
- Agachar e retornar
- Equilíbrio em pé

#### Dimensão E: Andar, Correr e Pular (24 itens)
- Marcha com e sem apoio
- Correr
- Pular
- Subir/descer escadas
- Chutar bola

### Escala de Pontuação (0-3)

| Pontos | Descrição |
|--------|-----------|
| 0 | NÃO INICIA - Criança não inicia a atividade |
| 1 | INICIA - Criança inicia mas completa < 10% |
| 2 | COMPLETA PARCIALMENTE - Completa 10-99% |
| 3 | COMPLETA - Completa 100% da tarefa |

### Pontuação

- **Por Dimensão:** % = (pontos obtidos / pontos possíveis) × 100
- **GMFM Total:** Média das 5 dimensões (0-100%)

### Classificação

| GMFM Total | Interpretação |
|------------|---------------|
| ≥ 90% | Função motora excelente - próximo ao típico |
| 70-89% | Função motora boa - dificuldades leves |
| 50-69% | Função motora moderada |
| 30-49% | Função motora limitada - dificuldades importantes |
| < 30% | Função motora severamente limitada |

### Aplicação Clínica
- Avaliar função motora em paralisia cerebral
- Monitorar progresso em fisioterapia/TO
- Definir metas terapêuticas
- Avaliar eficácia de intervenções
- Comunicar mudanças à equipe e família
- Pesquisa em reabilitação pediátrica

### Versões

**GMFM-88:** Versão completa com 88 itens (implementada)
**GMFM-66:** Versão com 66 itens selecionados (pode ser implementada futuramente)

---

## 🔧 INTEGRAÇÃO COM O SISTEMA

### Scripts de Seed

Todos os módulos possuem scripts de seed completos:

```bash
# COPM
PYTHONPATH=. python scripts/seed_copm.py

# ABC Scale
PYTHONPATH=. python scripts/seed_abc_scale.py

# FIM
PYTHONPATH=. python scripts/seed_fim.py

# WeeFIM
PYTHONPATH=. python scripts/seed_weefim.py

# GMFM
PYTHONPATH=. python scripts/seed_gmfm.py
```

### Métodos de Cálculo

O service `ModulosService` (`app/services/modulos_service.py`) fornece:

```python
from app.services.modulos_service import ModulosService

# Calcular escores
escores_copm = ModulosService.calcular_escores_copm(avaliacao_id)
escores_abc = ModulosService.calcular_escores_abc(avaliacao_id)
escores_fim = ModulosService.calcular_escores_fim(avaliacao_id)
escores_weefim = ModulosService.calcular_escores_weefim(avaliacao_id)
escores_gmfm = ModulosService.calcular_escores_gmfm(avaliacao_id)
```

### Estrutura de Dados

Todos os módulos compartilham a mesma estrutura do sistema:

```
Modulo
  └── Instrumento
       └── Domínio
            └── Questão
                 └── Resposta
```

---

## 📊 RESUMO ESTATÍSTICO

| Módulo | Instrumentos | Domínios | Itens | Faixa Etária | Tempo Estimado |
|--------|--------------|----------|-------|--------------|----------------|
| COPM | 1 | 3 áreas | 19* | Todas | 30-45 min |
| ABC Scale | 1 | 1 | 16 | 18+ anos | 10-15 min |
| FIM | 1 | 6 | 18 | 18+ anos | 20-30 min |
| WeeFIM | 1 | 6 | 18 | 0-7 anos | 20-30 min |
| GMFM-88 | 1 | 5 dimensões | 88 | 0-18 anos | 45-60 min |
| **TOTAL** | **5** | **21** | **159** | - | - |

\* COPM: 9 questões guiadas + 10 de avaliação (desempenho/satisfação para até 5 problemas)

---

## 🎯 CATEGORIAS DOS NOVOS MÓDULOS

### Por Categoria
- **Ocupacional:** COPM
- **Motor:** ABC Scale, GMFM-88
- **Funcional:** FIM, WeeFIM

### Por Faixa Etária
- **Pediátrico (0-7 anos):** WeeFIM, GMFM
- **Infantil (0-18 anos):** GMFM
- **Adulto (18+ anos):** ABC Scale, FIM
- **Todas as idades:** COPM

### Por Contexto
- **Clínica/Hospital:** FIM, GMFM, WeeFIM
- **Casa:** WeeFIM
- **Geral:** COPM, ABC Scale

---

## 📈 COMPARAÇÃO COM MÓDULOS EXISTENTES

### Total de Módulos no Sistema

| Categoria | Quantidade | Módulos |
|-----------|------------|---------|
| Sensorial | 2 | SPM 5-12, SPM-P 3-5, Perfil Sensorial 2 |
| Ocupacional | 1 | COPM |
| Motor | 2 | ABC Scale, GMFM-88 |
| Cognitivo | 1 | Avaliação Cognitiva |
| Funcional | 4 | PEDI, AVD, FIM, WeeFIM |
| **TOTAL** | **10** | **10 módulos** |

### Estatísticas Gerais

- **Total de Instrumentos:** 14+
- **Total de Domínios:** 60+
- **Total de Questões:** 600+
- **Faixas Etárias Cobertas:** 0 meses a 100+ anos

---

## 🚀 PRÓXIMOS PASSOS

### Em Produção
1. Executar seeds para popular banco de dados
2. Testar todos os módulos com dados reais
3. Validar cálculos de escores
4. Treinar equipe no uso dos novos módulos

### Futuras Expansões
- Criar relatórios específicos para cada módulo
- Adicionar tabelas de referência normativas
- Implementar gráficos de evolução
- Integrar com PEI (quando aplicável)
- Adicionar sugestões de intervenção baseadas nos escores

---

**Última Atualização:** 2025-11-08
**Versão:** 1.0
**Autor:** Claude AI / SPM-TO Development Team
