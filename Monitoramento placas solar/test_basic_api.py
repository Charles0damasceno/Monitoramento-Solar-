"""
Teste Básico da API
"""

from fastapi import FastAPI
import uvicorn

# Criar app FastAPI simples
app = FastAPI(title="Sistema Solar - Teste")

@app.get("/")
def read_root():
    return {"message": "Sistema de Monitoramento Solar - Teste OK"}

@app.get("/health")
def health_check():
    return {"status": "OK", "message": "Sistema funcionando"}

@app.get("/test")
def test_endpoint():
    return {
        "timestamp": "2025-10-16T11:20:00Z",
        "power": 2500,
        "status": "Normal",
        "test": True
    }

if __name__ == "__main__":
    print("Iniciando API de Teste...")
    print("URLs disponíveis:")
    print("  - http://localhost:8000/")
    print("  - http://localhost:8000/health")
    print("  - http://localhost:8000/test")
    print("  - http://localhost:8000/docs")
    print("-" * 50)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nAPI parada pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
