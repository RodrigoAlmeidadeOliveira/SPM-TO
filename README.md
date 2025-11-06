# SPM-TO - Sistema de Processamento Sensorial

Sistema web para cadastro e análise de testes SPM (Sensory Processing Measure), permitindo o registro de avaliações, acompanhamento da evolução de pacientes e geração de relatórios completos.

## Características Principais

- **Cadastro de Pacientes**: Gerencie informações completas dos pacientes e suas avaliações
- **Instrumentos SPM**: Suporte para SPM 5-12 anos e SPM-P 3-5 anos (contextos casa e escola)
- **Avaliações Completas**: Registro de respostas com escala de frequência
- **Cálculo Automático**: Escores por domínio (Participação Social, Visão, Audição, Tato, etc.)
- **Classificação de Resultados**: T-scores, percentis e categorias (Típico, Provável Disfunção, Disfunção Definitiva)
- **Gráficos de Evolução**: Visualize o progresso do paciente ao longo do tempo
- **Relatórios PDF**: Gere relatórios profissionais com interpretações
- **PEI**: Módulo de Plano Educacional Individualizado
- **Multi-usuário**: Sistema de autenticação com controle de acesso

## Requisitos

- Python 3.11+
- PostgreSQL 13+
- pip

## Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/SPM-TO.git
cd SPM-TO
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Crie um banco PostgreSQL:

```bash
createdb spm_dev
```

Configure as variáveis de ambiente criando um arquivo `.env`:

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:

```
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://usuario:senha@localhost/spm_dev
```

### 5. Inicialize o banco de dados

```bash
# Criar tabelas
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Ou usar o comando customizado
python run.py initdb

# Criar usuário admin
python run.py createadmin

# Popular com dados dos instrumentos
python run.py seed
```

### 6. Execute a aplicação

```bash
python run.py
```

Acesse: http://localhost:5000

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

## Estrutura do Projeto

```
SPM-TO/
├── app/
│   ├── __init__.py           # Application Factory
│   ├── config.py             # Configurações
│   ├── models/               # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── paciente.py
│   │   ├── instrumento.py
│   │   └── avaliacao.py
│   ├── services/             # Lógica de negócio
│   │   ├── calculo_service.py
│   │   └── classificacao_service.py
│   ├── routes/               # Blueprints (rotas)
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── pacientes.py
│   │   ├── avaliacoes.py
│   │   ├── instrumentos.py
│   │   ├── relatorios.py
│   │   └── admin.py
│   ├── templates/            # Templates Jinja2
│   └── static/               # CSS, JS, imagens
├── scripts/
│   └── seed_database.py      # Script de população
├── DOCTOS/                   # Planilhas e documentos SPM
├── migrations/               # Migrações do banco
├── requirements.txt
├── run.py                    # Arquivo principal
├── Dockerfile
└── fly.toml                  # Configuração Fly.io
```

## Design Patterns Utilizados

- **Application Factory Pattern**: Criação flexível da aplicação Flask
- **Blueprint Pattern**: Organização modular de rotas
- **Repository Pattern**: Abstração de acesso a dados
- **Service Layer Pattern**: Separação da lógica de negócio
- **MVC Architecture**: Model-View-Controller

## Domínios SPM

### SPM 5-12 anos
1. **SOC** - Participação Social
2. **VIS** - Visão
3. **HEA** - Audição (Hearing)
4. **TOU** - Tato (Touch)
5. **BOD** - Consciência Corporal (Body Awareness)
6. **BAL** - Equilíbrio e Movimento (Balance)
7. **PLA** - Planejamento e Ideação (Planning)

### SPM-P 3-5 anos
Inclui todos os acima mais:
- **OLF** - Olfato e Paladar

## Escala de Frequência

- **Nunca** (4 pontos na escala normal, 1 na invertida)
- **Ocasional** (3 ou 2 pontos)
- **Frequente** (2 ou 3 pontos)
- **Sempre** (1 ou 4 pontos)

**Nota**: Alguns domínios usam escala invertida (ex: Visão, Audição, Tato)

## Classificações

Baseado em T-scores e percentis:

- **Típico**: Processamento sensorial dentro da normalidade
- **Provável Disfunção**: Sugere possível disfunção, requer monitoramento
- **Disfunção Definitiva**: Indica disfunção clara, requer intervenção

## Deploy no Fly.io

**📖 Para instruções detalhadas, consulte: [DEPLOY.md](DEPLOY.md)**

**🚀 Deploy Rápido (Automatizado):**
```bash
./deploy.sh
```

**📝 Deploy Manual (Passo a Passo):**

### 1. Instale o Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Faça login

```bash
fly auth login
```

### 3. Crie a aplicação

```bash
fly apps create spm-to
```

### 4. Crie o banco PostgreSQL

```bash
fly postgres create --name spm-to-db
fly postgres attach spm-to-db -a spm-to
```

### 5. Configure secrets

```bash
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
```

### 6. Deploy

```bash
fly deploy
```

### 7. Inicialize o banco

```bash
fly ssh console -C "python run.py initdb"
fly ssh console -C "python run.py createadmin"
fly ssh console -C "python run.py seed"
```

## API / Rotas Principais

- `/` - Página inicial
- `/auth/login` - Login
- `/dashboard` - Dashboard principal
- `/pacientes` - Listagem de pacientes
- `/pacientes/novo` - Cadastro de paciente
- `/avaliacoes` - Listagem de avaliações
- `/avaliacoes/nova` - Nova avaliação
- `/avaliacoes/<id>/responder` - Responder avaliação
- `/relatorios/avaliacao/<id>` - Relatório de avaliação
- `/relatorios/evolucao/<paciente_id>` - Gráficos de evolução
- `/instrumentos` - Gerenciar instrumentos
- `/admin` - Área administrativa

## Desenvolvimento

### Executar testes

```bash
pytest
```

### Criar nova migração

```bash
flask db migrate -m "Descrição da alteração"
flask db upgrade
```

### Shell interativo

```bash
flask shell
```

## Segurança

- Senhas criptografadas com Werkzeug
- Proteção CSRF em formulários
- Sessões seguras com cookies HTTP-only
- Validação de entrada de dados
- Controle de acesso por tipo de usuário

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

Este projeto é proprietário. Todos os direitos reservados.

## Suporte

Para questões e suporte, contate: admin@spmto.com

## Autores

Desenvolvido para análise e acompanhamento de avaliações SPM no Tocantins.

---

**Versão**: 1.0.0
**Data**: 2024
