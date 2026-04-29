from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class Passage(Base):
    __tablename__ = "passages"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    has_tag = Column(Boolean)
    base_fuel_l = Column(Float)
    idle_time_min = Column(Float)
    total_co2_kg = Column(Float)
    total_fuel_l = Column(Float)
    waste_co2_kg = Column(Float)
    waste_fuel_l = Column(Float)
    paper_used = Column(Integer)
    
    vehicle = relationship("Vehicle", back_populates="passages")