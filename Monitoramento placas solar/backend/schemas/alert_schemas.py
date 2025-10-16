"""
Schemas Pydantic para alertas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    inverter_id: Optional[int] = None
    logger_id: Optional[int] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None
    message: Optional[str] = None

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    resolved: bool
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AlertStatistics(BaseModel):
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    alerts_24h: int
    alerts_7d: int
    alerts_30d: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
