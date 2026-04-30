from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from src.database.session import get_db
from src.models.event import Event

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard B2B"]
)

class DashboardMetrics(BaseModel):
    total_events: int
    total_co2_saved_kg: float
    total_fuel_saved_l: float
    total_time_saved_min: float

@router.get("/metrics", response_model=DashboardMetrics, summary="Obtém as métricas de economia agregadas (B2C)")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Lê os dados de eventos do banco de dados e realiza somatórias (agregações)
    para alimentar os gráficos do painel de usuário (B2C).
    """
    metrics = db.query(
        func.count(Event.id),
        func.sum(Event.co2_saved),
        func.sum(Event.fuel_saved),
        func.sum(Event.time_saved)
    ).one()

    total_events, total_co2, total_fuel, total_time = metrics

    return DashboardMetrics(
        total_events=total_events or 0,
        total_co2_saved_kg=round(total_co2 or 0.0, 2),
        total_fuel_saved_l=round(total_fuel or 0.0, 2),
        total_time_saved_min=round(total_time or 0.0, 2)
    )
