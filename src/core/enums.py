from enum import Enum
from dataclasses import dataclass

class VehicleTypeEnum(str, Enum):
    """Tipos de veículos aceitos pelo contrato da API e globalmente no sistema"""
    CAR = "car"
    TRUCK = "truck"

@dataclass
class VehicleEmissionFactors:
    """Estrutura interna de dados físicos para cálculo de emissão"""
    emission_factor_kg_per_l: float
    idle_fuel_consumption_l_per_min: float
    accel_brake_extra_fuel_l: float

class VehicleFactorsEnum(Enum):
    """Constantes de fatores de consumo por tipo de veículo"""
    CAR = VehicleEmissionFactors(2.30, 0.02, 0.05)
    TRUCK = VehicleEmissionFactors(2.68, 0.06, 0.15)
