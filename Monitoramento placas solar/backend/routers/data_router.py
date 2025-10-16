"""
Router para operações de dados e medições
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import InverterMeasurement, LoggerMeasurement, DailySummary
from ..schemas.data_schemas import (
    MeasurementResponse,
    DailySummaryResponse,
    DataStatistics
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/measurements", response_model=List[MeasurementResponse])
async def get_measurements(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    equipment_type: Optional[str] = Query(None),  # "inverter" ou "logger"
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Obter medições dos equipamentos"""
    try:
        if equipment_type == "inverter":
            query = db.query(InverterMeasurement)
        elif equipment_type == "logger":
            query = db.query(LoggerMeasurement)
        else:
            # Retornar ambos os tipos (implementação simplificada)
            query = db.query(InverterMeasurement)
        
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
        logger.error(f"Erro ao obter medições: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/current", response_model=MeasurementResponse)
async def get_current_measurement(
    equipment_type: str = Query("inverter"),
    db: Session = Depends(get_db)
):
    """Obter medição atual dos equipamentos"""
    try:
        if equipment_type == "inverter":
            measurement = db.query(InverterMeasurement)\
                .order_by(InverterMeasurement.timestamp.desc())\
                .first()
        elif equipment_type == "logger":
            measurement = db.query(LoggerMeasurement)\
                .order_by(LoggerMeasurement.timestamp.desc())\
                .first()
        else:
            raise HTTPException(status_code=400, detail="Tipo de equipamento inválido")
        
        if not measurement:
            raise HTTPException(status_code=404, detail="Nenhuma medição encontrada")
        
        return measurement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter medição atual: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/daily-summaries", response_model=List[DailySummaryResponse])
async def get_daily_summaries(
    days: int = Query(30, le=365),
    inverter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obter resumos diários"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(DailySummary)\
            .filter(DailySummary.date >= start_date)
        
        if inverter_id:
            query = query.filter(DailySummary.inverter_id == inverter_id)
        
        summaries = query\
            .order_by(DailySummary.date.desc())\
            .all()
        
        return summaries
        
    except Exception as e:
        logger.error(f"Erro ao obter resumos diários: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/statistics", response_model=DataStatistics)
async def get_data_statistics(
    days: int = Query(30, le=365),
    db: Session = Depends(get_db)
):
    """Obter estatísticas dos dados"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Estatísticas do inversor
        inverter_measurements = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.timestamp >= start_date)\
            .all()
        
        if inverter_measurements:
            power_values = [m.power_output for m in inverter_measurements if m.power_output is not None]
            energy_values = [m.energy_daily for m in inverter_measurements if m.energy_daily is not None]
            temp_values = [m.temperature for m in inverter_measurements if m.temperature is not None]
            efficiency_values = [m.efficiency for m in inverter_measurements if m.efficiency is not None]
            
            stats = {
                "period_days": days,
                "total_measurements": len(inverter_measurements),
                "power": {
                    "max": max(power_values) if power_values else 0,
                    "min": min(power_values) if power_values else 0,
                    "avg": sum(power_values) / len(power_values) if power_values else 0
                },
                "energy": {
                    "max": max(energy_values) if energy_values else 0,
                    "min": min(energy_values) if energy_values else 0,
                    "avg": sum(energy_values) / len(energy_values) if energy_values else 0
                },
                "temperature": {
                    "max": max(temp_values) if temp_values else 0,
                    "min": min(temp_values) if temp_values else 0,
                    "avg": sum(temp_values) / len(temp_values) if temp_values else 0
                },
                "efficiency": {
                    "max": max(efficiency_values) if efficiency_values else 0,
                    "min": min(efficiency_values) if efficiency_values else 0,
                    "avg": sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0
                }
            }
        else:
            stats = {
                "period_days": days,
                "total_measurements": 0,
                "power": {"max": 0, "min": 0, "avg": 0},
                "energy": {"max": 0, "min": 0, "avg": 0},
                "temperature": {"max": 0, "min": 0, "avg": 0},
                "efficiency": {"max": 0, "min": 0, "avg": 0}
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/export")
async def export_data(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    format: str = Query("csv"),
    db: Session = Depends(get_db)
):
    """Exportar dados para arquivo"""
    try:
        # Implementar exportação de dados
        # Por enquanto, retornar dados em JSON
        query = db.query(InverterMeasurement)
        
        if start_time:
            query = query.filter(InverterMeasurement.timestamp >= start_time)
        if end_time:
            query = query.filter(InverterMeasurement.timestamp <= end_time)
        
        measurements = query\
            .order_by(InverterMeasurement.timestamp.desc())\
            .all()
        
        # Converter para formato de exportação
        export_data = []
        for measurement in measurements:
            export_data.append({
                "timestamp": measurement.timestamp.isoformat(),
                "power_output": measurement.power_output,
                "energy_daily": measurement.energy_daily,
                "voltage_dc": measurement.voltage_dc,
                "current_dc": measurement.current_dc,
                "voltage_ac": measurement.voltage_ac,
                "current_ac": measurement.current_ac,
                "frequency": measurement.frequency,
                "temperature": measurement.temperature,
                "efficiency": measurement.efficiency,
                "status_code": measurement.status_code,
                "fault_code": measurement.fault_code
            })
        
        return {
            "format": format,
            "count": len(export_data),
            "data": export_data
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
