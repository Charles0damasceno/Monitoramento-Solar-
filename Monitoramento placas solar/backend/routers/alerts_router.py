"""
Router para operações de alertas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import Alert, Inverter, Logger
from ..schemas.alert_schemas import (
    AlertResponse,
    AlertCreate,
    AlertStatistics,
    AlertUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    active_only: bool = Query(False),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Obter lista de alertas"""
    try:
        query = db.query(Alert)
        
        if active_only:
            query = query.filter(Alert.resolved == False)
        
        if severity:
            query = query.filter(Alert.severity == severity)
            
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        alerts = query\
            .order_by(Alert.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return alerts
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(db: Session = Depends(get_db)):
    """Obter alertas ativos"""
    try:
        alerts = db.query(Alert)\
            .filter(Alert.resolved == False)\
            .order_by(Alert.timestamp.desc())\
            .all()
        
        return alerts
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas ativos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Obter alerta específico"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter alerta {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/", response_model=AlertResponse)
async def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    """Criar novo alerta"""
    try:
        alert = Alert(
            inverter_id=alert_data.inverter_id,
            logger_id=alert_data.logger_id,
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            message=alert_data.message,
            value=alert_data.value,
            threshold=alert_data.threshold,
            timestamp=datetime.utcnow()
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alerta criado: {alert.alert_type} - {alert.message}")
        return alert
        
    except Exception as e:
        logger.error(f"Erro ao criar alerta: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: int, alert_update: AlertUpdate, db: Session = Depends(get_db)):
    """Atualizar alerta"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        # Atualizar campos fornecidos
        if alert_update.acknowledged is not None:
            alert.acknowledged = alert_update.acknowledged
            if alert_update.acknowledged:
                alert.acknowledged_at = datetime.utcnow()
        
        if alert_update.resolved is not None:
            alert.resolved = alert_update.resolved
            if alert_update.resolved:
                alert.resolved_at = datetime.utcnow()
        
        if alert_update.message is not None:
            alert.message = alert_update.message
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alerta {alert_id} atualizado")
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar alerta {alert_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Reconhecer alerta"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Alerta {alert_id} reconhecido")
        return {"message": "Alerta reconhecido com sucesso", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reconhecer alerta {alert_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolver alerta"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Alerta {alert_id} resolvido")
        return {"message": "Alerta resolvido com sucesso", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Deletar alerta"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        db.delete(alert)
        db.commit()
        
        logger.info(f"Alerta {alert_id} deletado")
        return {"message": "Alerta deletado com sucesso", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar alerta {alert_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/statistics/overview", response_model=AlertStatistics)
async def get_alert_statistics(db: Session = Depends(get_db)):
    """Obter estatísticas de alertas"""
    try:
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Contadores gerais
        total_alerts = db.query(Alert).count()
        active_alerts = db.query(Alert).filter(Alert.resolved == False).count()
        acknowledged_alerts = db.query(Alert).filter(Alert.acknowledged == True).count()
        resolved_alerts = db.query(Alert).filter(Alert.resolved == True).count()
        
        # Contadores por período
        alerts_24h = db.query(Alert).filter(Alert.timestamp >= last_24h).count()
        alerts_7d = db.query(Alert).filter(Alert.timestamp >= last_7d).count()
        alerts_30d = db.query(Alert).filter(Alert.timestamp >= last_30d).count()
        
        # Contadores por severidade
        critical_alerts = db.query(Alert).filter(
            Alert.severity == "critical", 
            Alert.resolved == False
        ).count()
        high_alerts = db.query(Alert).filter(
            Alert.severity == "high", 
            Alert.resolved == False
        ).count()
        medium_alerts = db.query(Alert).filter(
            Alert.severity == "medium", 
            Alert.resolved == False
        ).count()
        low_alerts = db.query(Alert).filter(
            Alert.severity == "low", 
            Alert.resolved == False
        ).count()
        
        # Contadores por tipo
        alert_types = db.query(Alert.alert_type).distinct().all()
        alerts_by_type = {}
        for alert_type in alert_types:
            count = db.query(Alert).filter(
                Alert.alert_type == alert_type[0],
                Alert.resolved == False
            ).count()
            alerts_by_type[alert_type[0]] = count
        
        return AlertStatistics(
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            acknowledged_alerts=acknowledged_alerts,
            resolved_alerts=resolved_alerts,
            alerts_24h=alerts_24h,
            alerts_7d=alerts_7d,
            alerts_30d=alerts_30d,
            by_severity={
                "critical": critical_alerts,
                "high": high_alerts,
                "medium": medium_alerts,
                "low": low_alerts
            },
            by_type=alerts_by_type
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de alertas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/types/list")
async def get_alert_types():
    """Obter lista de tipos de alerta disponíveis"""
    try:
        from ..config import ALARM_CONFIG
        
        alert_types = []
        for alert_type, config in ALARM_CONFIG.items():
            alert_types.append({
                "type": alert_type,
                "enabled": config.get("enabled", True),
                "description": config.get("message", ""),
                "threshold": config.get("threshold"),
                "timeout": config.get("timeout")
            })
        
        return {
            "alert_types": alert_types,
            "severity_levels": ["low", "medium", "high", "critical"]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter tipos de alerta: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
