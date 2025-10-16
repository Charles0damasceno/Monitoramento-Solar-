"""
Teste Simples da API
"""

import requests
import time
import sys

def test_api_health():
    """Testar endpoint de saúde da API"""
    try:
        print("Testando API em http://localhost:8000...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            print("OK - API respondendo")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"ERRO - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERRO - API nao esta rodando")
        print("Execute: python main.py")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_api_docs():
    """Testar documentação da API"""
    try:
        print("Testando documentacao da API...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        
        if response.status_code == 200:
            print("OK - Documentacao acessivel")
            print("Acesse: http://localhost:8000/docs")
            return True
        else:
            print(f"ERRO - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_dashboard():
    """Testar dashboard"""
    try:
        print("Testando dashboard em http://localhost:3000...")
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code == 200:
            print("OK - Dashboard acessivel")
            print("Acesse: http://localhost:3000")
            return True
        else:
            print(f"ERRO - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("INFO - Dashboard nao esta rodando")
        print("Para iniciar o dashboard, execute o frontend")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Teste principal"""
    print("="*60)
    print("TESTE SIMPLES DA API E DASHBOARD")
    print("="*60)
    print()
    
    # Testar API
    api_ok = test_api_health()
    print()
    
    if api_ok:
        test_api_docs()
        print()
    
    # Testar Dashboard
    test_dashboard()
    print()
    
    # Resumo
    print("="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    if api_ok:
        print("OK - API funcionando")
        print("  - Health: http://localhost:8000/health")
        print("  - Docs: http://localhost:8000/docs")
    else:
        print("ERRO - API nao esta funcionando")
        print("  - Verifique se executou: python main.py")
        print("  - Verifique se nao ha erros no terminal")
    
    print()
    print("Para iniciar o sistema completo:")
    print("1. Backend: python main.py")
    print("2. Frontend: cd frontend && npm start")
    print("3. Acesse: http://localhost:3000")

if __name__ == "__main__":
    main()
