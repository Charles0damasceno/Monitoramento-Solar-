"""
Script simples de teste de conectividade
"""

import socket
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

def test_host_port(host, port, name):
    """Testar conectividade com host e porta"""
    print(f"Testando {name}: {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"  OK - Porta acessivel")
            return True
        else:
            print(f"  FALHA - Porta nao acessivel")
            return False
    except Exception as e:
        print(f"  ERRO: {e}")
        return False

def main():
    """Teste principal"""
    print("="*50)
    print("TESTE DE CONECTIVIDADE - SISTEMA SOLAR")
    print("="*50)
    
    # Configurações do seu equipamento
    logger_ip = "192.168.0.101"
    logger_port = 502
    
    print(f"Logger IP: {logger_ip}")
    print(f"Logger Porta: {logger_port}")
    print()
    
    # Testar conectividade básica
    success = test_host_port(logger_ip, logger_port, "Logger")
    
    print()
    print("="*50)
    if success:
        print("SUCESSO: Logger acessivel!")
        print("O sistema pode se conectar ao equipamento.")
        print()
        print("Para iniciar o monitoramento, execute:")
        print("  python main.py")
    else:
        print("FALHA: Nao foi possivel conectar ao logger")
        print()
        print("Verifique:")
        print("- Se o logger esta ligado")
        print("- Se o IP esta correto (192.168.0.101)")
        print("- Se nao ha firewall bloqueando a porta 502")
        print("- Se o logger esta conectado ao Wi-Fi")
    
    print("="*50)

if __name__ == "__main__":
    main()
