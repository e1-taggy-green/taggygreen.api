from sqlalchemy import Column, Integer, String, ForeignKey, Float
from .base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    event_type = Column(String) # 'toll', 'parking'
    co2_saved = Column(Float, default=0.0)
    time_saved = Column(Float, default=0.0)
    fuel_saved = Column(Float, default=0.0)
