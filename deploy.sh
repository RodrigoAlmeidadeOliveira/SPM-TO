#!/bin/bash
# Script de Deploy Automatizado para Fly.io - SPM-TO
# Uso: ./deploy.sh

set -e  # Parar em caso de erro

echo "======================================"
echo "  SPM-TO - Deploy Fly.io Automatizado"
echo "======================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para mensagens
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se fly CLI está instalado
if ! command -v fly &> /dev/null; then
    error "Fly CLI não encontrado!"
    echo ""
    echo "Por favor, instale o Fly CLI:"
    echo "  macOS/Linux: curl -L https://fly.io/install.sh | sh"
    echo "  Windows: pwsh -Command \"iwr https://fly.io/install.ps1 -useb | iex\""
    echo ""
    exit 1
fi

info "Fly CLI encontrado: $(fly version)"

# Verificar se está logado
if ! fly auth whoami &> /dev/null; then
    warn "Você não está logado no Fly.io"
    info "Fazendo login..."
    fly auth login
fi

info "Usuário logado: $(fly auth whoami)"

# Solicitar nome da aplicação
echo ""
read -p "Nome da aplicação (padrão: spm-to): " APP_NAME
APP_NAME=${APP_NAME:-spm-to}

info "Nome da aplicação: $APP_NAME"

# Verificar se app já existe
if fly apps list | grep -q "$APP_NAME"; then
    warn "Aplicação $APP_NAME já existe!"
    read -p "Deseja fazer apenas um redeploy? (s/N): " REDEPLOY

    if [[ "$REDEPLOY" =~ ^[Ss]$ ]]; then
        info "Fazendo redeploy..."
        fly deploy -a "$APP_NAME"
        info "Deploy concluído!"
        info "Acesse: https://${APP_NAME}.fly.dev"
        exit 0
    else
        error "Deploy cancelado. Use outro nome de aplicação."
        exit 1
    fi
fi

# Criar aplicação
info "Criando aplicação $APP_NAME..."
fly apps create "$APP_NAME" --org personal

# Atualizar fly.toml com o nome correto
if [ -f fly.toml ]; then
    sed -i.bak "s/^app = .*/app = \"$APP_NAME\"/" fly.toml
    info "fly.toml atualizado com o nome da aplicação"
fi

# Perguntar sobre banco de dados
echo ""
read -p "Criar novo banco PostgreSQL? (S/n): " CREATE_DB
CREATE_DB=${CREATE_DB:-S}

if [[ "$CREATE_DB" =~ ^[Ss]$ ]]; then
    DB_NAME="${APP_NAME}-db"
    info "Criando banco de dados $DB_NAME..."

    fly postgres create \
        --name "$DB_NAME" \
        --region gru \
        --vm-size shared-cpu-1x \
        --volume-size 1 \
        --org personal

    info "Anexando banco de dados à aplicação..."
    fly postgres attach "$DB_NAME" -a "$APP_NAME"
else
    warn "Certifique-se de configurar DATABASE_URL manualmente!"
fi

# Configurar SECRET_KEY
info "Gerando SECRET_KEY..."
if command -v openssl &> /dev/null; then
    SECRET_KEY=$(openssl rand -hex 32)
    fly secrets set SECRET_KEY="$SECRET_KEY" -a "$APP_NAME"
    info "SECRET_KEY configurada"
else
    warn "OpenSSL não encontrado. Configure SECRET_KEY manualmente:"
    echo "  fly secrets set SECRET_KEY=\$(openssl rand -hex 32) -a $APP_NAME"
fi

# Deploy
echo ""
info "Iniciando deploy..."
fly deploy -a "$APP_NAME"

# Inicializar banco de dados
echo ""
read -p "Inicializar banco de dados agora? (S/n): " INIT_DB
INIT_DB=${INIT_DB:-S}

if [[ "$INIT_DB" =~ ^[Ss]$ ]]; then
    info "Criando tabelas..."
    fly ssh console -a "$APP_NAME" -C "python run.py initdb"

    info "Criando usuário admin..."
    fly ssh console -a "$APP_NAME" -C "python run.py createadmin"

    info "Importando dados SPM..."
    fly ssh console -a "$APP_NAME" -C "python run.py seed"

    echo ""
    info "✅ Banco de dados inicializado!"
    info "📝 Credenciais padrão:"
    echo "   Usuário: admin"
    echo "   Senha: admin123"
    warn "⚠️  ALTERE ESTA SENHA APÓS O PRIMEIRO LOGIN!"
fi

# Finalização
echo ""
echo "======================================"
info "✅ Deploy concluído com sucesso!"
echo "======================================"
echo ""
info "URL da aplicação: https://${APP_NAME}.fly.dev"
echo ""
echo "Comandos úteis:"
echo "  Ver logs:        fly logs -a $APP_NAME"
echo "  Ver status:      fly status -a $APP_NAME"
echo "  Abrir app:       fly open -a $APP_NAME"
echo "  Console SSH:     fly ssh console -a $APP_NAME"
echo "  Dashboard:       fly dashboard -a $APP_NAME"
echo ""

# Perguntar se quer abrir no navegador
read -p "Abrir aplicação no navegador? (S/n): " OPEN_APP
OPEN_APP=${OPEN_APP:-S}

if [[ "$OPEN_APP" =~ ^[Ss]$ ]]; then
    fly open -a "$APP_NAME"
fi

info "Deploy finalizado! 🚀"
