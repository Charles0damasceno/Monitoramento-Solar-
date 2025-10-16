"""
Schemas Pydantic para dados e medições
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MeasurementResponse(BaseModel):
    id: int
    timestamp: datetime
    
    # Dados de produção (inversor)
    power_output: Optional[float] = None
    energy_daily: Optional[float] = None
    energy_total: Optional[float] = None
    
    # Dados elétricos DC
    voltage_dc: Optional[float] = None
    current_dc: Optional[float] = None
    
    # Dados elétricos AC
    voltage_ac: Optional[float] = None
    current_ac: Optional[float] = None
    frequency: Optional[float] = None
    
    # Dados ambientais
    temperature: Optional[float] = None
    efficiency: Optional[float] = None
    
    # Status
    status_code: Optional[int] = None
    fault_code: Optional[int] = None
    uptime: Optional[int] = None
    
    class Config:
        from_attributes = True

class DailySummaryResponse(BaseModel):
    id: int
    date: datetime
    inverter_id: int
    
    # Produção do dia
    total_energy: Optional[float] = None
    peak_power: Optional[float] = None
    average_power: Optional[float] = None
    
    # Eficiência
    peak_efficiency: Optional[float] = None
    average_efficiency: Optional[float] = None
    
    # Tempo de funcionamento
    operating_hours: Optional[float] = None
    downtime_hours: Optional[float] = None
    
    # Condições ambientais
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    average_temperature: Optional[float] = None
    
    # Alertas
    alert_count: int = 0
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class DataStatistics(BaseModel):
    period_days: int
    total_measurements: int
    
    power: dict
    energy: dict
    temperature: dict
    efficiency: dict
    
    class Config:
        from_attributes = True
