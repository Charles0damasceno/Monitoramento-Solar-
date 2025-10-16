"""
Router para operações relacionadas ao inversor
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import Inverter, InverterMeasurement, DailySummary
from ..schemas.inverter_schemas import (
    InverterResponse,
    InverterMeasurementResponse,
    DailySummaryResponse,
    InverterStatus
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[InverterResponse])
async def get_inverters(db: Session = Depends(get_db)):
    """Obter lista de todos os inversores"""
    try:
        inverters = db.query(Inverter).all()
        return inverters
    except Exception as e:
        logger.error(f"Erro ao obter inversores: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{inverter_id}", response_model=InverterResponse)
async def get_inverter(inverter_id: int, db: Session = Depends(get_db)):
    """Obter dados de um inversor específico"""
    try:
        inverter = db.query(Inverter).filter(Inverter.id == inverter_id).first()
        if not inverter:
            raise HTTPException(status_code=404, detail="Inversor não encontrado")
        return inverter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter inversor {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{inverter_id}/status", response_model=InverterStatus)
async def get_inverter_status(inverter_id: int, db: Session = Depends(get_db)):
    """Obter status atual do inversor"""
    try:
        inverter = db.query(Inverter).filter(Inverter.id == inverter_id).first()
        if not inverter:
            raise HTTPException(status_code=404, detail="Inversor não encontrado")
        
        # Obter última medição
        latest_measurement = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.inverter_id == inverter_id)\
            .order_by(InverterMeasurement.timestamp.desc())\
            .first()
        
        # Obter medição de 24h atrás para comparação
        yesterday = datetime.utcnow() - timedelta(days=1)
        yesterday_measurement = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.inverter_id == inverter_id)\
            .filter(InverterMeasurement.timestamp >= yesterday)\
            .order_by(InverterMeasurement.timestamp.asc())\
            .first()
        
        # Calcular energia do dia
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_energy = 0.0
        if latest_measurement and yesterday_measurement:
            daily_energy = latest_measurement.energy_daily - (yesterday_measurement.energy_daily or 0)
        
        # Determinar status de conexão
        is_online = False
        if latest_measurement:
            time_diff = datetime.utcnow() - latest_measurement.timestamp
            is_online = time_diff.total_seconds() < 300  # 5 minutos
        
        return InverterStatus(
            inverter_id=inverter.id,
            serial_number=inverter.serial_number,
            is_online=is_online,
            last_update=latest_measurement.timestamp if latest_measurement else None,
            current_power=latest_measurement.power_output if latest_measurement else 0.0,
            daily_energy=daily_energy,
            temperature=latest_measurement.temperature if latest_measurement else None,
            efficiency=latest_measurement.efficiency if latest_measurement else None,
            status_code=latest_measurement.status_code if latest_measurement else None,
            fault_code=latest_measurement.fault_code if latest_measurement else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do inversor {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{inverter_id}/measurements", response_model=List[InverterMeasurementResponse])
async def get_inverter_measurements(
    inverter_id: int,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Obter medições do inversor"""
    try:
        query = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.inverter_id == inverter_id)
        
        if start_time:
            query = query.filter(InverterMeasurement.timestamp >= start_time)
        if end_time:
            query = query.filter(InverterMeasurement.timestamp <= end_time)
        
        measurements = query\
            .order_by(InverterMeasurement.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return measurements
        
    except Exception as e:
        logger.error(f"Erro ao obter medições do inversor {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{inverter_id}/daily-summaries", response_model=List[DailySummaryResponse])
async def get_daily_summaries(
    inverter_id: int,
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Obter resumos diários do inversor"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        summaries = db.query(DailySummary)\
            .filter(DailySummary.inverter_id == inverter_id)\
            .filter(DailySummary.date >= start_date)\
            .order_by(DailySummary.date.desc())\
            .all()
        
        return summaries
        
    except Exception as e:
        logger.error(f"Erro ao obter resumos diários do inversor {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{inverter_id}/current-production")
async def get_current_production(inverter_id: int, db: Session = Depends(get_db)):
    """Obter produção atual do inversor"""
    try:
        # Obter última medição
        latest_measurement = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.inverter_id == inverter_id)\
            .order_by(InverterMeasurement.timestamp.desc())\
            .first()
        
        if not latest_measurement:
            return {
                "inverter_id": inverter_id,
                "timestamp": None,
                "power_output": 0.0,
                "energy_daily": 0.0,
                "efficiency": 0.0,
                "temperature": None,
                "status": "no_data"
            }
        
        return {
            "inverter_id": inverter_id,
            "timestamp": latest_measurement.timestamp,
            "power_output": latest_measurement.power_output or 0.0,
            "energy_daily": latest_measurement.energy_daily or 0.0,
            "efficiency": latest_measurement.efficiency or 0.0,
            "temperature": latest_measurement.temperature,
            "status": "online" if latest_measurement.status_code == 1 else "offline"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter produção atual do inversor {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
