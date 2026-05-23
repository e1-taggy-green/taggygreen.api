from sqlalchemy.orm import Session
from src.services.esg_engine import ESGEngine
from src.core.enums import VehicleFactorsEnum
from src.schemas.simulador_schema import SimulacaoRequest, SimulacaoResponse
from src.services.fuel_service import FuelPriceService
from src.services.b2b_service import B2BDashboardService
from src.repositories.lead_repository import LeadRepository


class SimuladorService:
    """Serviço responsável por realizar a projeção matemática de impacto para Leads."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.calculator = ESGEngine()
        self.fuel_price_service = FuelPriceService()
        self.repository = LeadRepository(db)

    def calculate_lead_projection(self, data: SimulacaoRequest) -> SimulacaoResponse:
        """
        Calcula a projeção de economia física (CO2, gasolina, tempo) e financeira
        acumulando eventos de pedágios e estacionamentos específicos para carros e caminhões,
        e persiste as informações no banco de dados.
        """
        co2_saved = 0.0
        fuel_saved = 0.0
        time_saved_min = 0.0

        # Parcela de CARROS
        if data.frota.qtd_carros > 0:
            # Pedágios (Toll)
            if data.frota.eventos_pedagio_carros > 0:
                res_toll = self.calculator.calculate_savings(
                    vehicle_factors=VehicleFactorsEnum.CAR.value,
                    vehicles_count=data.frota.qtd_carros,
                    event_type="toll",
                    occurrences=data.frota.eventos_pedagio_carros,
                )
                co2_saved += res_toll.co2_saved_kg
                fuel_saved += res_toll.fuel_saved_l
                time_saved_min += res_toll.time_saved_min

            # Estacionamentos (Parking)
            if data.frota.eventos_estacionamento_carros > 0:
                res_park = self.calculator.calculate_savings(
                    vehicle_factors=VehicleFactorsEnum.CAR.value,
                    vehicles_count=data.frota.qtd_carros,
                    event_type="parking",
                    occurrences=data.frota.eventos_estacionamento_carros,
                )
                co2_saved += res_park.co2_saved_kg
                fuel_saved += res_park.fuel_saved_l
                time_saved_min += res_park.time_saved_min

        # Parcela de CAMINHÕES
        if data.frota.qtd_caminhoes > 0:
            # Pedágios (Toll)
            if data.frota.eventos_pedagio_caminhoes > 0:
                res_toll = self.calculator.calculate_savings(
                    vehicle_factors=VehicleFactorsEnum.TRUCK.value,
                    vehicles_count=data.frota.qtd_caminhoes,
                    event_type="toll",
                    occurrences=data.frota.eventos_pedagio_caminhoes,
                )
                co2_saved += res_toll.co2_saved_kg
                fuel_saved += res_toll.fuel_saved_l
                time_saved_min += res_toll.time_saved_min

            # Estacionamentos (Parking)
            if data.frota.eventos_estacionamento_caminhoes > 0:
                res_park = self.calculator.calculate_savings(
                    vehicle_factors=VehicleFactorsEnum.TRUCK.value,
                    vehicles_count=data.frota.qtd_caminhoes,
                    event_type="parking",
                    occurrences=data.frota.eventos_estacionamento_caminhoes,
                )
                co2_saved += res_park.co2_saved_kg
                fuel_saved += res_park.fuel_saved_l
                time_saved_min += res_park.time_saved_min

        # Conversão financeira dinâmica
        gasoline_price = self.fuel_price_service.get_average_gasoline_price()
        economia_reais = B2BDashboardService.calculate_financial_savings(
            fuel_saved=fuel_saved,
            time_saved=time_saved_min,
            gasoline_price=gasoline_price,
        )

        economia_co2_kg_final = round(co2_saved, 4)
        economia_gasolina_litros_final = round(fuel_saved, 4)
        economia_tempo_minutos_final = round(time_saved_min, 4)
        dinheiro_economizado_final = round(economia_reais, 4)

        # Persistir os dados da simulação e do Lead no banco de dados
        self.repository.create_lead_simulation(
            nome=data.lead.nome,
            email=data.lead.email,
            telefone=data.lead.telefone,
            endereco=data.lead.endereco,
            qtd_carros=data.frota.qtd_carros,
            qtd_caminhoes=data.frota.qtd_caminhoes,
            eventos_pedagio_carros=data.frota.eventos_pedagio_carros,
            eventos_estacionamento_carros=data.frota.eventos_estacionamento_carros,
            eventos_pedagio_caminhoes=data.frota.eventos_pedagio_caminhoes,
            eventos_estacionamento_caminhoes=data.frota.eventos_estacionamento_caminhoes,
            economia_co2_kg=economia_co2_kg_final,
            economia_gasolina_litros=economia_gasolina_litros_final,
            economia_tempo_minutos=economia_tempo_minutos_final,
            dinheiro_economizado=dinheiro_economizado_final,
        )

        return SimulacaoResponse(
            economia_co2_kg=economia_co2_kg_final,
            economia_gasolina_litros=economia_gasolina_litros_final,
            economia_tempo_minutos=economia_tempo_minutos_final,
            dinheiro_economizado=dinheiro_economizado_final,
        )
