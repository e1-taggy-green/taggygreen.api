from src.schemas.esg_schema import ESGSavingResult
from src.core.enums import VehicleEmissionFactors


class ESGEngine:
    """
    O Coração Matemático ESG do TaggyGreen.
    Responsável por calcular a economia ambiental a partir de uma lógica de multiplicação
    direta de eventos, veículos e fatores de consumo estáticos.
    """

    def calculate_savings(
        self, 
        vehicle_factors: VehicleEmissionFactors,
        vehicles_count: int,
        event_type: str,
        occurrences: int
    ) -> ESGSavingResult:
        # Tempo base perdido na guarita por tipo de evento (ex: 2 mins pedágio, 3 mins estacionamento)
        time_saved_per_occurrence = 2.0 if event_type == 'toll' else 3.0
        
        total_time_saved_min = time_saved_per_occurrence * vehicles_count * occurrences

        # Combustível economizado = (Marcha lenta * Tempo parado) + Combustível da frenagem/arrancada
        fuel_saved_per_occurrence = (
            (vehicle_factors.idle_fuel_consumption_l_per_min * time_saved_per_occurrence) + 
            vehicle_factors.accel_brake_extra_fuel_l
        )
        total_fuel_saved_l = fuel_saved_per_occurrence * vehicles_count * occurrences
        
        # CO2 economizado = Combustível total economizado * Fator de emissão (kg/l)
        co2_saved_per_occurrence = fuel_saved_per_occurrence * vehicle_factors.emission_factor_kg_per_l
        total_co2_saved_kg = co2_saved_per_occurrence * vehicles_count * occurrences

        return ESGSavingResult(
            co2_saved_kg=round(total_co2_saved_kg, 4),
            fuel_saved_l=round(total_fuel_saved_l, 4),
            time_saved_min=round(total_time_saved_min, 4)
        )

