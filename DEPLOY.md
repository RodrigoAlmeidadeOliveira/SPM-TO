# Guia de Deploy no Fly.io - SPM-TO

Este guia fornece instruções passo a passo para fazer o deploy da aplicação SPM-TO no Fly.io.

## Pré-requisitos

- Conta no Fly.io (gratuita): https://fly.io/app/sign-up
- Git instalado
- Código do projeto commitado no branch atual

## Passo 1: Instalar o Fly CLI

### macOS
```bash
curl -L https://fly.io/install.sh | sh
```

### Linux
```bash
curl -L https://fly.io/install.sh | sh
```

### Windows (PowerShell)
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Após a instalação, adicione o Fly ao seu PATH (se necessário):

**macOS/Linux:**
```bash
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

Adicione ao seu `.bashrc` ou `.zshrc` para tornar permanente.

**Windows:**
O instalador já adiciona ao PATH automaticamente.

### Verificar instalação
```bash
fly version
```

## Passo 2: Fazer Login no Fly.io

```bash
fly auth login
```

Isso abrirá uma janela do navegador para você fazer login ou criar uma conta.

## Passo 3: Criar a Aplicação no Fly.io

```bash
fly apps create spm-to
```

**Nota:** Se o nome "spm-to" já estiver em uso, escolha outro nome (ex: `spm-to-seu-nome`).

## Passo 4: Provisionar Banco de Dados PostgreSQL

### Criar banco de dados
```bash
fly postgres create --name spm-to-db --region gru --vm-size shared-cpu-1x --volume-size 1
```

**Parâmetros:**
- `--region gru`: São Paulo, Brasil (mesmo região da app)
- `--vm-size shared-cpu-1x`: Tier gratuito/baixo custo
- `--volume-size 1`: 1GB de armazenamento

### Anexar o banco à aplicação
```bash
fly postgres attach spm-to-db -a spm-to
```

Isso criará automaticamente a variável de ambiente `DATABASE_URL` na sua aplicação.

### Verificar conexão
```bash
fly postgres connect -a spm-to-db
```

Digite `\q` para sair do console PostgreSQL.

## Passo 5: Configurar Secrets/Environment Variables

### Gerar e definir SECRET_KEY
```bash
fly secrets set SECRET_KEY=$(openssl rand -hex 32) -a spm-to
```

### Verificar secrets configurados
```bash
fly secrets list -a spm-to
```

Você deve ver:
- `DATABASE_URL` (criado automaticamente pelo postgres attach)
- `SECRET_KEY` (criado no comando acima)

## Passo 6: Deploy da Aplicação

### Primeiro deploy
```bash
fly deploy
```

Este comando irá:
1. Construir a imagem Docker usando o Dockerfile
2. Fazer push da imagem para o registro do Fly.io
3. Criar e iniciar as máquinas virtuais
4. Executar health checks

**Tempo estimado:** 3-5 minutos

### Acompanhar logs durante o deploy
Em outro terminal:
```bash
fly logs -a spm-to
```

## Passo 7: Inicializar o Banco de Dados

Após o deploy bem-sucedido, você precisa inicializar o banco de dados.

### Criar tabelas
```bash
fly ssh console -a spm-to -C "python run.py initdb"
```

### Criar usuário admin
```bash
fly ssh console -a spm-to -C "python run.py createadmin"
```

**Credenciais padrão criadas:**
- Usuário: `admin`
- Senha: `admin123`

**⚠️ IMPORTANTE:** Altere esta senha imediatamente após o primeiro login!

### Popular com dados dos instrumentos SPM
```bash
fly ssh console -a spm-to -C "python run.py seed"
```

Este comando irá:
- Carregar os instrumentos SPM 5-12 e SPM-P 3-5
- Importar todas as questões das planilhas Excel
- Carregar as tabelas de referência (T-scores, percentis, classificações)

**Tempo estimado:** 1-2 minutos

## Passo 8: Verificar Deployment

### Abrir aplicação no navegador
```bash
fly open -a spm-to
```

Ou acesse diretamente: `https://spm-to.fly.dev`

### Verificar status
```bash
fly status -a spm-to
```

### Verificar logs
```bash
fly logs -a spm-to
```

### Fazer login na aplicação
1. Acesse a URL da aplicação
2. Clique em "Login"
3. Use as credenciais: `admin` / `admin123`
4. **Altere a senha** em Admin > Usuários

## Passo 9: Configurações Pós-Deploy

### Escalar recursos (se necessário)

Se a aplicação estiver lenta ou apresentar erros de memória:

```bash
# Aumentar memória para 1GB
fly scale memory 1024 -a spm-to

# Adicionar mais CPUs
fly scale vm shared-cpu-2x -a spm-to

# Adicionar mais instâncias (para alta disponibilidade)
fly scale count 2 -a spm-to
```

### Configurar domínio personalizado (opcional)

```bash
# Adicionar certificado SSL para domínio customizado
fly certs add seudominio.com -a spm-to
```

Depois configure os registros DNS conforme instruído pelo Fly.io.

## Comandos Úteis

### Ver informações da aplicação
```bash
fly info -a spm-to
```

### Acessar console SSH
```bash
fly ssh console -a spm-to
```

### Ver configuração atual
```bash
fly config show -a spm-to
```

### Reiniciar aplicação
```bash
fly apps restart spm-to
```

### Ver métricas
```bash
fly dashboard -a spm-to
```

### Fazer backup do banco
```bash
fly postgres connect -a spm-to-db -C "pg_dump -U postgres -Fc spm_to > /tmp/backup.dump"
```

## Atualizações Futuras

Quando você fizer alterações no código:

```bash
# 1. Commitar suas alterações
git add .
git commit -m "Descrição das alterações"

# 2. Fazer novo deploy
fly deploy -a spm-to

# 3. Verificar logs
fly logs -a spm-to
```

## Migrations do Banco de Dados

Se você fizer alterações nos models:

```bash
# Conectar via SSH e executar migrations
fly ssh console -a spm-to

# Dentro do console:
cd /app
flask db migrate -m "Descrição da alteração"
flask db upgrade
exit
```

Ou diretamente:
```bash
fly ssh console -a spm-to -C "cd /app && flask db upgrade"
```

## Troubleshooting

### Aplicação não inicia

```bash
# Ver logs detalhados
fly logs -a spm-to

# Verificar status
fly status -a spm-to

# Verificar health checks
fly checks list -a spm-to
```

### Erro de conexão com banco de dados

```bash
# Verificar se o banco está rodando
fly status -a spm-to-db

# Verificar se DATABASE_URL está configurada
fly secrets list -a spm-to

# Testar conexão
fly ssh console -a spm-to
# Dentro do console:
python -c "from app import create_app; app = create_app(); print('DB OK')"
```

### Erro 502 Bad Gateway

Geralmente indica que a aplicação não está respondendo. Verifique:

```bash
# Logs da aplicação
fly logs -a spm-to

# Aumentar timeout no fly.toml
# Edit fly.toml e ajuste timeout no health check
# Depois: fly deploy
```

### Aplicação lenta

```bash
# Escalar memória
fly scale memory 1024 -a spm-to

# Ou escalar VM
fly scale vm shared-cpu-2x -a spm-to
```

### Erro ao importar dados (seed)

```bash
# Verificar se as planilhas estão no container
fly ssh console -a spm-to -C "ls -la /app/DOCTOS"

# Se os arquivos não estiverem lá, refaça o deploy:
fly deploy -a spm-to

# Depois tente o seed novamente
fly ssh console -a spm-to -C "python run.py seed"
```

## Custos Estimados

**Tier Gratuito Fly.io:**
- 3 VMs compartilhadas (shared-cpu-1x, 256MB RAM)
- 3GB storage persistente
- 160GB bandwidth

**Configuração Recomendada (Baixo Custo):**
- App: 1x shared-cpu-1x, 512MB RAM (~$3-5/mês)
- PostgreSQL: 1x shared-cpu-1x, 1GB storage (~$0-3/mês)

**Total estimado:** $0-8/mês (dentro ou próximo do free tier)

Para produção com mais usuários, considere:
- App: 2x shared-cpu-2x, 1GB RAM (~$15-20/mês)
- PostgreSQL: Dedicated-cpu-1x, 10GB storage (~$15-25/mês)

## Segurança

### Checklist pós-deploy:

- [ ] Alterar senha do admin padrão
- [ ] Configurar HTTPS (já vem habilitado por padrão no Fly.io)
- [ ] Verificar SECRET_KEY está definida e não é o valor padrão
- [ ] Revisar permissões de usuários
- [ ] Configurar backups automáticos do banco
- [ ] Monitorar logs regularmente

### Configurar backups automáticos

```bash
# Criar script de backup
fly ssh console -a spm-to-db

# Dentro do console, criar arquivo de backup script
# E configurar cron job ou usar serviço de backup do Fly.io
```

## Suporte

- Documentação Fly.io: https://fly.io/docs/
- Community Forum: https://community.fly.io/
- Status Page: https://status.flyio.net/

## Próximos Passos

1. ✅ Deploy realizado
2. ✅ Banco de dados inicializado
3. ✅ Dados SPM importados
4. ⬜ Alterar senha admin
5. ⬜ Criar usuários terapeutas
6. ⬜ Cadastrar primeiro paciente
7. ⬜ Realizar primeira avaliação
8. ⬜ Configurar domínio personalizado (opcional)
9. ⬜ Configurar backups automáticos
10. ⬜ Monitoramento e alertas

---

**Versão do Guia:** 1.0
**Última Atualização:** 06/11/2025
**Aplicação:** SPM-TO v1.0.0
