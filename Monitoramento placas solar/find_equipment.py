"""
Script para descobrir automaticamente os IPs dos equipamentos solares
"""

import socket
import threading
import time
from datetime import datetime
import json

def scan_port(host, port, timeout=1):
    """Testar se uma porta está aberta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_local_ip():
    """Obter o IP da máquina local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.1"

def get_network_range():
    """Obter a faixa de IPs da rede local"""
    local_ip = get_local_ip()
    parts = local_ip.split('.')
    base_ip = '.'.join(parts[:3])
    return base_ip

def scan_network_for_modbus():
    """Escanear a rede em busca de dispositivos Modbus"""
    print("🔍 Escaneando rede em busca de equipamentos Modbus...")
    print(f"📡 Faixa de rede: {get_network_range()}.x")
    print("⏳ Isso pode levar alguns minutos...")
    print()
    
    network_base = get_network_range()
    modbus_ports = [502, 1502, 2502]  # Portas comuns do Modbus
    found_devices = []
    
    def scan_ip(ip):
        """Escanear um IP específico"""
        for port in modbus_ports:
            if scan_port(ip, port, timeout=2):
                found_devices.append({
                    'ip': ip,
                    'port': port,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ Dispositivo encontrado: {ip}:{port}")
    
    # Escanear IPs de 1 a 254
    threads = []
    for i in range(1, 255):
        ip = f"{network_base}.{i}"
        thread = threading.Thread(target=scan_ip, args=(ip,))
        threads.append(thread)
        thread.start()
        
        # Limitar número de threads simultâneas
        if len(threads) >= 50:
            for t in threads:
                t.join()
            threads = []
    
    # Aguardar threads restantes
    for thread in threads:
        thread.join()
    
    return found_devices

def test_modbus_device(ip, port):
    """Testar se o dispositivo responde ao protocolo Modbus"""
    try:
        # Tentar conectar e fazer uma leitura básica
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        # Enviar uma requisição Modbus básica (ler registros)
        # Função 0x03 (Read Holding Registers), Endereço 0, Quantidade 1, Unit ID 1
        modbus_request = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'
        sock.send(modbus_request)
        
        # Tentar receber resposta
        response = sock.recv(1024)
        sock.close()
        
        if len(response) >= 8:  # Resposta mínima do Modbus
            return True, "Responde ao protocolo Modbus"
        else:
            return False, "Porta aberta mas não responde ao Modbus"
            
    except Exception as e:
        return False, f"Erro na comunicação: {str(e)}"

def identify_equipment(ip, port):
    """Tentar identificar o tipo de equipamento"""
    try:
        # Tentar diferentes Unit IDs comuns
        unit_ids = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16]
        
        for unit_id in unit_ids:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((ip, port))
                
                # Tentar ler registros de identificação (0x1000-0x1003)
                modbus_request = bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, unit_id, 0x03, 0x10, 0x00, 0x00, 0x04])
                sock.send(modbus_request)
                
                response = sock.recv(1024)
                sock.close()
                
                if len(response) >= 8:
                    # Analisar resposta para tentar identificar o equipamento
                    if unit_id == 1:
                        return "Possível Inversor", f"Unit ID {unit_id}"
                    elif unit_id == 2:
                        return "Possível Logger", f"Unit ID {unit_id}"
                    else:
                        return "Dispositivo Modbus", f"Unit ID {unit_id}"
                        
            except:
                continue
                
        return "Dispositivo Modbus", "Unit ID não identificado"
        
    except:
        return "Dispositivo Desconhecido", "Não foi possível identificar"

def generate_config(devices):
    """Gerar configuração sugerida baseada nos dispositivos encontrados"""
    config = {
        "inverter": None,
        "logger": None
    }
    
    for device in devices:
        equipment_type, details = identify_equipment(device['ip'], device['port'])
        
        if "Inversor" in equipment_type and not config["inverter"]:
            config["inverter"] = {
                "ip": device['ip'],
                "port": device['port'],
                "unit_id": 1,
                "type": equipment_type,
                "details": details
            }
        elif "Logger" in equipment_type and not config["logger"]:
            config["logger"] = {
                "ip": device['ip'],
                "port": device['port'],
                "unit_id": 2,
                "type": equipment_type,
                "details": details
            }
        elif not config["inverter"]:
            config["inverter"] = {
                "ip": device['ip'],
                "port": device['port'],
                "unit_id": 1,
                "type": equipment_type,
                "details": details
            }
        elif not config["logger"]:
            config["logger"] = {
                "ip": device['ip'],
                "port": device['port'],
                "unit_id": 2,
                "type": equipment_type,
                "details": details
            }
    
    return config

def save_discovery_results(devices, config):
    """Salvar resultados da descoberta"""
    results = {
        "discovery_time": datetime.now().isoformat(),
        "network_range": get_network_range(),
        "found_devices": devices,
        "suggested_config": config
    }
    
    with open("equipment_discovery.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados salvos em: equipment_discovery.json")

def main():
    """Função principal"""
    print("🔍 DESCOBRIDOR AUTOMÁTICO DE EQUIPAMENTOS SOLARES")
    print("=" * 60)
    print()
    
    # Escanear rede
    devices = scan_network_for_modbus()
    
    print()
    print("📊 RESULTADOS DA DESCOBERTA:")
    print("=" * 40)
    
    if not devices:
        print("❌ Nenhum dispositivo Modbus encontrado na rede")
        print()
        print("💡 DICAS PARA SOLUÇÃO DE PROBLEMAS:")
        print("1. Verifique se os equipamentos estão ligados")
        print("2. Confirme se estão na mesma rede Wi-Fi")
        print("3. Verifique se não há firewall bloqueando")
        print("4. Tente escanear manualmente com:")
        print("   - Advanced IP Scanner")
        print("   - nmap (se disponível)")
        print("   - Aplicativo do fabricante")
        return
    
    # Identificar equipamentos
    print(f"✅ {len(devices)} dispositivo(s) Modbus encontrado(s):")
    print()
    
    for i, device in enumerate(devices, 1):
        equipment_type, details = identify_equipment(device['ip'], device['port'])
        print(f"{i}. {device['ip']}:{device['port']}")
        print(f"   Tipo: {equipment_type}")
        print(f"   Detalhes: {details}")
        print()
    
    # Gerar configuração sugerida
    suggested_config = generate_config(devices)
    
    print("⚙️ CONFIGURAÇÃO SUGERIDA:")
    print("=" * 40)
    
    if suggested_config["inverter"]:
        print("🔋 Inversor:")
        print(f"   IP: {suggested_config['inverter']['ip']}")
        print(f"   Porta: {suggested_config['inverter']['port']}")
        print(f"   Unit ID: {suggested_config['inverter']['unit_id']}")
        print(f"   Tipo: {suggested_config['inverter']['type']}")
        print()
    
    if suggested_config["logger"]:
        print("📡 Logger:")
        print(f"   IP: {suggested_config['logger']['ip']}")
        print(f"   Porta: {suggested_config['logger']['port']}")
        print(f"   Unit ID: {suggested_config['logger']['unit_id']}")
        print(f"   Tipo: {suggested_config['logger']['type']}")
        print()
    
    # Salvar resultados
    save_discovery_results(devices, suggested_config)
    
    print("🚀 PRÓXIMOS PASSOS:")
    print("=" * 40)
    print("1. Acesse o dashboard: http://localhost:8000")
    print("2. Clique em 'Configuração' no menu")
    print("3. Preencha os IPs encontrados")
    print("4. Teste as conexões")
    print("5. Salve as configurações")
    print()
    
    # Gerar arquivo .env sugerido
    if suggested_config["inverter"] or suggested_config["logger"]:
        print("📝 Gerando arquivo .env sugerido...")
        
        env_content = "# Configurações do Sistema de Monitoramento Solar\n"
        env_content += "# Gerado automaticamente pelo descobridor de equipamentos\n\n"
        
        if suggested_config["inverter"]:
            env_content += f"INVERTER_HOST={suggested_config['inverter']['ip']}\n"
            env_content += f"INVERTER_PORT={suggested_config['inverter']['port']}\n"
            env_content += f"INVERTER_ADDRESS={suggested_config['inverter']['unit_id']}\n\n"
        
        if suggested_config["logger"]:
            env_content += f"LOGGER_HOST={suggested_config['logger']['ip']}\n"
            env_content += f"LOGGER_PORT={suggested_config['logger']['port']}\n"
            env_content += f"LOGGER_ADDRESS={suggested_config['logger']['unit_id']}\n\n"
        
        env_content += "DATA_COLLECTION_INTERVAL=60\n"
        env_content += "CONNECTION_TIMEOUT_THRESHOLD=5\n"
        
        with open(".env.suggested", "w") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env.suggested criado!")
        print("   Copie o conteúdo para o arquivo .env se desejar usar essas configurações")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Descoberta interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a descoberta: {e}")
        import traceback
        traceback.print_exc()
