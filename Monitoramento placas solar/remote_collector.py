"""
Coletor Local para Sistema de Monitoramento Solar Remoto
Este script roda no local do equipamento e envia dados para a nuvem
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from backend.services.modbus_client import ModbusClient
from backend.config import settings, EQUIPMENT_CONFIG

class RemoteCollector:
    def __init__(self, cloud_api_url="https://seu-servidor.com/api"):
        self.logger_ip = settings.LOGGER_HOST
        self.logger_port = settings.LOGGER_PORT
        self.cloud_api_url = cloud_api_url
        self.collection_interval = 60  # segundos
        self.running = False
        
    async def collect_solar_data(self):
        """Coletar dados do sistema solar via Modbus"""
        try:
            client = ModbusClient()
            await client.connect(self.logger_ip, self.logger_port)
            
            # Dados do inversor (via logger)
            inverter_data = await self.read_inverter_data(client)
            
            # Dados do logger
            logger_data = await self.read_logger_data(client)
            
            await client.disconnect()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "inverter": inverter_data,
                "logger": logger_data,
                "location": "solar_farm_1"  # Identificar localização
            }
            
        except Exception as e:
            print(f"Erro ao coletar dados: {e}")
            return None
    
    async def read_inverter_data(self, client):
        """Ler dados do inversor"""
        inverter_data = {}
        registers = EQUIPMENT_CONFIG["inverter"]["modbus_registers"]
        
        for reg_name, address in registers.items():
            try:
                value = await client.read_holding_register(address, settings.INVERTER_ADDRESS)
                if value is not None:
                    inverter_data[reg_name] = value
            except Exception as e:
                print(f"Erro ao ler {reg_name}: {e}")
                inverter_data[reg_name] = None
                
        return inverter_data
    
    async def read_logger_data(self, client):
        """Ler dados do logger"""
        logger_data = {}
        registers = EQUIPMENT_CONFIG["logger"]["modbus_registers"]
        
        for reg_name, address in registers.items():
            try:
                value = await client.read_holding_register(address, settings.LOGGER_ADDRESS)
                if value is not None:
                    logger_data[reg_name] = value
            except Exception as e:
                print(f"Erro ao ler {reg_name}: {e}")
                logger_data[reg_name] = None
                
        return logger_data
    
    async def send_to_cloud(self, data):
        """Enviar dados para API na nuvem"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_api_url}/solar-data",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        print(f"✅ Dados enviados: {data['timestamp']}")
                        return True
                    else:
                        print(f"❌ Erro ao enviar: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Erro de conexão com nuvem: {e}")
            return False
    
    async def save_local_backup(self, data):
        """Salvar backup local dos dados"""
        try:
            backup_file = f"backups/solar_data_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs("backups", exist_ok=True)
            
            with open(backup_file, "a") as f:
                f.write(json.dumps(data) + "\n")
                
        except Exception as e:
            print(f"Erro ao salvar backup: {e}")
    
    async def collect_and_send(self):
        """Ciclo principal de coleta e envio"""
        print(f"🔄 Iniciando coleta de dados...")
        print(f"📡 Logger: {self.logger_ip}:{self.logger_port}")
        print(f"☁️  Nuvem: {self.cloud_api_url}")
        print(f"⏱️  Intervalo: {self.collection_interval}s")
        print("-" * 50)
        
        while self.running:
            try:
                # Coletar dados
                data = await self.collect_solar_data()
                
                if data:
                    # Salvar backup local
                    await self.save_local_backup(data)
                    
                    # Enviar para nuvem
                    success = await self.send_to_cloud(data)
                    
                    if success:
                        print(f"📊 Dados coletados e enviados: {data['timestamp']}")
                    else:
                        print("⚠️  Dados coletados mas não enviados (salvos localmente)")
                else:
                    print("❌ Falha na coleta de dados")
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.collection_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Coletor interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no ciclo de coleta: {e}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
    
    async def start(self):
        """Iniciar o coletor"""
        self.running = True
        print("🚀 Iniciando Coletor Remoto de Dados Solares")
        print("=" * 60)
        
        # Testar conectividade inicial
        print("🔍 Testando conectividade...")
        test_data = await self.collect_solar_data()
        
        if test_data:
            print("✅ Conectividade OK - Iniciando coleta contínua")
            await self.collect_and_send()
        else:
            print("❌ Falha na conectividade - Verifique as configurações")
            return False
    
    def stop(self):
        """Parar o coletor"""
        self.running = False
        print("🛑 Parando coletor...")

# Configurações para diferentes ambientes
CLOUD_ENDPOINTS = {
    "development": "https://seu-app.herokuapp.com/api",
    "production": "https://monitor-solar.com/api",
    "local_test": "http://localhost:8000/api"
}

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coletor Remoto de Dados Solares")
    parser.add_argument("--env", choices=["development", "production", "local_test"], 
                       default="development", help="Ambiente de deploy")
    parser.add_argument("--interval", type=int, default=60, 
                       help="Intervalo de coleta em segundos")
    
    args = parser.parse_args()
    
    # Configurar coletor
    collector = RemoteCollector(CLOUD_ENDPOINTS[args.env])
    collector.collection_interval = args.interval
    
    try:
        await collector.start()
    except KeyboardInterrupt:
        print("\n👋 Encerrando coletor...")
        collector.stop()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🌞 Sistema de Monitoramento Solar Remoto")
    print("=" * 50)
    print("Para usar:")
    print("  python remote_collector.py --env development")
    print("  python remote_collector.py --env production --interval 30")
    print("=" * 50)
    
    asyncio.run(main())
