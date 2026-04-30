from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field

class VehicleTypeEnum(str, Enum):
    """Tipos de veículos aceitos pelo contrato da API"""
    CAR = "car"
    TRUCK = "truck"

@dataclass
class VehicleEmissionFactors:
    """Estrutura interna de dados para o motor de cálculo (Não é mais um Schema do Pydantic)"""
    emission_factor_kg_per_l: float
    idle_fuel_consumption_l_per_min: float
    accel_brake_extra_fuel_l: float

class VehicleFactorsEnum(Enum):
    """Constantes de fatores de consumo definidas diretamente no código"""
    CAR = VehicleEmissionFactors(2.30, 0.02, 0.05)
    TRUCK = VehicleEmissionFactors(2.68, 0.06, 0.15)

class ESGSavingResult(BaseModel):
    """
    Resultado final de economia (O Rastro Verde).
    """
    co2_saved_kg: float
    fuel_saved_l: float
    time_saved_min: float


class CalculateSavingsRequest(BaseModel):
    """Contrato de entrada (Payload) esperado do Frontend na requisição POST"""
    vehicle_type: VehicleTypeEnum = Field(..., description="Tipo do veículo (car ou truck)")
    vehicles_count: int = Field(1, description="Quantidade de veículos", ge=1)
    event_type: str = Field("toll", description="Tipo de evento (toll ou parking)")
    occurrences: int = Field(1, description="Quantidade de ocorrências desse evento", ge=1)
