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


def test_calculo_economia_pedagio_simples(engine, diesel_truck_factors):
    """
    Testa o cálculo para 1 caminhão em 1 ocorrência de pedágio (2 minutos).
    """
    savings = engine.calculate_savings(
        vehicle_factors=diesel_truck_factors,
        vehicles_count=1,
        event_type='toll',
        occurrences=1
    )
    
    # Combustível economizado = (0.06 L/min * 2 min) + 0.15 L = 0.27 L
    assert savings.fuel_saved_l == 0.27
    
    # CO2 economizado = 0.27 L * 2.68 kg/L = 0.7236 kg
    assert savings.co2_saved_kg == 0.7236
    
    assert savings.time_saved_min == 2.0


def test_calculo_economia_estacionamento_multiplos_veiculos(engine, diesel_truck_factors):
    """
    Testa o cálculo multiplicativo para 5 caminhões com 2 ocorrências de estacionamento (3 minutos).
    """
    savings = engine.calculate_savings(
        vehicle_factors=diesel_truck_factors,
        vehicles_count=5,
        event_type='parking',
        occurrences=2
    )
    
    # Combustível por ocorrência = (0.06 * 3 min) + 0.15 = 0.33 L
    # Combustível Total = 0.33 L * 5 veículos * 2 ocorrências = 3.3 L
    assert savings.fuel_saved_l == 3.3
    
    # CO2 Total = 3.3 L * 2.68 kg/L = 8.844 kg
    assert savings.co2_saved_kg == 8.844
    
    # Tempo Total = 3 min * 5 veículos * 2 ocorrências = 30.0 min
    assert savings.time_saved_min == 30.0
