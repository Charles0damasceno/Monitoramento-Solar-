#!/bin/bash

echo "Deploy do Sistema de Monitoramento Solar"
echo "============================================="

# Verificar se Railway CLI est� instalado
if ! command -v railway &> /dev/null; then
    echo "ERRO - Railway CLI n�o encontrado"
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

# Configurar vari�veis de ambiente
echo "Configurando vari�veis de ambiente..."
railway variables set LOGGER_HOST=192.168.0.101
railway variables set LOGGER_PORT=502
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
echo "Fazendo deploy..."
railway up

echo "OK - Deploy conclu�do!"
echo "Acesse: https://seu-app.railway.app"
