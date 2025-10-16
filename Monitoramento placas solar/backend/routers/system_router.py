"""
Router para operações do sistema
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging
import psutil
import platform

from ..database import get_db
from ..models import SystemStatus

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
async def get_system_status():
    """Obter status detalhado do sistema"""
    try:
        # Informações do sistema
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node()
        }
        
        # Uso de recursos
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            }
        }
        
        # Informações de rede
        network_info = {}
        try:
            net_io = psutil.net_io_counters()
            network_info = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception as e:
            logger.warning(f"Erro ao obter informações de rede: {e}")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_info,
            "resources": resources,
            "network": network_info,
            "uptime": "calculado_em_background"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        # Verificar componentes críticos
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy",
                "modbus_connection": "unknown",
                "data_collection": "unknown"
            }
        }
        
        # Verificar banco de dados
        try:
            db = next(get_db())
            # Tentar uma query simples
            db.execute("SELECT 1")
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
            logger.error(f"Banco de dados não está saudável: {e}")
        
        # Verificar uso de recursos
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 90:
            health_status["status"] = "degraded"
            health_status["warnings"] = health_status.get("warnings", [])
            health_status["warnings"].append("CPU usage high")
            
        if memory_percent > 90:
            health_status["status"] = "degraded"
            health_status["warnings"] = health_status.get("warnings", [])
            health_status["warnings"].append("Memory usage high")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        raise HTTPException(status_code=503, detail="Sistema indisponível")

@router.get("/configuration")
async def get_system_configuration():
    """Obter configurações do sistema"""
    try:
        from ..config import settings, EQUIPMENT_CONFIG, ALARM_CONFIG
        
        # Configurações que podem ser expostas (sem informações sensíveis)
        config = {
            "application": {
                "name": settings.APP_NAME,
                "debug": settings.DEBUG,
                "data_collection_interval": settings.DATA_COLLECTION_INTERVAL,
                "data_retention_days": settings.DATA_RETENTION_DAYS
            },
            "equipment": {
                "inverter": {
                    "serial_number": EQUIPMENT_CONFIG["inverter"]["serial_number"],
                    "model": EQUIPMENT_CONFIG["inverter"]["model"],
                    "rated_power": EQUIPMENT_CONFIG["inverter"]["rated_power"],
                    "mppt_count": EQUIPMENT_CONFIG["inverter"]["mppt_count"]
                },
                "logger": {
                    "serial_number": EQUIPMENT_CONFIG["logger"]["serial_number"],
                    "model": EQUIPMENT_CONFIG["logger"]["model"],
                    "firmware_version": EQUIPMENT_CONFIG["logger"]["firmware_version"]
                }
            },
            "modbus": {
                "inverter_host": settings.INVERTER_HOST,
                "inverter_port": settings.INVERTER_PORT,
                "logger_host": settings.LOGGER_HOST,
                "logger_port": settings.LOGGER_PORT,
                "timeout": settings.INVERTER_TIMEOUT
            },
            "alerts": {
                "low_production_threshold": ALARM_CONFIG["low_production"]["threshold"],
                "high_temperature_threshold": ALARM_CONFIG["high_temperature"]["threshold"],
                "connection_timeout_threshold": ALARM_CONFIG["communication_error"]["timeout"]
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/restart-data-collection")
async def restart_data_collection():
    """Reiniciar coleta de dados"""
    try:
        # Esta funcionalidade seria implementada para reiniciar o serviço de coleta
        # Por enquanto, apenas retorna uma mensagem
        return {
            "message": "Comando para reiniciar coleta de dados enviado",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erro ao reiniciar coleta de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/logs")
async def get_system_logs(lines: int = 100):
    """Obter logs do sistema"""
    try:
        import os
        from ..config import settings
        
        log_file = settings.LOG_FILE
        
        if not os.path.exists(log_file):
            return {
                "message": "Arquivo de log não encontrado",
                "logs": []
            }
        
        # Ler as últimas linhas do arquivo de log
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "log_file": log_file,
            "lines": len(recent_lines),
            "logs": [line.strip() for line in recent_lines]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/backup")
async def create_backup():
    """Criar backup dos dados"""
    try:
        # Implementar lógica de backup
        # Por enquanto, apenas retorna uma mensagem
        return {
            "message": "Backup iniciado",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
