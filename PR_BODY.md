# Implementar Módulos Perfil Sensorial para Diferentes Faixas Etárias

## 📋 Resumo

Este PR implementa dois novos módulos do Perfil Sensorial de Winnie Dunn para complementar o módulo existente (Criança 3-14 anos), fornecendo cobertura completa de avaliação sensorial do nascimento aos 14 anos.

## ✨ Novos Módulos

### 1. Perfil Sensorial - Bebê (0-6 meses)
- ✅ 36 questões distribuídas em 5 seções sensoriais
- ✅ 4 quadrantes de processamento sensorial
- ✅ Tabelas de classificação por percentis
- ✅ Documentação clínica completa com estratégias de intervenção
- ✅ Script de seed para popular banco de dados

### 2. Perfil Sensorial - Criança Pequena (7-35 meses)
- ✅ 54 questões distribuídas em 7 seções sensoriais
- ✅ 4 quadrantes com pontuação apropriada para idade
- ✅ Exemplos comportamentais específicos para idade
- ✅ Guias clínicos detalhados e estratégias de cuidado
- ✅ Script de seed para popular banco de dados

## 🎯 Cobertura Completa por Idade

| Faixa Etária | Módulo | Questões | Seções |
|--------------|--------|----------|---------|
| **0-6 meses** | Perfil Sensorial - Bebê | 36 | 5 |
| **7-35 meses** | Perfil Sensorial - Criança Pequena | 54 | 7 |
| **3-14 anos** | Perfil Sensorial 2 - Criança | 86 | 9 |

## 📦 Arquivos Adicionados

### Documentação
- `PERFIL_SENSORIAL_INFANT.md` - Documentação completa do módulo Bebê
- `PERFIL_SENSORIAL_TODDLER.md` - Documentação completa do módulo Criança Pequena

### Scripts de Seed
- `scripts/seed_perfil_sensorial_infant.py` - Popular banco com módulo Bebê
- `scripts/seed_perfil_sensorial_toddler.py` - Popular banco com módulo Criança Pequena

### Código
- `app/services/modulos_service.py` - Adicionados métodos de cálculo e classificação

## 🔧 Funcionalidades Implementadas

### Cálculo de Escores
- ✅ `calcular_perfil_sensorial_infant()` - Cálculo para módulo Bebê
- ✅ `calcular_perfil_sensorial_toddler()` - Cálculo para módulo Criança Pequena
- ✅ Classificação por seções sensoriais
- ✅ Classificação por quadrantes (Busca, Esquiva, Sensibilidade, Registro Baixo)

### Tabelas de Classificação
- ✅ Tabelas de percentis para cada seção sensorial
- ✅ Tabelas de percentis para cada quadrante
- ✅ Interpretações clínicas automáticas
- ✅ Métodos helper reutilizáveis

## 📊 Detalhes Técnicos

### Seções Sensoriais - Bebê (0-6 meses)
1. Processamento Geral (10 questões)
2. Processamento Auditivo (7 questões)
3. Processamento Visual (7 questões)
4. Processamento Tátil (7 questões)
5. Processamento Vestibular e Proprioceptivo (5 questões)

### Seções Sensoriais - Criança Pequena (7-35 meses)
1. Processamento Geral (9 questões)
2. Processamento Auditivo (8 questões)
3. Processamento Visual (8 questões)
4. Processamento do Tato (9 questões)
5. Processamento de Movimentos (8 questões)
6. Processamento da Posição do Corpo (7 questões)
7. Processamento Oral/Sensibilidade (5 questões)

### Quadrantes (Modelo de Dunn)
Para ambos os módulos:
- **Busca Sensorial (BS)** - Limiar ALTO + Autorregulação ATIVA
- **Esquiva Sensorial (ES)** - Limiar BAIXO + Autorregulação ATIVA
- **Sensibilidade Sensorial (SS)** - Limiar BAIXO + Autorregulação PASSIVA
- **Registro Baixo (RB)** - Limiar ALTO + Autorregulação PASSIVA

## 🚀 Como Usar

### Popular o Banco de Dados
```bash
# Módulo Bebê
PYTHONPATH=. python scripts/seed_perfil_sensorial_infant.py

# Módulo Criança Pequena
PYTHONPATH=. python scripts/seed_perfil_sensorial_toddler.py
```

### Calcular Escores
```python
from app.services.modulos_service import ModulosService

# Para bebês (0-6 meses)
resultado_infant = ModulosService.calcular_perfil_sensorial_infant(avaliacao_id)

# Para crianças pequenas (7-35 meses)
resultado_toddler = ModulosService.calcular_perfil_sensorial_toddler(avaliacao_id)
```

## 📚 Base Científica

Todos os módulos são baseados no trabalho de **Winnie Dunn, PhD, OTR, FAOTA** e seguem o modelo teórico de Processamento Sensorial validado internacionalmente.

## ✅ Checklist

- [x] Documentação completa em português
- [x] Scripts de seed funcionais
- [x] Métodos de cálculo implementados
- [x] Tabelas de classificação por percentis
- [x] Interpretações clínicas
- [x] Sintaxe Python validada
- [x] Código commitado e enviado
- [x] Integração com sistema existente

## 📈 Estatísticas

- **Total de linhas adicionadas:** 1.740
- **Arquivos criados:** 4
- **Arquivos modificados:** 1
- **Questões totais:** 90 (36 Bebê + 54 Criança Pequena)
- **Seções totais:** 12 (5 Bebê + 7 Criança Pequena)

## 🎯 Impacto

Este PR expande significativamente a capacidade do sistema SPM-TO de avaliar processamento sensorial, permitindo:

1. **Intervenção Precoce** - Identificação de padrões sensoriais desde o nascimento
2. **Acompanhamento Longitudinal** - Seguimento do desenvolvimento sensorial de 0 a 14 anos
3. **Orientação aos Pais** - Estratégias específicas para cada faixa etária
4. **Decisões Clínicas** - Dados objetivos para planejamento terapêutico

---

**Desenvolvido para o Sistema SPM-TO**
