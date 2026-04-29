from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String, unique=True, index=True)
    name = Column(String)
    
    vehicles = relationship("Vehicle", back_populates="company")