"""
Iniciar Sistema de Teste Simples
"""

import uvicorn
import os

# Criar diretórios necessários
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("backups", exist_ok=True)

if __name__ == "__main__":
    print("Iniciando Sistema de Teste...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nSistema parado pelo usuario")
    except Exception as e:
        print(f"Erro ao iniciar sistema: {e}")
