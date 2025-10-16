"""
Cliente Modbus para comunicação com equipamentos solares
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)

class ModbusClient:
    """Cliente Modbus assíncrono para comunicação com equipamentos"""
    
    def __init__(self):
        self.client: Optional[ModbusTcpClient] = None
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.connected = False
        
    async def connect(self, host: str, port: int, timeout: int = 5):
        """Conectar ao dispositivo Modbus"""
        try:
            if self.client and self.connected:
                await self.disconnect()
                
            self.host = host
            self.port = port
            
            # Criar cliente Modbus TCP
            self.client = ModbusTcpClient(
                host=host,
                port=port,
                timeout=timeout
            )
            
            # Conectar
            self.client.connect()
            self.connected = True
            logger.info(f"Conectado ao Modbus TCP {host}:{port}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar Modbus TCP {host}:{port}: {e}")
            self.connected = False
            raise
            
    async def disconnect(self):
        """Desconectar do dispositivo Modbus"""
        try:
            if self.client and self.connected:
                self.client.close()
                self.connected = False
                logger.info(f"Desconectado do Modbus TCP {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Erro ao desconectar Modbus TCP: {e}")
        finally:
            self.client = None
            self.host = None
            self.port = None
            
    async def is_connected(self) -> bool:
        """Verificar se está conectado"""
        return self.connected and self.client is not None
        
    async def read_holding_register(self, address: int, unit_id: int = 1) -> Optional[Any]:
        """Ler registro de holding"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = self.client.read_holding_registers(
                address=address,
                count=1,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao ler registro 0x{address:04X}: {result}")
                return None
                
            # Retornar o valor lido (assumindo que é um valor de 16 bits)
            return result.registers[0] if result.registers else None
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao ler registro 0x{address:04X}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao ler registro 0x{address:04X}: {e}")
            return None
            
    async def read_holding_registers(self, address: int, count: int, unit_id: int = 1) -> Optional[list]:
        """Ler múltiplos registros de holding"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = await self.client.read_holding_registers(
                address=address,
                count=count,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao ler registros 0x{address:04X} (count={count}): {result}")
                return None
                
            return result.registers
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao ler registros 0x{address:04X}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao ler registros 0x{address:04X}: {e}")
            return None
            
    async def read_input_register(self, address: int, unit_id: int = 1) -> Optional[Any]:
        """Ler registro de entrada"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = await self.client.read_input_registers(
                address=address,
                count=1,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao ler registro de entrada 0x{address:04X}: {result}")
                return None
                
            return result.registers[0] if result.registers else None
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao ler registro de entrada 0x{address:04X}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao ler registro de entrada 0x{address:04X}: {e}")
            return None
            
    async def write_holding_register(self, address: int, value: int, unit_id: int = 1) -> bool:
        """Escrever registro de holding"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = await self.client.write_register(
                address=address,
                value=value,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao escrever registro 0x{address:04X}: {result}")
                return False
                
            return True
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao escrever registro 0x{address:04X}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao escrever registro 0x{address:04X}: {e}")
            return False
            
    async def read_coils(self, address: int, count: int = 1, unit_id: int = 1) -> Optional[list]:
        """Ler coils (discretos)"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = await self.client.read_coils(
                address=address,
                count=count,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao ler coils 0x{address:04X}: {result}")
                return None
                
            return result.bits
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao ler coils 0x{address:04X}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao ler coils 0x{address:04X}: {e}")
            return None
            
    async def read_discrete_inputs(self, address: int, count: int = 1, unit_id: int = 1) -> Optional[list]:
        """Ler entradas discretas"""
        if not await self.is_connected():
            raise ConnectionError("Cliente Modbus não conectado")
            
        try:
            result = await self.client.read_discrete_inputs(
                address=address,
                count=count,
                unit=unit_id
            )
            
            if result.isError():
                logger.error(f"Erro ao ler entradas discretas 0x{address:04X}: {result}")
                return None
                
            return result.bits
            
        except ModbusException as e:
            logger.error(f"Exceção Modbus ao ler entradas discretas 0x{address:04X}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao ler entradas discretas 0x{address:04X}: {e}")
            return None
            
    async def get_device_info(self, unit_id: int = 1) -> Optional[Dict[str, Any]]:
        """Obter informações do dispositivo (se suportado)"""
        try:
            # Tentar ler alguns registros comuns para identificar o dispositivo
            device_info = {}
            
            # Ler registros de identificação (se disponíveis)
            for reg_name, address in [
                ("model", 0x1000),
                ("serial", 0x1001),
                ("firmware", 0x1002),
                ("manufacturer", 0x1003)
            ]:
                value = await self.read_holding_register(address, unit_id)
                if value is not None:
                    device_info[reg_name] = value
                    
            return device_info if device_info else None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do dispositivo: {e}")
            return None
