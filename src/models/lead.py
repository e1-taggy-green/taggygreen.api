from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    
    # Parâmetros da frota na simulação
    qtd_carros = Column(Integer, nullable=False, default=0)
    qtd_caminhoes = Column(Integer, nullable=False, default=0)
    eventos_pedagio_carros = Column(Integer, nullable=False, default=0)
    eventos_estacionamento_carros = Column(Integer, nullable=False, default=0)
    eventos_pedagio_caminhoes = Column(Integer, nullable=False, default=0)
    eventos_estacionamento_caminhoes = Column(Integer, nullable=False, default=0)
    
    # Resultados calculados da projeção
    economia_co2_kg = Column(Float, nullable=False)
    economia_gasolina_litros = Column(Float, nullable=False)
    economia_tempo_minutos = Column(Float, nullable=False)
    dinheiro_economizado = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), index=True)
