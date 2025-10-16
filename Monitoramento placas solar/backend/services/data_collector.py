"""
Serviço de coleta de dados dos equipamentos solares
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..config import settings, EQUIPMENT_CONFIG
from ..database import SessionLocal
from ..models import Inverter, InverterMeasurement, Logger, LoggerMeasurement, SystemStatus
from .modbus_client import ModbusClient
from .alert_service import AlertService

logger = logging.getLogger(__name__)

class DataCollectorService:
    """Serviço principal para coleta de dados dos equipamentos"""
    
    def __init__(self):
        self.running = False
        self.modbus_client = ModbusClient()
        self.alert_service = AlertService()
        self.collection_task = None
        self.last_inverter_data = None
        self.last_logger_data = None
        
        # Cache para evitar consultas desnecessárias
        self.inverter_cache = {}
        self.logger_cache = {}
        
    async def start_collection(self):
        """Iniciar coleta automática de dados"""
        if self.running:
            logger.warning("Coleta de dados já está em execução")
            return
            
        self.running = True
        logger.info("Iniciando coleta de dados dos equipamentos solares")
        
        # Inicializar equipamentos no banco de dados
        await self._initialize_equipment()
        
        # Iniciar tarefa de coleta
        self.collection_task = asyncio.create_task(self._collection_loop())
        
    async def stop_collection(self):
        """Parar coleta de dados"""
        if not self.running:
            return
            
        self.running = False
        logger.info("Parando coleta de dados")
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
                
        await self.modbus_client.disconnect()
        
    async def _collection_loop(self):
        """Loop principal de coleta de dados"""
        while self.running:
            try:
                # Coletar dados do inversor
                await self._collect_inverter_data()
                
                # Coletar dados do logger
                await self._collect_logger_data()
                
                # Atualizar status do sistema
                await self._update_system_status()
                
                # Verificar alertas
                await self.alert_service.check_alerts()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(settings.DATA_COLLECTION_INTERVAL)
                
            except Exception as e:
                logger.error(f"Erro no loop de coleta: {e}")
                await asyncio.sleep(30)  # Aguardar 30s antes de tentar novamente
                
    async def _initialize_equipment(self):
        """Inicializar equipamentos no banco de dados"""
        db = SessionLocal()
        try:
            # Verificar se o inversor já existe
            inverter = db.query(Inverter).filter(
                Inverter.serial_number == EQUIPMENT_CONFIG["inverter"]["serial_number"]
            ).first()
            
            if not inverter:
                inverter = Inverter(
                    serial_number=EQUIPMENT_CONFIG["inverter"]["serial_number"],
                    model=EQUIPMENT_CONFIG["inverter"]["model"],
                    rated_power=EQUIPMENT_CONFIG["inverter"]["rated_power"],
                    mppt_count=EQUIPMENT_CONFIG["inverter"]["mppt_count"],
                    protocol_version=EQUIPMENT_CONFIG["inverter"]["protocol_version"]
                )
                db.add(inverter)
                db.commit()
                logger.info(f"Inversor {inverter.serial_number} registrado no banco de dados")
            
            # Verificar se o logger já existe
            logger_device = db.query(Logger).filter(
                Logger.serial_number == EQUIPMENT_CONFIG["logger"]["serial_number"]
            ).first()
            
            if not logger_device:
                logger_device = Logger(
                    serial_number=EQUIPMENT_CONFIG["logger"]["serial_number"],
                    model=EQUIPMENT_CONFIG["logger"]["model"],
                    firmware_version=EQUIPMENT_CONFIG["logger"]["firmware_version"],
                    system_version=EQUIPMENT_CONFIG["logger"]["system_version"],
                    mac_address=EQUIPMENT_CONFIG["logger"]["mac_address"],
                    router_ssid=EQUIPMENT_CONFIG["logger"]["router_ssid"],
                    signal_strength=EQUIPMENT_CONFIG["logger"]["signal_strength"],
                    data_send_interval=EQUIPMENT_CONFIG["logger"]["data_send_interval"],
                    data_log_interval=EQUIPMENT_CONFIG["logger"]["data_log_interval"],
                    max_devices=EQUIPMENT_CONFIG["logger"]["max_devices"]
                )
                db.add(logger_device)
                db.commit()
                logger.info(f"Logger {logger_device.serial_number} registrado no banco de dados")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar equipamentos: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _collect_inverter_data(self):
        """Coletar dados do inversor via Modbus"""
        try:
            # Conectar se necessário
            if not await self.modbus_client.is_connected():
                await self.modbus_client.connect(
                    host=settings.INVERTER_HOST,
                    port=settings.INVERTER_PORT
                )
            
            # Ler dados do inversor
            inverter_data = await self._read_inverter_registers()
            
            if inverter_data:
                await self._save_inverter_measurement(inverter_data)
                self.last_inverter_data = datetime.utcnow()
                logger.debug("Dados do inversor coletados com sucesso")
            else:
                logger.warning("Falha ao coletar dados do inversor")
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados do inversor: {e}")
            await self.alert_service.create_alert(
                alert_type="communication_error",
                severity="high",
                message=f"Erro de comunicação com inversor: {str(e)}"
            )
            
    async def _collect_logger_data(self):
        """Coletar dados do logger via Modbus"""
        try:
            # Conectar se necessário
            if not await self.modbus_client.is_connected():
                await self.modbus_client.connect(
                    host=settings.LOGGER_HOST,
                    port=settings.LOGGER_PORT
                )
            
            # Ler dados do logger
            logger_data = await self._read_logger_registers()
            
            if logger_data:
                await self._save_logger_measurement(logger_data)
                self.last_logger_data = datetime.utcnow()
                logger.debug("Dados do logger coletados com sucesso")
            else:
                logger.warning("Falha ao coletar dados do logger")
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados do logger: {e}")
            await self.alert_service.create_alert(
                alert_type="communication_error",
                severity="medium",
                message=f"Erro de comunicação com logger: {str(e)}"
            )
            
    async def _read_inverter_registers(self) -> Optional[Dict[str, Any]]:
        """Ler registros Modbus do inversor"""
        try:
            registers = EQUIPMENT_CONFIG["inverter"]["modbus_registers"]
            data = {}
            
            # Ler registros de holding (dados de produção)
            for key, address in registers.items():
                try:
                    value = await self.modbus_client.read_holding_register(
                        address, 
                        unit_id=settings.INVERTER_ADDRESS
                    )
                    data[key] = value
                except Exception as e:
                    logger.warning(f"Erro ao ler registro {key} (0x{address:04X}): {e}")
                    data[key] = None
                    
            return data
            
        except Exception as e:
            logger.error(f"Erro ao ler registros do inversor: {e}")
            return None
            
    async def _read_logger_registers(self) -> Optional[Dict[str, Any]]:
        """Ler registros Modbus do logger"""
        try:
            registers = EQUIPMENT_CONFIG["logger"]["modbus_registers"]
            data = {}
            
            # Ler registros de holding (dados de comunicação)
            for key, address in registers.items():
                try:
                    value = await self.modbus_client.read_holding_register(
                        address, 
                        unit_id=settings.LOGGER_ADDRESS
                    )
                    data[key] = value
                except Exception as e:
                    logger.warning(f"Erro ao ler registro {key} (0x{address:04X}): {e}")
                    data[key] = None
                    
            return data
            
        except Exception as e:
            logger.error(f"Erro ao ler registros do logger: {e}")
            return None
            
    async def _save_inverter_measurement(self, data: Dict[str, Any]):
        """Salvar medição do inversor no banco de dados"""
        db = SessionLocal()
        try:
            # Obter inversor
            inverter = db.query(Inverter).filter(
                Inverter.serial_number == EQUIPMENT_CONFIG["inverter"]["serial_number"]
            ).first()
            
            if not inverter:
                logger.error("Inversor não encontrado no banco de dados")
                return
                
            # Criar nova medição
            measurement = InverterMeasurement(
                inverter_id=inverter.id,
                timestamp=datetime.utcnow(),
                power_output=data.get("power_output"),
                energy_daily=data.get("energy_daily"),
                energy_total=data.get("energy_total"),
                voltage_dc=data.get("voltage_dc"),
                current_dc=data.get("current_dc"),
                voltage_ac=data.get("voltage_ac"),
                current_ac=data.get("current_ac"),
                frequency=data.get("frequency"),
                temperature=data.get("temperature"),
                efficiency=data.get("efficiency"),
                status_code=data.get("status"),
                fault_code=data.get("fault_code"),
                uptime=data.get("uptime")
            )
            
            db.add(measurement)
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar medição do inversor: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _save_logger_measurement(self, data: Dict[str, Any]):
        """Salvar medição do logger no banco de dados"""
        db = SessionLocal()
        try:
            # Obter logger
            logger_device = db.query(Logger).filter(
                Logger.serial_number == EQUIPMENT_CONFIG["logger"]["serial_number"]
            ).first()
            
            if not logger_device:
                logger.error("Logger não encontrado no banco de dados")
                return
                
            # Criar nova medição
            measurement = LoggerMeasurement(
                logger_id=logger_device.id,
                timestamp=datetime.utcnow(),
                connection_status=data.get("connection_status"),
                signal_quality=data.get("signal_quality"),
                last_data_sync=data.get("last_data_sync"),
                error_count=data.get("error_count")
            )
            
            db.add(measurement)
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar medição do logger: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _update_system_status(self):
        """Atualizar status do sistema"""
        db = SessionLocal()
        try:
            import psutil
            
            status = SystemStatus(
                timestamp=datetime.utcnow(),
                inverter_connected=self.last_inverter_data is not None and 
                    (datetime.utcnow() - self.last_inverter_data).total_seconds() < 300,
                logger_connected=self.last_logger_data is not None and 
                    (datetime.utcnow() - self.last_logger_data).total_seconds() < 300,
                database_connected=True,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                last_inverter_data=self.last_inverter_data,
                last_logger_data=self.last_logger_data,
                last_alert_check=datetime.utcnow()
            )
            
            db.add(status)
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do sistema: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def check_inverter_connection(self) -> bool:
        """Verificar conectividade com o inversor"""
        try:
            if not await self.modbus_client.is_connected():
                await self.modbus_client.connect(
                    host=settings.INVERTER_HOST,
                    port=settings.INVERTER_PORT
                )
            
            # Tentar ler um registro simples
            test_value = await self.modbus_client.read_holding_register(
                0x0001,  # Potência de saída
                unit_id=settings.INVERTER_ADDRESS
            )
            return test_value is not None
            
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com inversor: {e}")
            return False
            
    async def check_logger_connection(self) -> bool:
        """Verificar conectividade com o logger"""
        try:
            if not await self.modbus_client.is_connected():
                await self.modbus_client.connect(
                    host=settings.LOGGER_HOST,
                    port=settings.LOGGER_PORT
                )
            
            # Tentar ler um registro simples
            test_value = await self.modbus_client.read_holding_register(
                0x0100,  # Status da conexão
                unit_id=settings.LOGGER_ADDRESS
            )
            return test_value is not None
            
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com logger: {e}")
            return False
            
    async def get_system_status(self) -> Dict[str, Any]:
        """Obter status completo do sistema"""
        return {
            "data_collector_running": self.running,
            "last_inverter_data": self.last_inverter_data,
            "last_logger_data": self.last_logger_data,
            "inverter_connected": await self.check_inverter_connection(),
            "logger_connected": await self.check_logger_connection(),
            "collection_interval": settings.DATA_COLLECTION_INTERVAL,
            "uptime": "calculado_em_background"
        }
