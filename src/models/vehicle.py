from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String) # 'car', 'truck', etc.
