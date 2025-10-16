"""
Schemas Pydantic para análises e relatórios
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ProductionAnalysis(BaseModel):
    period_days: int
    total_energy: float
    average_daily_energy: float
    peak_power: float
    average_power: float
    production_efficiency: float
    operating_hours: float
    best_day: Optional[str] = None
    worst_day: Optional[str] = None

class EfficiencyReport(BaseModel):
    period_days: int
    average_efficiency: float
    peak_efficiency: float
    min_efficiency: float
    efficiency_trend: str  # "improving", "declining", "stable"
    temperature_impact: float
    optimal_conditions: Optional[Dict[str, Any]] = None

class PerformanceComparison(BaseModel):
    period1: Dict[str, Any]
    period2: Dict[str, Any]
    comparison: Dict[str, float]

class ForecastData(BaseModel):
    forecast_days: int
    confidence: str  # "low", "medium", "high"
    predictions: List[Dict[str, Any]]
    methodology: str
