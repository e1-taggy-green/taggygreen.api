import pytest
from src.schemas.esg import VehicleEmissionFactors
from src.services.esg_engine import ESGEngine


@pytest.fixture
def engine():
    return ESGEngine()


@pytest.fixture
def diesel_truck_factors():
    return VehicleEmissionFactors(
        emission_factor_kg_per_l=2.68,         # Ex: caminhão (kg CO2 / L diesel)
        idle_fuel_consumption_l_per_min=0.06,  # Ex: Consumo severo em marcha lenta 
        accel_brake_extra_fuel_l=0.15          # Queima extra na inércia de frenagem/arranque
    )


def test_cenario_1_caminhao_pesado_com_tag(engine, diesel_truck_factors):
    """
    Testa o Given/When/Then do Cenário 1:
    A engine deve retornar valores zerados para os 'multadores' (desperdícios) se o veículo tiver a tag.
    """
    result = engine.calculate_passagem(
        base_fuel_l=10.0,
        vehicle_factors=diesel_truck_factors,
        has_tag=True
    )
    
    assert result.has_tag is True
    assert result.waste_co2_kg == 0.0
    assert result.waste_fuel_l == 0.0
    assert result.paper_used == 0
    assert result.total_fuel_l == 10.0  # Sem adição de desperdício


def test_cenario_2_caminhao_pesado_sem_tag_comparativo(engine, diesel_truck_factors):
    """
    Testa o Given/When/Then do Cenário 2:
    A engine deve computar precisamente a diferença gerada pela ausência da tag e perdas ambientais.
    """
    savings = engine.calculate_savings(
        base_fuel_l=10.0,
        vehicle_factors=diesel_truck_factors,
        idle_time_min=3.0  # 3 Minutos na guarita
    )
    
    # Combustível desperdiçado = (3 min * 0.06) + 0.15 extra arranque = 0.33 L
    assert savings.fuel_saved_l == 0.33
    
    # CO2 desperdiçado = (0.33L * 2.68 kg_co2/L) + 0.005 kg do ticket = 0.8844 + 0.005 = 0.8894 kg
    assert savings.co2_saved_kg == 0.8894
    
    assert savings.paper_saved == 1
    assert savings.time_saved_min == 3.0
