@echo off
echo ========================================
echo Sistema de Monitoramento Solar
echo ========================================
echo.

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

echo.
echo Verificando dependencias...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

echo.
echo Criando diretorios...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist backups mkdir backups
if not exist frontend\dist mkdir frontend\dist

echo.
echo Verificando arquivo de configuracao...
if not exist .env (
    if exist env.example (
        echo Copiando arquivo de configuracao...
        copy env.example .env
        echo.
        echo IMPORTANTE: Configure o arquivo .env com os IPs dos seus equipamentos!
        echo.
    ) else (
        echo AVISO: Arquivo env.example nao encontrado!
    )
)

echo.
echo Iniciando sistema...
echo Dashboard: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar o sistema
echo.

python main.py

pause
