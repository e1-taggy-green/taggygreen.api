from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String) # 'car', 'truck', etc.

    # --- Campos para o Motor ESG (B2B) ---
    emission_factor_kg_per_l = Column(Float)
    idle_fuel_consumption_l_per_min = Column(Float)
    accel_brake_extra_fuel_l = Column(Float)

    # --- Relacionamentos (B2C e B2B) ---
    # Um veículo pode pertencer a um usuário (B2C) OU a uma empresa (B2B)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # O Alembic precisa que o model User exista para criar a FK.
    # user = relationship("User", back_populates="vehicles")
    company = relationship("Company", back_populates="vehicles")
    passages = relationship("Passage", back_populates="vehicle")
