"""
Router para análises e relatórios
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from ..database import get_db
from ..models import InverterMeasurement, DailySummary, Alert
from ..schemas.analytics_schemas import (
    ProductionAnalysis,
    EfficiencyReport,
    PerformanceComparison,
    ForecastData
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/production-analysis", response_model=ProductionAnalysis)
async def get_production_analysis(
    days: int = Query(30, le=365),
    inverter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Análise detalhada da produção de energia"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(InverterMeasurement)
        if inverter_id:
            query = query.filter(InverterMeasurement.inverter_id == inverter_id)
        
        measurements = query\
            .filter(InverterMeasurement.timestamp >= start_date)\
            .order_by(InverterMeasurement.timestamp.asc())\
            .all()
        
        if not measurements:
            return ProductionAnalysis(
                period_days=days,
                total_energy=0,
                average_daily_energy=0,
                peak_power=0,
                average_power=0,
                production_efficiency=0,
                operating_hours=0,
                best_day=None,
                worst_day=None
            )
        
        # Converter para DataFrame para análise
        data = []
        for m in measurements:
            if m.power_output is not None and m.energy_daily is not None:
                data.append({
                    'timestamp': m.timestamp,
                    'power': m.power_output,
                    'energy': m.energy_daily,
                    'temperature': m.temperature or 0,
                    'efficiency': m.efficiency or 0
                })
        
        if not data:
            return ProductionAnalysis(
                period_days=days,
                total_energy=0,
                average_daily_energy=0,
                peak_power=0,
                average_power=0,
                production_efficiency=0,
                operating_hours=0,
                best_day=None,
                worst_day=None
            )
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Calcular métricas
        total_energy = df['energy'].max() - df['energy'].min()
        peak_power = df['power'].max()
        average_power = df['power'].mean()
        
        # Produção diária
        daily_production = df.groupby('date')['power'].agg(['max', 'mean', 'count']).reset_index()
        daily_production.columns = ['date', 'peak_power', 'avg_power', 'measurements']
        
        average_daily_energy = daily_production['peak_power'].mean()
        
        # Horas de funcionamento (assumindo que há produção quando power > 0)
        operating_hours = len(df[df['power'] > 0]) * 1  # Assumindo medições a cada minuto
        
        # Melhor e pior dia
        best_day = daily_production.loc[daily_production['peak_power'].idxmax(), 'date'].isoformat()
        worst_day = daily_production.loc[daily_production['peak_power'].idxmin(), 'date'].isoformat()
        
        # Eficiência de produção
        production_efficiency = (average_power / peak_power * 100) if peak_power > 0 else 0
        
        return ProductionAnalysis(
            period_days=days,
            total_energy=round(total_energy, 2),
            average_daily_energy=round(average_daily_energy, 2),
            peak_power=round(peak_power, 2),
            average_power=round(average_power, 2),
            production_efficiency=round(production_efficiency, 2),
            operating_hours=round(operating_hours / 60, 1),  # Converter para horas
            best_day=best_day,
            worst_day=worst_day
        )
        
    except Exception as e:
        logger.error(f"Erro na análise de produção: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/efficiency-report", response_model=EfficiencyReport)
async def get_efficiency_report(
    days: int = Query(30, le=365),
    inverter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Relatório de eficiência do sistema"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(InverterMeasurement)
        if inverter_id:
            query = query.filter(InverterMeasurement.inverter_id == inverter_id)
        
        measurements = query\
            .filter(InverterMeasurement.timestamp >= start_date)\
            .filter(InverterMeasurement.efficiency.isnot(None))\
            .order_by(InverterMeasurement.timestamp.asc())\
            .all()
        
        if not measurements:
            return EfficiencyReport(
                period_days=days,
                average_efficiency=0,
                peak_efficiency=0,
                min_efficiency=0,
                efficiency_trend="stable",
                temperature_impact=0,
                optimal_conditions=None
            )
        
        # Converter para DataFrame
        data = []
        for m in measurements:
            if m.efficiency is not None:
                data.append({
                    'timestamp': m.timestamp,
                    'efficiency': m.efficiency,
                    'temperature': m.temperature or 0,
                    'power': m.power_output or 0
                })
        
        df = pd.DataFrame(data)
        
        # Calcular métricas de eficiência
        average_efficiency = df['efficiency'].mean()
        peak_efficiency = df['efficiency'].max()
        min_efficiency = df['efficiency'].min()
        
        # Tendência de eficiência
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_efficiency = df.groupby('date')['efficiency'].mean()
        
        if len(daily_efficiency) > 7:
            # Calcular tendência dos últimos 7 dias
            recent_trend = daily_efficiency.tail(7)
            if len(recent_trend) > 1:
                trend_slope = np.polyfit(range(len(recent_trend)), recent_trend.values, 1)[0]
                if trend_slope > 0.5:
                    efficiency_trend = "improving"
                elif trend_slope < -0.5:
                    efficiency_trend = "declining"
                else:
                    efficiency_trend = "stable"
            else:
                efficiency_trend = "stable"
        else:
            efficiency_trend = "stable"
        
        # Impacto da temperatura na eficiência
        if len(df) > 10:
            correlation = df['efficiency'].corr(df['temperature'])
            temperature_impact = abs(correlation) * 100
        else:
            temperature_impact = 0
        
        # Condições ótimas
        optimal_temp_range = None
        if len(df) > 0:
            # Encontrar faixa de temperatura com melhor eficiência
            temp_bins = pd.cut(df['temperature'], bins=5)
            efficiency_by_temp = df.groupby(temp_bins)['efficiency'].mean()
            best_temp_bin = efficiency_by_temp.idxmax()
            if pd.notna(best_temp_bin):
                optimal_temp_range = {
                    "min_temp": best_temp_bin.left,
                    "max_temp": best_temp_bin.right,
                    "avg_efficiency": efficiency_by_temp[best_temp_bin]
                }
        
        return EfficiencyReport(
            period_days=days,
            average_efficiency=round(average_efficiency, 2),
            peak_efficiency=round(peak_efficiency, 2),
            min_efficiency=round(min_efficiency, 2),
            efficiency_trend=efficiency_trend,
            temperature_impact=round(temperature_impact, 2),
            optimal_conditions=optimal_temp_range
        )
        
    except Exception as e:
        logger.error(f"Erro no relatório de eficiência: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/performance-comparison", response_model=PerformanceComparison)
async def get_performance_comparison(
    period1_days: int = Query(30),
    period2_days: int = Query(30),
    inverter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Comparação de performance entre períodos"""
    try:
        now = datetime.utcnow()
        period1_start = now - timedelta(days=period1_days)
        period2_start = now - timedelta(days=period1_days + period2_days)
        period2_end = period1_start
        
        query = db.query(InverterMeasurement)
        if inverter_id:
            query = query.filter(InverterMeasurement.inverter_id == inverter_id)
        
        # Período 1 (mais recente)
        period1_data = query\
            .filter(InverterMeasurement.timestamp >= period1_start)\
            .filter(InverterMeasurement.timestamp < now)\
            .all()
        
        # Período 2 (anterior)
        period2_data = query\
            .filter(InverterMeasurement.timestamp >= period2_start)\
            .filter(InverterMeasurement.timestamp < period2_end)\
            .all()
        
        def calculate_metrics(measurements):
            if not measurements:
                return {
                    "total_energy": 0,
                    "average_power": 0,
                    "peak_power": 0,
                    "average_efficiency": 0,
                    "operating_hours": 0
                }
            
            power_values = [m.power_output for m in measurements if m.power_output is not None]
            efficiency_values = [m.efficiency for m in measurements if m.efficiency is not None]
            
            total_energy = max([m.energy_daily for m in measurements if m.energy_daily is not None], default=0)
            average_power = sum(power_values) / len(power_values) if power_values else 0
            peak_power = max(power_values) if power_values else 0
            average_efficiency = sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0
            operating_hours = len([m for m in measurements if m.power_output and m.power_output > 0]) / 60  # Assumindo medições por minuto
            
            return {
                "total_energy": round(total_energy, 2),
                "average_power": round(average_power, 2),
                "peak_power": round(peak_power, 2),
                "average_efficiency": round(average_efficiency, 2),
                "operating_hours": round(operating_hours, 1)
            }
        
        period1_metrics = calculate_metrics(period1_data)
        period2_metrics = calculate_metrics(period2_data)
        
        # Calcular diferenças percentuais
        def calculate_change(current, previous):
            if previous == 0:
                return 0 if current == 0 else 100
            return round(((current - previous) / previous) * 100, 2)
        
        return PerformanceComparison(
            period1={
                "days": period1_days,
                "start_date": period1_start.date().isoformat(),
                "end_date": now.date().isoformat(),
                **period1_metrics
            },
            period2={
                "days": period2_days,
                "start_date": period2_start.date().isoformat(),
                "end_date": period2_end.date().isoformat(),
                **period2_metrics
            },
            comparison={
                "energy_change": calculate_change(period1_metrics["total_energy"], period2_metrics["total_energy"]),
                "power_change": calculate_change(period1_metrics["average_power"], period2_metrics["average_power"]),
                "peak_power_change": calculate_change(period1_metrics["peak_power"], period2_metrics["peak_power"]),
                "efficiency_change": calculate_change(period1_metrics["average_efficiency"], period2_metrics["average_efficiency"]),
                "operating_hours_change": calculate_change(period1_metrics["operating_hours"], period2_metrics["operating_hours"])
            }
        )
        
    except Exception as e:
        logger.error(f"Erro na comparação de performance: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/forecast", response_model=ForecastData)
async def get_production_forecast(
    days_ahead: int = Query(7, le=30),
    inverter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Previsão de produção de energia"""
    try:
        # Obter dados históricos dos últimos 30 dias
        start_date = datetime.utcnow() - timedelta(days=30)
        
        query = db.query(InverterMeasurement)
        if inverter_id:
            query = query.filter(InverterMeasurement.inverter_id == inverter_id)
        
        measurements = query\
            .filter(InverterMeasurement.timestamp >= start_date)\
            .filter(InverterMeasurement.power_output.isnot(None))\
            .order_by(InverterMeasurement.timestamp.asc())\
            .all()
        
        if len(measurements) < 7:
            return ForecastData(
                forecast_days=days_ahead,
                confidence="low",
                predictions=[],
                methodology="insufficient_data"
            )
        
        # Converter para DataFrame
        data = []
        for m in measurements:
            data.append({
                'timestamp': m.timestamp,
                'power': m.power_output,
                'date': m.timestamp.date()
            })
        
        df = pd.DataFrame(data)
        
        # Calcular média diária histórica
        daily_avg = df.groupby('date')['power'].mean()
        
        # Previsão simples baseada na média dos últimos dias
        recent_avg = daily_avg.tail(7).mean()  # Últimos 7 dias
        
        # Gerar previsões
        predictions = []
        base_date = datetime.utcnow().date()
        
        for i in range(1, days_ahead + 1):
            forecast_date = base_date + timedelta(days=i)
            
            # Ajuste sazonal simples (assumindo variação de ±20%)
            seasonal_factor = 1.0
            if forecast_date.month in [12, 1, 2]:  # Verão no Brasil
                seasonal_factor = 1.2
            elif forecast_date.month in [6, 7, 8]:  # Inverno no Brasil
                seasonal_factor = 0.8
            
            predicted_power = recent_avg * seasonal_factor
            
            predictions.append({
                "date": forecast_date.isoformat(),
                "predicted_power": round(predicted_power, 2),
                "confidence": "medium" if len(measurements) > 14 else "low"
            })
        
        return ForecastData(
            forecast_days=days_ahead,
            confidence="medium" if len(measurements) > 14 else "low",
            predictions=predictions,
            methodology="historical_average_with_seasonal_adjustment"
        )
        
    except Exception as e:
        logger.error(f"Erro na previsão: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/roi-analysis")
async def get_roi_analysis(
    system_cost: float = Query(15000),  # Custo do sistema em reais
    energy_price: float = Query(0.65),  # Preço da energia em R$/kWh
    db: Session = Depends(get_db)
):
    """Análise de retorno sobre investimento (ROI)"""
    try:
        # Obter dados dos últimos 365 dias
        start_date = datetime.utcnow() - timedelta(days=365)
        
        measurements = db.query(InverterMeasurement)\
            .filter(InverterMeasurement.timestamp >= start_date)\
            .filter(InverterMeasurement.energy_daily.isnot(None))\
            .order_by(InverterMeasurement.timestamp.asc())\
            .all()
        
        if not measurements:
            return {
                "system_cost": system_cost,
                "energy_price": energy_price,
                "annual_production": 0,
                "annual_savings": 0,
                "payback_period_years": 0,
                "roi_10_years": 0,
                "lifetime_savings": 0
            }
        
        # Calcular produção anual
        total_energy = max([m.energy_daily for m in measurements if m.energy_daily is not None], default=0)
        annual_production = total_energy  # kWh
        
        # Calcular economia anual
        annual_savings = annual_production * energy_price
        
        # Calcular período de payback
        payback_period = system_cost / annual_savings if annual_savings > 0 else 0
        
        # Calcular ROI em 10 anos
        savings_10_years = annual_savings * 10
        roi_10_years = ((savings_10_years - system_cost) / system_cost) * 100 if system_cost > 0 else 0
        
        # Economia ao longo da vida útil (25 anos)
        lifetime_savings = annual_savings * 25 - system_cost
        
        return {
            "system_cost": system_cost,
            "energy_price": energy_price,
            "annual_production": round(annual_production, 2),
            "annual_savings": round(annual_savings, 2),
            "payback_period_years": round(payback_period, 1),
            "roi_10_years": round(roi_10_years, 1),
            "lifetime_savings": round(lifetime_savings, 2)
        }
        
    except Exception as e:
        logger.error(f"Erro na análise de ROI: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
