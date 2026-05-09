from pydantic import BaseModel, Field
from src.core.enums import VehicleTypeEnum

class ESGSavingResult(BaseModel):
    """
    Resultado final de economia (O Rastro Verde).
    """
    co2_saved_kg: float
    fuel_saved_l: float
    time_saved_min: float


class CalculateSavingsRequest(BaseModel):
    """Contrato de entrada (Payload) esperado do Frontend na requisição POST do Simulador Utilitário"""
    vehicle_type: VehicleTypeEnum = Field(..., description="Tipo do veículo (car ou truck)")
    vehicles_count: int = Field(1, description="Quantidade de veículos", ge=1)
    event_type: str = Field("toll", description="Tipo de evento (toll ou parking)")
    occurrences: int = Field(1, description="Quantidade de ocorrências desse evento", ge=1)
