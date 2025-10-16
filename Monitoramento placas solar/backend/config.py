"""
Configurações do sistema de monitoramento solar
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Sistema de Monitoramento Solar"
    DEBUG: bool = False
    SECRET_KEY: str = "solar_monitoring_secret_key_2024"
    
    # Banco de dados
    DATABASE_URL: str = "sqlite:///./solar_monitoring.db"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Modbus - Inversor
    INVERTER_HOST: str = "192.168.1.100"
    INVERTER_PORT: int = 502
    INVERTER_ADDRESS: int = 1
    INVERTER_TIMEOUT: int = 5
    
    # Modbus - Logger
    LOGGER_HOST: str = "192.168.0.101"
    LOGGER_PORT: int = 502
    LOGGER_ADDRESS: int = 2
    LOGGER_TIMEOUT: int = 5
    
    # Coleta de dados
    DATA_COLLECTION_INTERVAL: int = 60  # segundos
    DATA_RETENTION_DAYS: int = 365
    
    # Alertas
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_SMTP_HOST: str = ""
    ALERT_EMAIL_SMTP_PORT: int = 587
    ALERT_EMAIL_USERNAME: str = ""
    ALERT_EMAIL_PASSWORD: str = ""
    ALERT_EMAIL_TO: List[str] = []
    
    # Thresholds para alertas
    LOW_PRODUCTION_THRESHOLD: float = 0.1  # 10% da potência nominal
    HIGH_TEMPERATURE_THRESHOLD: float = 70.0  # °C
    CONNECTION_TIMEOUT_THRESHOLD: int = 300  # segundos
    
    # API Externa (se disponível)
    EXTERNAL_API_URL: str = ""
    EXTERNAL_API_KEY: str = ""
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # segundos
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/solar_monitoring.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instância global das configurações
settings = Settings()

# Configurações específicas dos equipamentos
EQUIPMENT_CONFIG = {
    "inverter": {
        "serial_number": "2106027230",
        "model": "String Single Inverter",
        "rated_power": 3000,  # W
        "mppt_count": 1,
        "protocol_version": "V0.2.0.1",
        "modbus_registers": {
            # Registros Modbus para leitura de dados
            "power_output": 0x0001,      # Potência de saída (W)
            "energy_daily": 0x0002,      # Energia diária (kWh)
            "voltage_dc": 0x0003,        # Tensão DC (V)
            "current_dc": 0x0004,        # Corrente DC (A)
            "voltage_ac": 0x0005,        # Tensão AC (V)
            "current_ac": 0x0006,        # Corrente AC (A)
            "frequency": 0x0007,         # Frequência (Hz)
            "temperature": 0x0008,       # Temperatura (°C)
            "efficiency": 0x0009,        # Eficiência (%)
            "status": 0x000A,            # Status do inversor
            "fault_code": 0x000B,        # Código de falha
            "uptime": 0x000C,            # Tempo de funcionamento
        }
    },
    "logger": {
        "serial_number": "1782433145",
        "model": "LSW3_15_FFFF",
        "firmware_version": "1.0.9E",
        "system_version": "V1.1.00.10",
        "data_send_interval": 5,         # minutos
        "data_log_interval": 60,         # segundos
        "max_devices": 1,
        "signal_strength": 90,
        "mac_address": "34EAE7B8618E",
        "router_ssid": "NetPlus-Charles",
        "modbus_registers": {
            # Registros específicos do logger
            "connection_status": 0x0100, # Status da conexão
            "last_data_sync": 0x0101,    # Última sincronização
            "error_count": 0x0102,       # Contador de erros
            "signal_quality": 0x0103,    # Qualidade do sinal
        }
    }
}

# Configurações de alarmes
ALARM_CONFIG = {
    "low_production": {
        "enabled": True,
        "threshold": 300,  # W (10% de 3000W)
        "message": "Baixa produção de energia detectada"
    },
    "high_temperature": {
        "enabled": True,
        "threshold": 70.0,  # °C
        "message": "Temperatura elevada no inversor"
    },
    "communication_error": {
        "enabled": True,
        "timeout": 300,  # segundos
        "message": "Erro de comunicação com equipamento"
    },
    "fault_detected": {
        "enabled": True,
        "message": "Falha detectada no sistema"
    }
}
