"""
Script para Deploy do Sistema na Nuvem
Usa Railway para deploy automático
"""

import os
import json
import subprocess
import sys

def create_railway_config():
    """Criar configuração para Railway"""
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python main.py",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    print("OK - railway.json criado")

def create_requirements_cloud():
    """Criar requirements.txt para nuvem"""
    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "sqlalchemy==2.0.23",
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        "pymodbus==3.5.2",
        "aiohttp==3.9.1",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "asyncio-mqtt==0.16.1",
        "redis==5.0.1",
        "celery==5.3.4",
        "gunicorn==21.2.0"
    ]
    
    with open("requirements-cloud.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("OK - requirements-cloud.txt criado")

def create_procfile():
    """Criar Procfile para deploy"""
    procfile_content = """web: gunicorn main:app --host 0.0.0.0 --port $PORT
worker: python remote_collector.py --env production
"""
    
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    
    print("OK - Procfile criado")

def create_dockerfile():
    """Criar Dockerfile para deploy"""
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements-cloud.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "main.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("OK - Dockerfile criado")

def create_env_template():
    """Criar template de variáveis de ambiente"""
    env_template = """# Configurações da Aplicação
APP_NAME=Sistema de Monitoramento Solar
DEBUG=false
SECRET_KEY=SUA_CHAVE_SECRETA_SUPER_FORTE_AQUI

# Banco de Dados (Railway PostgreSQL)
DATABASE_URL=${{DATABASE_URL}}

# CORS
ALLOWED_ORIGINS=["https://seu-app.railway.app", "https://seu-dominio.com"]

# Modbus - Logger (IP do equipamento local)
LOGGER_HOST=192.168.0.101
LOGGER_PORT=502
LOGGER_ADDRESS=2
LOGGER_TIMEOUT=5

# Coleta de Dados
DATA_COLLECTION_INTERVAL=60
DATA_RETENTION_DAYS=365

# Alertas por Email
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=seu-email@gmail.com
ALERT_EMAIL_PASSWORD=SUA_SENHA_APP
ALERT_EMAIL_TO=["admin@seu-dominio.com"]

# Thresholds para Alertas
LOW_PRODUCTION_THRESHOLD=300
HIGH_TEMPERATURE_THRESHOLD=70.0
CONNECTION_TIMEOUT_THRESHOLD=300

# Cache Redis (Railway Redis)
REDIS_URL=${{REDIS_URL}}

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/solar_monitoring.log
"""
    
    with open("env.railway", "w") as f:
        f.write(env_template)
    
    print("OK - env.railway criado")

def create_deploy_script():
    """Criar script de deploy"""
    deploy_script = """#!/bin/bash

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
"""
    
    with open("deploy.sh", "w") as f:
        f.write(deploy_script)
    
    # Tornar executável
    os.chmod("deploy.sh", 0o755)
    
    print("OK - deploy.sh criado")

def create_github_actions():
    """Criar GitHub Actions para deploy automático"""
    github_workflow = """name: Deploy to Railway

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Railway CLI
      run: npm install -g @railway/cli
    
    - name: Deploy to Railway
      run: railway up --service
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    with open(".github/workflows/deploy.yml", "w") as f:
        f.write(github_workflow)
    
    print("OK - GitHub Actions criado")

def main():
    """Função principal"""
    print("Configurando Deploy na Nuvem")
    print("=" * 50)
    
    # Criar arquivos de configuração
    create_railway_config()
    create_requirements_cloud()
    create_procfile()
    create_dockerfile()
    create_env_template()
    create_deploy_script()
    create_github_actions()
    
    print("\nOK - Arquivos de deploy criados!")
    print("\nProximos passos:")
    print("1. Instalar Railway CLI: npm install -g @railway/cli")
    print("2. Executar: ./deploy.sh")
    print("3. Ou conectar repositorio GitHub ao Railway")
    print("\nApos deploy, acesse: https://seu-app.railway.app")
    print("\nPara acesso mobile, configure PWA no frontend")

if __name__ == "__main__":
    main()
