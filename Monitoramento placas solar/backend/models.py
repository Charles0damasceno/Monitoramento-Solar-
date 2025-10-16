"""
Modelos de dados para o sistema de monitoramento solar
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Inverter(Base):
    """Modelo para dados do inversor"""
    __tablename__ = "inverters"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), unique=True, index=True)
    model = Column(String(100))
    rated_power = Column(Float)  # W
    mppt_count = Column(Integer)
    protocol_version = Column(String(20))
    firmware_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    measurements = relationship("InverterMeasurement", back_populates="inverter")
    alerts = relationship("Alert", back_populates="inverter")

class Logger(Base):
    """Modelo para dados do logger"""
    __tablename__ = "loggers"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), unique=True, index=True)
    model = Column(String(100))
    firmware_version = Column(String(20))
    system_version = Column(String(20))
    mac_address = Column(String(17))
    router_ssid = Column(String(50))
    signal_strength = Column(Integer)
    data_send_interval = Column(Integer)  # minutos
    data_log_interval = Column(Integer)   # segundos
    max_devices = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    measurements = relationship("LoggerMeasurement", back_populates="logger")
    alerts = relationship("Alert", back_populates="logger")

class InverterMeasurement(Base):
    """Medições do inversor"""
    __tablename__ = "inverter_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    inverter_id = Column(Integer, ForeignKey("inverters.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Dados de produção
    power_output = Column(Float)  # W
    energy_daily = Column(Float)  # kWh
    energy_total = Column(Float)  # kWh
    
    # Dados elétricos DC
    voltage_dc = Column(Float)    # V
    current_dc = Column(Float)    # A
    
    # Dados elétricos AC
    voltage_ac = Column(Float)    # V
    current_ac = Column(Float)    # A
    frequency = Column(Float)     # Hz
    
    # Dados ambientais
    temperature = Column(Float)   # °C
    efficiency = Column(Float)    # %
    
    # Status
    status_code = Column(Integer)
    fault_code = Column(Integer)
    uptime = Column(Integer)      # horas
    
    # Relacionamentos
    inverter = relationship("Inverter", back_populates="measurements")

class LoggerMeasurement(Base):
    """Medições do logger"""
    __tablename__ = "logger_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    logger_id = Column(Integer, ForeignKey("loggers.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Dados de comunicação
    connection_status = Column(Boolean)
    signal_quality = Column(Integer)
    last_data_sync = Column(DateTime)
    error_count = Column(Integer)
    
    # Dados de rede
    ip_address = Column(String(15))
    network_status = Column(String(20))
    
    # Relacionamentos
    logger = relationship("Logger", back_populates="measurements")

class Alert(Base):
    """Alertas do sistema"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    inverter_id = Column(Integer, ForeignKey("inverters.id"), nullable=True)
    logger_id = Column(Integer, ForeignKey("loggers.id"), nullable=True)
    
    alert_type = Column(String(50), index=True)
    severity = Column(String(20))  # low, medium, high, critical
    message = Column(Text)
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    inverter = relationship("Inverter", back_populates="alerts")
    logger = relationship("Logger", back_populates="alerts")

class SystemStatus(Base):
    """Status geral do sistema"""
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Status dos componentes
    inverter_connected = Column(Boolean)
    logger_connected = Column(Boolean)
    database_connected = Column(Boolean)
    
    # Métricas do sistema
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
    # Últimas atualizações
    last_inverter_data = Column(DateTime, nullable=True)
    last_logger_data = Column(DateTime, nullable=True)
    last_alert_check = Column(DateTime, nullable=True)

class DailySummary(Base):
    """Resumo diário de produção"""
    __tablename__ = "daily_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    inverter_id = Column(Integer, ForeignKey("inverters.id"))
    
    # Produção do dia
    total_energy = Column(Float)  # kWh
    peak_power = Column(Float)    # W
    average_power = Column(Float) # W
    
    # Eficiência
    peak_efficiency = Column(Float)  # %
    average_efficiency = Column(Float)  # %
    
    # Tempo de funcionamento
    operating_hours = Column(Float)
    downtime_hours = Column(Float)
    
    # Condições ambientais
    min_temperature = Column(Float)
    max_temperature = Column(Float)
    average_temperature = Column(Float)
    
    # Alertas
    alert_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    inverter = relationship("Inverter")

class Configuration(Base):
    """Configurações do sistema"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    category = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
