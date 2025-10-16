"""
Script de teste de conectividade com equipamentos solares
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from backend.services.modbus_client import ModbusClient
from backend.config import settings, EQUIPMENT_CONFIG

async def test_modbus_connection(host, port, unit_id, device_name):
    """Testar conexão Modbus com um dispositivo"""
    print(f"\n🔌 Testando conexão com {device_name}")
    print(f"   Host: {host}:{port}")
    print(f"   Unit ID: {unit_id}")
    
    client = ModbusClient()
    
    try:
        # Tentar conectar
        await client.connect(host, port, timeout=5)
        print(f"   ✅ Conexão estabelecida")
        
        # Testar leitura de um registro básico
        if device_name == "Inversor":
            # Testar leitura da potência de saída
            test_address = 0x0001
            print(f"   📖 Testando leitura do registro 0x{test_address:04X} (Potência de Saída)")
        else:
            # Testar leitura do status da conexão
            test_address = 0x0100
            print(f"   📖 Testando leitura do registro 0x{test_address:04X} (Status da Conexão)")
        
        value = await client.read_holding_register(test_address, unit_id)
        
        if value is not None:
            print(f"   ✅ Valor lido: {value}")
            return True
        else:
            print(f"   ❌ Falha ao ler registro")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False
    finally:
        await client.disconnect()

async def test_inverter_communication():
    """Testar comunicação com o inversor"""
    print("\n" + "="*50)
    print("🔋 TESTE DE COMUNICAÇÃO - INVERSOR")
    print("="*50)
    
    inverter_config = EQUIPMENT_CONFIG["inverter"]
    print(f"📋 Informações do Inversor:")
    print(f"   Serial Number: {inverter_config['serial_number']}")
    print(f"   Modelo: {inverter_config['model']}")
    print(f"   Potência Nominal: {inverter_config['rated_power']} W")
    print(f"   MPPT Count: {inverter_config['mppt_count']}")
    print(f"   Versão do Protocolo: {inverter_config['protocol_version']}")
    
    # Testar conexão básica
    success = await test_modbus_connection(
        settings.INVERTER_HOST,
        settings.INVERTER_PORT,
        settings.INVERTER_ADDRESS,
        "Inversor"
    )
    
    if success:
        print("\n📊 Testando leitura de múltiplos registros...")
        client = ModbusClient()
        try:
            await client.connect(settings.INVERTER_HOST, settings.INVERTER_PORT)
            
            registers = inverter_config["modbus_registers"]
            print(f"   Registros disponíveis: {len(registers)}")
            
            for reg_name, address in registers.items():
                try:
                    value = await client.read_holding_register(address, settings.INVERTER_ADDRESS)
                    if value is not None:
                        print(f"   ✅ {reg_name}: {value}")
                    else:
                        print(f"   ❌ {reg_name}: Falha na leitura")
                except Exception as e:
                    print(f"   ❌ {reg_name}: {e}")
            
        except Exception as e:
            print(f"   ❌ Erro na leitura múltipla: {e}")
        finally:
            await client.disconnect()
    
    return success

async def test_logger_communication():
    """Testar comunicação com o logger"""
    print("\n" + "="*50)
    print("📡 TESTE DE COMUNICAÇÃO - LOGGER")
    print("="*50)
    
    logger_config = EQUIPMENT_CONFIG["logger"]
    print(f"📋 Informações do Logger:")
    print(f"   Serial Number: {logger_config['serial_number']}")
    print(f"   Modelo: {logger_config['model']}")
    print(f"   Firmware: {logger_config['firmware_version']}")
    print(f"   Sistema: {logger_config['system_version']}")
    print(f"   MAC Address: {logger_config['mac_address']}")
    print(f"   Router SSID: {logger_config['router_ssid']}")
    print(f"   Força do Sinal: {logger_config['signal_strength']}%")
    
    # Testar conexão básica
    success = await test_modbus_connection(
        settings.LOGGER_HOST,
        settings.LOGGER_PORT,
        settings.LOGGER_ADDRESS,
        "Logger"
    )
    
    if success:
        print("\n📊 Testando leitura de registros do logger...")
        client = ModbusClient()
        try:
            await client.connect(settings.LOGGER_HOST, settings.LOGGER_PORT)
            
            registers = logger_config["modbus_registers"]
            print(f"   Registros disponíveis: {len(registers)}")
            
            for reg_name, address in registers.items():
                try:
                    value = await client.read_holding_register(address, settings.LOGGER_ADDRESS)
                    if value is not None:
                        print(f"   ✅ {reg_name}: {value}")
                    else:
                        print(f"   ❌ {reg_name}: Falha na leitura")
                except Exception as e:
                    print(f"   ❌ {reg_name}: {e}")
            
        except Exception as e:
            print(f"   ❌ Erro na leitura múltipla: {e}")
        finally:
            await client.disconnect()
    
    return success

async def test_network_configuration():
    """Testar configuração de rede"""
    print("\n" + "="*50)
    print("🌐 TESTE DE CONFIGURAÇÃO DE REDE")
    print("="*50)
    
    print(f"📋 Configurações atuais:")
    print(f"   Inversor: {settings.INVERTER_HOST}:{settings.INVERTER_PORT}")
    print(f"   Logger: {settings.LOGGER_HOST}:{settings.LOGGER_PORT}")
    print(f"   Timeout: {settings.INVERTER_TIMEOUT}s")
    
    # Testar conectividade de rede básica
    import socket
    
    def test_host_port(host, port, name):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ {name}: {host}:{port} - Porta acessível")
                return True
            else:
                print(f"   ❌ {name}: {host}:{port} - Porta não acessível")
                return False
        except Exception as e:
            print(f"   ❌ {name}: {host}:{port} - Erro: {e}")
            return False
    
    inverter_network = test_host_port(settings.INVERTER_HOST, settings.INVERTER_PORT, "Inversor")
    logger_network = test_host_port(settings.LOGGER_HOST, settings.LOGGER_PORT, "Logger")
    
    return inverter_network and logger_network

async def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONECTIVIDADE - SISTEMA DE MONITORAMENTO SOLAR")
    print("="*70)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Testar configuração de rede
    network_ok = await test_network_configuration()
    
    if not network_ok:
        print("\n❌ PROBLEMAS DE REDE DETECTADOS")
        print("Verifique:")
        print("- Se os equipamentos estão ligados")
        print("- Se os IPs estão corretos no arquivo .env")
        print("- Se não há firewall bloqueando as portas")
        print("- Se os equipamentos estão na mesma rede")
        return
    
    # Testar comunicação com equipamentos
    inverter_ok = await test_inverter_communication()
    logger_ok = await test_logger_communication()
    
    # Resumo dos testes
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    print(f"🌐 Rede: {'✅ OK' if network_ok else '❌ FALHA'}")
    print(f"🔋 Inversor: {'✅ OK' if inverter_ok else '❌ FALHA'}")
    print(f"📡 Logger: {'✅ OK' if logger_ok else '❌ FALHA'}")
    
    if inverter_ok and logger_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O sistema está pronto para monitoramento.")
        print("\nPara iniciar o sistema, execute:")
        print("   python main.py")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique as configurações e tente novamente.")
        print("\nDicas para solução de problemas:")
        
        if not inverter_ok:
            print("- Verifique se o inversor está ligado e configurado")
            print("- Confirme o IP e porta do inversor")
            print("- Teste a conectividade de rede")
        
        if not logger_ok:
            print("- Verifique se o logger está ligado e conectado ao Wi-Fi")
            print("- Confirme o IP e porta do logger")
            print("- Verifique a configuração do Wi-Fi do logger")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
