# MANIFEST - SPM-TO

Documentação completa da estrutura e componentes do projeto SPM-TO.

## Data de Criação
2024-11-06

## Visão Geral

Sistema web completo para gestão e análise de avaliações SPM (Sensory Processing Measure), desenvolvido em Flask com PostgreSQL, seguindo as melhores práticas de design patterns e arquitetura de software.

## Arquitetura

### Design Patterns Implementados

1. **Application Factory Pattern** (`app/__init__.py`)
   - Permite criação de múltiplas instâncias da aplicação
   - Facilita testes e diferentes configurações

2. **Blueprint Pattern** (`app/routes/`)
   - Modularização de rotas
   - Organização por funcionalidade

3. **Service Layer Pattern** (`app/services/`)
   - Separação da lógica de negócio
   - Reutilização de código

4. **MVC Architecture**
   - Models: `app/models/`
   - Views: `app/templates/`
   - Controllers: `app/routes/`

## Estrutura de Arquivos

### Raiz do Projeto
```
SPM-TO/
├── run.py                    # Ponto de entrada da aplicação
├── requirements.txt          # Dependências Python
├── Dockerfile               # Container Docker
├── fly.toml                 # Configuração Fly.io
├── Procfile                 # Comandos para deploy
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── README.md               # Documentação principal
└── MANIFEST.md             # Este arquivo
```

### Aplicação (`app/`)

#### Configuração
- `__init__.py`: Application Factory, registro de blueprints
- `config.py`: Configurações por ambiente (dev, prod, test)

#### Modelos de Dados (`app/models/`)
- `user.py`: Usuários do sistema (admin, terapeuta, professor, familiar)
- `paciente.py`: Dados das crianças avaliadas
- `instrumento.py`: Instrumentos SPM, Domínios, Questões, Tabelas de Referência
- `avaliacao.py`: Avaliações e Respostas

#### Serviços (`app/services/`)
- `calculo_service.py`: Cálculo de escores brutos por domínio
- `classificacao_service.py`: Classificação baseada em T-scores

#### Rotas/Blueprints (`app/routes/`)
- `main.py`: Página inicial e dashboard
- `auth.py`: Autenticação (login/logout)
- `pacientes.py`: CRUD de pacientes
- `avaliacoes.py`: CRUD de avaliações
- `instrumentos.py`: Gerenciamento de instrumentos
- `relatorios.py`: Geração de relatórios
- `admin.py`: Área administrativa

#### Templates (`app/templates/`)
```
templates/
├── base.html                # Template base
├── index.html              # Página inicial
├── dashboard.html          # Dashboard principal
├── auth/
│   └── login.html          # Login
├── pacientes/              # Templates de pacientes
├── avaliacoes/             # Templates de avaliações
├── instrumentos/           # Templates de instrumentos
├── relatorios/             # Templates de relatórios
└── admin/                  # Templates administrativos
```

#### Arquivos Estáticos (`app/static/`)
```
static/
├── css/
│   └── style.css           # Estilos customizados
├── js/                     # JavaScript
└── images/                 # Imagens
```

### Scripts (`scripts/`)
- `seed_database.py`: Popula banco com dados das planilhas Excel

### Documentos (`DOCTOS/`)
Contém as planilhas originais SPM:
- Planilha PEI SPM 5-12 - casa.xlsx
- Planilha PEI SPM 5-12 - escola.xlsx
- Planilha PEI SPM-P 3-5 - casa.xlsx
- Planilha PEI SPM-P 3-5 - escola.xlsx
- Gráficos e PDFs de referência

## Modelos de Dados

### User
- Autenticação e autorização
- Tipos: admin, terapeuta, professor, familiar
- Senhas criptografadas com Werkzeug

### Paciente
- Informações da criança
- Cálculo automático de idade
- Seleção automática de instrumento adequado

### Instrumento
- SPM 5-12 anos (Casa e Escola)
- SPM-P 3-5 anos (Casa e Escola)
- Instruções e faixa etária

### Dominio
- 7-8 domínios por instrumento
- Escala normal ou invertida
- Códigos: SOC, VIS, HEA, TOU, BOD, BAL, PLA, OLF

### Questao
- Itens de avaliação
- Número sequencial e global
- Vínculo com domínio

### TabelaReferencia
- T-scores e percentis
- Classificações (Típico, Provável Disfunção, Disfunção Definitiva)
- Faixas de escores

### Avaliacao
- Dados gerais (data, relacionamento do respondente)
- Escores calculados por domínio
- T-scores e classificações
- Status: em_andamento, concluida, revisao

### Resposta
- Respostas individuais às questões
- Valores: NUNCA, OCASIONAL, FREQUENTE, SEMPRE
- Pontuação calculada (1-4)

## Serviços

### CalculoService
Responsável pelo cálculo de escores:
- Converte respostas em pontuações
- Considera escalas normais e invertidas
- Calcula escores por domínio
- Calcula escore total

### ClassificacaoService
Responsável pela classificação:
- Busca na tabela de referência
- Obtém T-scores
- Determina percentis
- Classifica resultados

## Rotas Principais

### Públicas
- `GET /` - Página inicial

### Autenticação
- `GET/POST /auth/login` - Login
- `GET /auth/logout` - Logout

### Dashboard
- `GET /dashboard` - Dashboard principal

### Pacientes
- `GET /pacientes` - Listar pacientes
- `GET/POST /pacientes/novo` - Criar paciente
- `GET /pacientes/<id>` - Visualizar paciente

### Avaliações
- `GET /avaliacoes` - Listar avaliações
- `GET/POST /avaliacoes/nova` - Criar avaliação
- `GET /avaliacoes/<id>` - Visualizar avaliação
- `GET/POST /avaliacoes/<id>/responder` - Responder avaliação

### Instrumentos
- `GET /instrumentos` - Listar instrumentos
- `GET /instrumentos/<id>` - Visualizar instrumento
- `GET/POST /instrumentos/<id>/questoes` - Gerenciar questões

### Relatórios
- `GET /relatorios/avaliacao/<id>` - Relatório de avaliação
- `GET /relatorios/evolucao/<paciente_id>` - Gráfico de evolução
- `GET /relatorios/pei/<avaliacao_id>` - Relatório PEI

### Admin
- `GET /admin` - Dashboard administrativo
- `GET /admin/usuarios` - Gerenciar usuários
- `GET /admin/configuracoes` - Configurações

## Comandos CLI

```bash
# Inicializar banco de dados
python run.py initdb

# Criar usuário admin
python run.py createadmin

# Popular banco com dados
python run.py seed

# Shell interativo
flask shell
```

## Tecnologias Utilizadas

### Backend
- **Flask 3.0.0**: Framework web
- **SQLAlchemy**: ORM
- **Flask-Migrate**: Migrações de banco
- **Flask-Login**: Autenticação
- **Flask-WTF**: Formulários com proteção CSRF

### Frontend
- **Bootstrap 5.3**: Framework CSS
- **Font Awesome 6.4**: Ícones
- **jQuery 3.7**: Manipulação DOM
- **Plotly**: Gráficos interativos

### Banco de Dados
- **PostgreSQL 13+**: Banco relacional

### Análise de Dados
- **Pandas**: Manipulação de dados
- **Matplotlib**: Gráficos estáticos
- **OpenPyXL**: Leitura de planilhas Excel

### Relatórios
- **ReportLab**: Geração de PDFs

### Deploy
- **Gunicorn**: Servidor WSGI
- **Fly.io**: Plataforma de hospedagem
- **Docker**: Containerização

## Segurança

### Implementações
1. Senhas criptografadas (Werkzeug)
2. Proteção CSRF (Flask-WTF)
3. Sessões seguras (HTTP-only cookies)
4. Validação de entrada
5. Controle de acesso por tipo de usuário
6. Auditoria de ações

### Boas Práticas
- Secrets em variáveis de ambiente
- Conexão HTTPS no produção
- Sanitização de inputs
- Rate limiting (a implementar)

## Deploy

### Fly.io
1. Dockerfile otimizado
2. fly.toml configurado
3. PostgreSQL como serviço
4. Variáveis de ambiente via secrets
5. Health checks configurados

### Processo
1. Build da imagem Docker
2. Push para Fly.io
3. Provisionamento de PostgreSQL
4. Execução de migrações
5. Seed do banco de dados

## Próximos Passos

### Funcionalidades Pendentes
1. Implementar formulários completos de cadastro
2. Desenvolver sistema de gráficos de evolução
3. Criar gerador de relatórios PDF
4. Implementar módulo PEI completo
5. Adicionar área administrativa funcional
6. Implementar exportação de dados
7. Adicionar testes unitários
8. Implementar testes de integração

### Melhorias
1. Cache de consultas frequentes
2. Paginação de listagens
3. Busca e filtros avançados
4. Notificações por email
5. API REST para integração
6. Logs estruturados
7. Monitoramento de performance
8. Backup automático

## Manutenção

### Atualizações de Segurança
```bash
pip list --outdated
pip install --upgrade <pacote>
```

### Backup do Banco
```bash
pg_dump spm_db > backup.sql
```

### Logs
- Aplicação: stdout/stderr
- Fly.io: `fly logs`
- Banco: PostgreSQL logs

## Contato

Para questões técnicas ou suporte:
- Email: admin@spmto.com
- Repository: https://github.com/seu-usuario/SPM-TO

---

**Última Atualização**: 2024-11-06
**Versão**: 1.0.0
