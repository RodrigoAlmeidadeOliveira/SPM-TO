# ARQUITETURA DA PLATAFORMA - TO360

## 📋 VISÃO GERAL

Transformar SPM-TO em **TO360** - Plataforma completa de avaliação e atendimento em Terapia Ocupacional e áreas correlatas.

---

## 🎯 CONCEITOS PRINCIPAIS

### 1. **MÓDULOS DE AVALIAÇÃO**
Cada teste/avaliação é um módulo independente:

```
📦 Módulo SPM (Sensory Processing Measure)
├── Instrumentos (SPM 5-12, SPM-P)
├── Domínios (SOC, VIS, HEA, TOU, BOD, BAL, PLA, OLF)
├── Questões
├── Cálculo de escores
├── Classificação (T-scores)
└── PEI

📦 Módulo COPM (Canadian Occupational Performance Measure)
├── Áreas (Autocuidado, Produtividade, Lazer)
├── Identificação de problemas
├── Escala de desempenho (1-10)
├── Escala de satisfação (1-10)
└── Cálculo de mudança clínica

📦 Módulo PEDI (Pediatric Evaluation of Disability Inventory)
├── Domínios (Autocuidado, Mobilidade, Função Social)
├── Habilidades funcionais
├── Modificações ambientais
├── Assistência do cuidador
└── Escores normativos

📦 Módulo Avaliação Cognitiva
├── Atenção
├── Memória
├── Funções executivas
├── Orientação
└── Linguagem

📦 Módulo AVD (Atividades de Vida Diária)
├── Alimentação
├── Higiene
├── Vestuário
├── Transferências
└── Independência funcional
```

---

## 🏥 PRONTUÁRIO ELETRÔNICO (CENTRO DA PLATAFORMA)

O prontuário é o **hub central** que conecta todos os módulos:

```
┌─────────────────────────────────────────┐
│          PRONTUÁRIO ELETRÔNICO          │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   DADOS DO PACIENTE             │   │
│  │   - Anamnese                    │   │
│  │   - Histórico médico            │   │
│  │   - Diagnósticos                │   │
│  │   - Medicações                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   ATENDIMENTOS/SESSÕES          │   │
│  │   - Data e hora                 │   │
│  │   - Tipo de atendimento         │   │
│  │   - Evolução (SOAP)             │   │
│  │   - Objetivos trabalhados       │   │
│  │   - Próximos passos             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   AVALIAÇÕES (Multi-módulo)     │   │
│  │   - SPM                         │   │
│  │   - COPM                        │   │
│  │   - PEDI                        │   │
│  │   - Cognitiva                   │   │
│  │   - AVD                         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   PLANO TERAPÊUTICO             │   │
│  │   - Objetivos curto prazo       │   │
│  │   - Objetivos longo prazo       │   │
│  │   - Estratégias                 │   │
│  │   - Frequência                  │   │
│  │   - PEI (se aplicável)          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   ANEXOS                        │   │
│  │   - Fotos                       │   │
│  │   - Vídeos                      │   │
│  │   - Laudos externos             │   │
│  │   - Documentos                  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 📊 RELATÓRIOS E ANALYTICS

### 1. **Por Especialista**
```
Dashboard do Terapeuta:
├── Meus pacientes (lista)
├── Atendimentos desta semana
├── Avaliações pendentes
├── Evolução dos pacientes
├── Horas trabalhadas
└── Métricas de desempenho
```

### 2. **Visão Consolidada (Admin/Coordenador)**
```
Dashboard Geral:
├── Total de pacientes ativos
├── Avaliações realizadas (por módulo)
├── Taxa de alta
├── Tempo médio de tratamento
├── Domínios mais afetados
├── Ranking de terapeutas
├── Comparação entre módulos
└── Indicadores de qualidade
```

### 3. **Relatórios Customizados**
```
Geração de relatórios:
├── Relatório individual do paciente
├── Relatório consolidado (multi-módulo)
├── Relatório de evolução temporal
├── Relatório comparativo (grupos)
├── Relatório para escola/médico
└── Relatório estatístico institucional
```

---

## 🤖 INTEGRAÇÃO COM LLM

### 1. **Geração Automática de Relatórios**
```python
# Exemplo:
prompt = f"""
Baseado nos seguintes dados:
- Paciente: {paciente.nome}, {idade} anos
- Avaliação SPM: {resultados_spm}
- Avaliação COPM: {resultados_copm}
- Últimos 5 atendimentos: {evolucoes}

Gere um relatório profissional de evolução em português.
"""

relatorio_gerado = llm.gerar_relatorio(prompt)
```

### 2. **Sugestões de Intervenção**
```python
# Análise com IA:
sugestoes = llm.analisar_caso({
    'paciente': dados_paciente,
    'avaliacoes': todas_avaliacoes,
    'evolucoes': historico_atendimentos
})

# Retorna:
# - Objetivos terapêuticos sugeridos
# - Estratégias de intervenção
# - Recursos recomendados
# - Literatura relevante
```

### 3. **Chatbot Clínico**
```
Terapeuta: "Paciente com déficit em planejamento motor. O que fazer?"

IA: "Baseado nos dados da plataforma e literatura, sugiro:
1. Atividades de sequenciamento (ex: receitas, montagem)
2. Jogos de estratégia progressivos
3. Exercícios de imitação motora
4. Quebra-cabeças visuoespaciais
Ver protocolo detalhado no módulo de intervenções."
```

### 4. **Predição de Evolução**
```python
# Machine Learning:
predicao = ml_model.predict_evolution({
    'baseline': avaliacao_inicial,
    'sessions': numero_sessoes,
    'frequency': frequencia_semanal,
    'severity': gravidade_inicial
})

# Retorna: tempo estimado para alta, probabilidade de melhora
```

---

## 🗄️ MODELOS DE DADOS

### **Model: Modulo**
```python
class Modulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)  # 'SPM', 'COPM', 'PEDI'
    nome = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))  # 'sensorial', 'ocupacional', 'motor', 'cognitivo'
    ativo = db.Column(db.Boolean, default=True)
    icone = db.Column(db.String(50))  # Bootstrap icon
    cor = db.Column(db.String(7))  # HEX color

    # Configurações
    permite_reavaliacao = db.Column(db.Boolean, default=True)
    intervalo_reavaliacao_dias = db.Column(db.Integer)

    # Relacionamentos
    instrumentos = db.relationship('Instrumento', backref='modulo')
```

### **Model: Prontuario**
```python
class Prontuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))

    # Anamnese
    queixa_principal = db.Column(db.Text)
    historia_doenca = db.Column(db.Text)
    historia_familiar = db.Column(db.Text)
    historia_gestacional = db.Column(db.Text)
    desenvolvimento = db.Column(db.Text)

    # Dados clínicos
    diagnosticos = db.Column(db.Text)  # JSON array
    medicacoes = db.Column(db.Text)  # JSON array
    alergias = db.Column(db.Text)
    comorbidades = db.Column(db.Text)

    # Dados sociais
    composicao_familiar = db.Column(db.Text)
    escolaridade = db.Column(db.String(100))
    ocupacao = db.Column(db.String(100))

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### **Model: Atendimento**
```python
class Atendimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    prontuario_id = db.Column(db.Integer, db.ForeignKey('prontuarios.id'))

    data_hora = db.Column(db.DateTime, nullable=False)
    duracao_minutos = db.Column(db.Integer)
    tipo = db.Column(db.String(50))  # 'avaliacao', 'terapia', 'reavaliacao', 'orientacao'
    modalidade = db.Column(db.String(50))  # 'presencial', 'teleatendimento'

    # SOAP
    subjetivo = db.Column(db.Text)  # S: relato do paciente/cuidador
    objetivo = db.Column(db.Text)   # O: observações do terapeuta
    avaliacao = db.Column(db.Text)  # A: análise clínica
    plano = db.Column(db.Text)      # P: plano de ação

    # Objetivos trabalhados
    objetivos_ids = db.Column(db.Text)  # JSON array

    # Vínculo com avaliações
    avaliacoes_realizadas = db.Column(db.Text)  # JSON: [{modulo: 'SPM', avaliacao_id: 123}]

    compareceu = db.Column(db.Boolean, default=True)
    motivo_falta = db.Column(db.String(200))

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
```

### **Model: PlanoTerapeutico**
```python
class PlanoTerapeutico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    prontuario_id = db.Column(db.Integer, db.ForeignKey('prontuarios.id'))
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    data_inicio = db.Column(db.Date)
    data_revisao = db.Column(db.Date)
    status = db.Column(db.String(20))  # 'ativo', 'concluido', 'suspenso'

    # Objetivos
    objetivos_curto_prazo = db.Column(db.Text)  # JSON array
    objetivos_longo_prazo = db.Column(db.Text)  # JSON array

    # Frequência
    sessoes_semana = db.Column(db.Integer)
    duracao_sessao = db.Column(db.Integer)
    previsao_alta = db.Column(db.Date)

    observacoes = db.Column(db.Text)
```

### **Model: ObjetivoTerapeutico**
```python
class ObjetivoTerapeutico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plano_id = db.Column(db.Integer, db.ForeignKey('planos_terapeuticos.id'))

    descricao = db.Column(db.Text, nullable=False)
    prazo = db.Column(db.String(20))  # 'curto', 'longo'
    prioridade = db.Column(db.String(20))  # 'alta', 'media', 'baixa'

    # Mensuração
    criterio_sucesso = db.Column(db.Text)
    progresso_percentual = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20))  # 'nao_iniciado', 'em_progresso', 'concluido', 'cancelado'

    data_inicio = db.Column(db.Date)
    data_conclusao = db.Column(db.Date)

    # Vinculação com domínios/áreas
    modulo_codigo = db.Column(db.String(50))
    dominio = db.Column(db.String(100))
```

---

## 🔄 FLUXO DE TRABALHO

### **Fluxo Típico:**

```
1. CADASTRO DO PACIENTE
   ↓
2. CRIAÇÃO DO PRONTUÁRIO
   - Anamnese
   - Dados clínicos
   - História
   ↓
3. AVALIAÇÃO INICIAL (Multi-módulo)
   - SPM (se processamento sensorial)
   - COPM (desempenho ocupacional)
   - PEDI (independência funcional)
   - Outras conforme necessário
   ↓
4. ANÁLISE DOS RESULTADOS
   - Escores calculados automaticamente
   - Classificações geradas
   - IA sugere intervenções
   ↓
5. ELABORAÇÃO DO PLANO TERAPÊUTICO
   - Objetivos baseados nas avaliações
   - Frequência e duração
   - Estratégias de intervenção
   - PEI (se aplicável)
   ↓
6. ATENDIMENTOS/SESSÕES
   - Registro em formato SOAP
   - Progresso dos objetivos
   - Anexos (fotos, vídeos)
   ↓
7. REAVALIAÇÕES PERIÓDICAS
   - Mesmos módulos da avaliação inicial
   - Comparação de evolução
   - Ajuste do plano terapêutico
   ↓
8. RELATÓRIOS
   - Evolução clínica
   - Para escola/médico
   - Para família
   - Com análise de IA
   ↓
9. ALTA (quando objetivos atingidos)
   - Relatório final
   - Orientações de manutenção
```

---

## 🚀 PLANO DE IMPLEMENTAÇÃO

### **FASE 1: Fundação (1-2 semanas)**
- [ ] Model Modulo (sistema genérico de módulos)
- [ ] Refatorar SPM para ser um módulo
- [ ] Model Prontuario
- [ ] Model Atendimento
- [ ] Model PlanoTerapeutico
- [ ] Model ObjetivoTerapeutico
- [ ] Migrações de banco

### **FASE 2: Prontuário Eletrônico (1-2 semanas)**
- [ ] CRUD Prontuário
- [ ] CRUD Atendimentos (SOAP)
- [ ] CRUD Plano Terapêutico
- [ ] Timeline de evolução
- [ ] Vinculação com avaliações existentes
- [ ] Dashboard do prontuário

### **FASE 3: Novos Módulos (2-3 semanas)**
- [ ] Módulo COPM (primeiro novo módulo)
- [ ] Módulo Avaliação Cognitiva
- [ ] Módulo AVD
- [ ] Interface de seleção de módulos

### **FASE 4: Relatórios Avançados (1 semana)**
- [ ] Dashboard por terapeuta
- [ ] Dashboard consolidado
- [ ] Relatórios multi-módulo
- [ ] Comparação temporal
- [ ] Exportação avançada

### **FASE 5: Integração LLM (1-2 semanas)**
- [ ] Serviço de integração OpenAI/Anthropic
- [ ] Geração de relatórios com IA
- [ ] Sugestões de intervenção
- [ ] Chatbot clínico
- [ ] Análise preditiva

---

## 💰 MODELO DE NEGÓCIO ATUALIZADO

### **Planos para Plataforma Completa:**

```
🆓 FREE (Trial 30 dias)
├── 5 pacientes
├── 1 usuário
├── Módulo SPM
└── Relatórios básicos

💼 BÁSICO (R$ 99/mês)
├── 30 pacientes
├── 2 usuários
├── Todos os módulos
├── Prontuário completo
├── Relatórios avançados
└── 50 relatórios IA/mês

🏥 PROFISSIONAL (R$ 249/mês)
├── 100 pacientes
├── 5 usuários
├── Todos os módulos
├── Prontuário + templates
├── Relatórios + whitelabel
├── 200 relatórios IA/mês
└── API access

🏢 CLÍNICA (R$ 599/mês)
├── Pacientes ilimitados
├── 15 usuários
├── Todos os módulos
├── Multi-clínica
├── Relatórios customizados
├── 1000 relatórios IA/mês
├── API completa
└── Suporte prioritário
```

---

## 🎯 DIFERENCIAIS DA PLATAFORMA

1. ✅ **Multi-módulo**: Diversos testes integrados
2. ✅ **Prontuário unificado**: Centro da prática clínica
3. ✅ **Inteligência artificial**: Sugestões e análises
4. ✅ **Interdisciplinar**: TO, fisio, fono, psico
5. ✅ **Baseado em evidências**: Testes validados
6. ✅ **Evolução temporal**: Comparação fácil
7. ✅ **Colaborativo**: Múltiplos profissionais
8. ✅ **Compliant**: LGPD, CFM, COFFITO

---

## 📝 NOMENCLATURA

**Sugestão de novo nome:**
- **TO360** - Plataforma 360° de Terapia Ocupacional
- **TheraPro** - Plataforma Profissional de Terapia
- **CliniFlex** - Clínica Flexível e Inteligente
- **EvalCare** - Avaliação e Cuidado Integrados

**Manter SPM-TO?**
- SPM vira um módulo da plataforma maior
- Branding pode ser mantido para marketing (pioneiros em SPM digital)

---

**Autor:** Claude AI
**Data:** 2025-11-07
**Versão:** 1.0
