#!/usr/bin/env python3
"""
Script de inicialização para Railway
"""

import os
import sys
from pathlib import Path

def main():
    """Função principal de inicialização"""
    print("Iniciando Sistema de Monitoramento Solar")
    print("=" * 50)
    
    # Verificar se estamos no Railway
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print("OK - Executando no Railway")
        print(f"   Ambiente: {os.getenv('RAILWAY_ENVIRONMENT')}")
    else:
        print("INFO - Executando localmente")
    
    # Verificar Python
    print(f"Python: {sys.version}")
    
    # Verificar dependências
    try:
        import fastapi
        import uvicorn
        print("OK - Dependencias principais OK")
    except ImportError as e:
        print(f"ERRO de dependencia: {e}")
        return 1
    
    # Criar diretórios necessários
    directories = ["logs", "data", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Diretorio criado: {directory}")
    
    # Configurar variáveis de ambiente padrão
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Iniciar servidor
    print("Iniciando servidor web...")
    print("   URL: http://0.0.0.0:8000")
    print("   Docs: http://0.0.0.0:8000/docs")
    print("-" * 50)
    
    try:
        # Importar e executar o app
        from backend.main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            log_level="info"
        )
    except Exception as e:
        print(f"ERRO ao iniciar servidor: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
