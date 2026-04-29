from pydantic import BaseModel, Field


class VehicleEmissionFactors(BaseModel):
    """
    Fatores de emissão isolados.
    No futuro (CH-02), esses dados virão do banco de dados dependendo da placa/tipo do veículo.
    """
    emission_factor_kg_per_l: float = Field(..., description="Fator de emissão kg CO2 por litro de combustível")
    idle_fuel_consumption_l_per_min: float = Field(..., description="Consumo de combustível em marcha lenta (litros/min)")
    accel_brake_extra_fuel_l: float = Field(..., description="Combustível extra consumido na frenagem e aceleração na guarita (litros)")


class EnvironmentFactors(BaseModel):
    """Valores globais de impacto ambiental"""
    paper_ticket_co2_kg: float = Field(0.005, description="Emissão de CO2 média por produção e descarte de ticket de papel (kg)")


class PassagemResult(BaseModel):
    """Resultado do cálculo do motor para um evento específico de pedágio/estacionamento"""
    has_tag: bool
    total_co2_kg: float
    total_fuel_l: float
    waste_co2_kg: float
    waste_fuel_l: float
    paper_used: int


class ESGSavingResult(BaseModel):
    """
    Resultado final comparativo de economia (O Rastro Verde).
    Representa: (Emissões Sem Tag) - (Emissões Com Tag)
    """
    co2_saved_kg: float
    fuel_saved_l: float
    time_saved_min: float
    paper_saved: int


class CalculateSavingsRequest(BaseModel):
    """Payload esperado no corpo da requisição (POST) para testar o cálculo"""
    base_fuel_l: float = Field(..., description="Litragem base gasta no trajeto", json_schema_extra={"example": 10.0})
    idle_time_min: float = Field(2.0, description="Tempo médio em minutos parado na guarita sem tag", json_schema_extra={"example": 3.0})
    vehicle_factors: VehicleEmissionFactors
