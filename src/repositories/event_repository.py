from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.models.event import Event
from src.models.vehicle import Vehicle
from src.models.user import User

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_events_by_user(self, user_id: int):
        return self.db.query(Event).join(Vehicle).filter(Vehicle.user_id == user_id).all()

    def get_total_co2_saved_by_user(self, user_id: int) -> float:
        # Soma todo o CO2 poupado pelo usuário (saldo de mitigação acumulada),
        # filtrando exclusivamente pelos eventos das placas atreladas ao userID.
        total = (
            self.db.query(func.sum(Event.co2_saved))
            .join(Vehicle, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .scalar()
        )
        return total or 0.0

    def get_monthly_savings_by_user(self, user_id: int, since: datetime):
        # Agrupa a economia (CO2, combustível e tempo) por mês a partir da data
        # de corte informada, considerando apenas os eventos do usuário (userID).
        mes = func.strftime("%Y-%m", Event.created_at)
        return (
            self.db.query(
                mes.label("mes"),
                func.sum(Event.co2_saved).label("co2_saved"),
                func.sum(Event.fuel_saved).label("fuel_saved"),
                func.sum(Event.time_saved).label("time_saved"),
            )
            .join(Vehicle, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id, Event.created_at >= since)
            .group_by(mes)
            .order_by(mes)
            .all()
        )

    def get_extrato_by_user(self, user_id: int, limit: int = 10):
        # Lista as últimas passagens (pedágio/estacionamento) das placas do usuário,
        # da mais recente para a mais antiga, para compor o extrato individual.
        return (
            self.db.query(
                Event.event_type,
                Event.created_at,
                Event.co2_saved,
            )
            .join(Vehicle, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .order_by(Event.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_aggregated_b2b_dashboard(self, email: str):
        resultado = self.db.query(
            func.sum(Event.co2_saved).label("co2_evitado_kg"),
            func.sum(Event.fuel_saved).label("combustivel_evitado_litros"),
            func.sum(Event.time_saved).label("tempo_economizado_minutos"),
            func.count(func.distinct(Vehicle.id)).label("frota_total")
        ).select_from(Event) \
         .join(Vehicle, Event.vehicle_id == Vehicle.id) \
         .join(User, Vehicle.user_id == User.id) \
         .filter(User.email == email, User.user_type == 'b2b').first()
        
        return resultado

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email, User.user_type == 'b2b').first()

    def get_performance_by_category(self, user_id: int):
        return (
            self.db.query(
                Vehicle.vehicle_type,
                func.sum(Event.co2_saved).label("total_co2"),
                func.sum(Event.fuel_saved).label("total_fuel")
            )
            .join(Event, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .group_by(Vehicle.vehicle_type)
            .all()
        )

    def get_fleet_ranking(self, user_id: int, limit: int = 5):
        return (
            self.db.query(
                Vehicle.license_plate,
                Vehicle.vehicle_type,
                func.sum(Event.co2_saved).label("total_co2"),
                func.count(Event.id).label("total_transacoes")
            )
            .join(Event, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .group_by(Vehicle.license_plate, Vehicle.vehicle_type)
            .order_by(desc("total_transacoes"), desc("total_co2"))
            .limit(limit)
            .all()
        )

    def get_raw_events_for_csv(self, user_id: int):
        return (
            self.db.query(
                Event.created_at,
                Vehicle.license_plate,
                Vehicle.vehicle_type,
                Event.co2_saved,
                Event.fuel_saved,
                Event.time_saved
            )
            .join(Vehicle, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .order_by(Event.created_at.desc())
            .all()
        )

