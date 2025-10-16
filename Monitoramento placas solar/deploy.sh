#!/bin/bash

echo "Deploy do Sistema de Monitoramento Solar"
echo "============================================="

# Verificar se Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "ERRO - Railway CLI não encontrado"
    echo "Instale com: npm install -g @railway/cli"
    exit 1
fi

# Login no Railway
echo "Fazendo login no Railway..."
railway login

# Criar novo projeto
echo "Criando projeto no Railway..."
railway init

# Adicionar PostgreSQL
echo "Adicionando PostgreSQL..."
railway add postgresql

# Adicionar Redis
echo "Adicionando Redis..."
railway add redis

# Configurar variáveis de ambiente
echo "Configurando variáveis de ambiente..."
railway variables set LOGGER_HOST=192.168.0.101
railway variables set LOGGER_PORT=502
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
echo "Fazendo deploy..."
railway up

echo "OK - Deploy concluído!"
echo "Acesse: https://seu-app.railway.app"
