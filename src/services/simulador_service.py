from src.services.esg_engine import ESGEngine
from src.core.enums import VehicleFactorsEnum
from src.schemas.simulador_schema import SimulacaoInput, SimulacaoOutput


class SimuladorService:
   

    def simular(self, payload: SimulacaoInput) -> SimulacaoOutput:
        # Reaproveita o motor de cálculo ESG já existente no projeto
        calculator = ESGEngine()

        # Tipo de evento fixo para o simulador (mesmo padrão usado no esg_engine.py)
        event_type = "toll"

        # Acumuladores mensais (motor retorna valores mensais pois 'occurrences' é mensal)
        co2_kg_mensal = 0.0
        combustivel_l_mensal = 0.0
        tempo_min_mensal = 0.0

        # Cálculo para a parcela de CARROS da frota hipotética
        if payload.qtd_carros > 0:
            resultado_carros = calculator.calculate_savings(
                vehicle_factors=VehicleFactorsEnum.CAR.value,
                vehicles_count=payload.qtd_carros,
                event_type=event_type,
                occurrences=payload.eventos_mensais_por_veiculo,
            )
            co2_kg_mensal += resultado_carros.co2_saved_kg
            combustivel_l_mensal += resultado_carros.fuel_saved_l
            tempo_min_mensal += resultado_carros.time_saved_min

        # Cálculo para a parcela de CAMINHÕES da frota hipotética
        if payload.qtd_caminhoes > 0:
            resultado_caminhoes = calculator.calculate_savings(
                vehicle_factors=VehicleFactorsEnum.TRUCK.value,
                vehicles_count=payload.qtd_caminhoes,
                event_type=event_type,
                occurrences=payload.eventos_mensais_por_veiculo,
            )
            co2_kg_mensal += resultado_caminhoes.co2_saved_kg
            combustivel_l_mensal += resultado_caminhoes.fuel_saved_l
            tempo_min_mensal += resultado_caminhoes.time_saved_min

        # Conversão de minutos para horas (mensal)
        tempo_horas_mensal = tempo_min_mensal / 60.0

        # Projeção anual = mensal * 12 meses
        co2_kg_anual = co2_kg_mensal * 12
        combustivel_l_anual = combustivel_l_mensal * 12
        tempo_horas_anual = tempo_horas_mensal * 12

        # Arredondamento final (mesmo padrão do esg_engine.py)
        return SimulacaoOutput(
            co2_mitigado_kg_mensal=round(co2_kg_mensal, 4),
            co2_mitigado_kg_anual=round(co2_kg_anual, 4),
            combustivel_economizado_l_mensal=round(combustivel_l_mensal, 4),
            combustivel_economizado_l_anual=round(combustivel_l_anual, 4),
            tempo_economizado_horas_mensal=round(tempo_horas_mensal, 4),
            tempo_economizado_horas_anual=round(tempo_horas_anual, 4),
        )
