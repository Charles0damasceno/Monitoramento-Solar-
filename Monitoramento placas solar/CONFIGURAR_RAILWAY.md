# Configuração do Railway - Passo a Passo

## ✅ Railway CLI Instalado com Sucesso!

O Railway CLI foi instalado corretamente (versão 4.10.0).

## 🔐 Passo 1: Fazer Login no Railway

Execute este comando no terminal:

```bash
railway login
```

**O que vai acontecer:**
1. Abrirá uma janela do navegador
2. Faça login com sua conta GitHub/Google
3. Autorize o Railway CLI
4. Volte ao terminal - estará logado

## 🚀 Passo 2: Conectar ao Projeto

Após fazer login, execute:

```bash
railway link
```

**O que vai acontecer:**
1. Listará seus projetos Railway
2. Escolha o projeto do sistema solar
3. O projeto será vinculado localmente

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

Execute estes comandos:

```bash
# Configurar IP do logger
railway variables set LOGGER_HOST=192.168.0.101

# Configurar porta do logger
railway variables set LOGGER_PORT=502

# Configurar endereço do logger
railway variables set LOGGER_ADDRESS=2

# Gerar chave secreta
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Configurar banco de dados (Railway gera automaticamente)
railway variables set DATABASE_URL=$DATABASE_URL

# Configurar Redis (Railway gera automaticamente)
railway variables set REDIS_URL=$REDIS_URL
```

## 🔄 Passo 4: Fazer Deploy

Execute:

```bash
railway up
```

**O que vai acontecer:**
1. Build do projeto
2. Deploy na nuvem
3. Sistema ficará online

## 📊 Passo 5: Verificar Status

Execute:

```bash
railway status
```

**Para ver:**
- Status do deploy
- URLs do projeto
- Logs do sistema

## 🌐 Passo 6: Acessar o Sistema

Após o deploy, acesse:

- **Dashboard**: `https://seu-app.railway.app`
- **API**: `https://seu-app.railway.app/docs`
- **Health**: `https://seu-app.railway.app/health`

## 🛠️ Comandos Úteis

```bash
# Ver logs do sistema
railway logs

# Ver variáveis configuradas
railway variables

# Parar o sistema
railway down

# Reiniciar o sistema
railway restart

# Ver status
railway status
```

## 🚨 Solução de Problemas

### Se der erro de login:
```bash
# Limpar cache e tentar novamente
railway logout
railway login
```

### Se der erro de link:
```bash
# Listar projetos disponíveis
railway projects

# Conectar manualmente
railway link --project SEU_PROJECT_ID
```

### Se der erro de deploy:
```bash
# Ver logs detalhados
railway logs --follow

# Verificar variáveis
railway variables
```

## 📱 Próximo Passo: Coletor Local

Após configurar o Railway, execute no local do equipamento:

```bash
python remote_collector.py --env production
```

**Isso irá:**
1. Conectar ao logger 192.168.0.101
2. Coletar dados a cada 60 segundos
3. Enviar dados para a API na nuvem
4. Salvar backup local

## 🎯 Resultado Final

Após completar todos os passos:

✅ **Sistema na nuvem** funcionando  
✅ **Acesso global** de qualquer lugar  
✅ **Coletor local** enviando dados  
✅ **Dashboard** com dados em tempo real  
✅ **Alertas** automáticos  

**🌍 Seu sistema solar estará monitorado globalmente!**
