#!/bin/bash

echo "========================================"
echo "Sistema de Monitoramento Solar"
echo "========================================"
echo

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Instale Python 3.8+ e tente novamente."
    exit 1
fi

python3 --version

echo
echo "Verificando dependências..."
if ! pip3 show fastapi &> /dev/null; then
    echo "Instalando dependências..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao instalar dependências!"
        exit 1
    fi
fi

echo
echo "Criando diretórios..."
mkdir -p logs data backups frontend/dist

echo
echo "Verificando arquivo de configuração..."
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        echo "Copiando arquivo de configuração..."
        cp env.example .env
        echo
        echo "IMPORTANTE: Configure o arquivo .env com os IPs dos seus equipamentos!"
        echo
    else
        echo "AVISO: Arquivo env.example não encontrado!"
    fi
fi

echo
echo "Iniciando sistema..."
echo "Dashboard: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Pressione Ctrl+C para parar o sistema"
echo

python3 main.py
