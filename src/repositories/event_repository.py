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
                func.sum(Event.co2_saved).label("total_co2"),
                func.count(Event.id).label("total_transacoes")
            )
            .join(Event, Event.vehicle_id == Vehicle.id)
            .filter(Vehicle.user_id == user_id)
            .group_by(Vehicle.license_plate)
            .order_by(desc("total_transacoes"), desc("total_co2"))
            .limit(limit)
            .all()
        )
