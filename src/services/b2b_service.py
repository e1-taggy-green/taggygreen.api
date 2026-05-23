import csv
import io
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.repositories.event_repository import EventRepository
from src.schemas.dashboard_schema import RelatorioESGResponse
from src.services.fuel_service import FuelPriceService

class B2BDashboardService:
    VEHICLE_TRANSLATION = {"car": "Carro", "truck": "Caminhão"}

    @staticmethod
    def calculate_financial_savings(fuel_saved: float, time_saved: float, gasoline_price: float) -> float:
        """
        Calcula a economia financeira baseada no combustível dinâmico (gasoline_price/L)
        e tempo economizado (R$ 50,00/h -> R$ 50,00/60 por minuto).
        """
        fuel = fuel_saved or 0.0
        time = time_saved or 0.0
        return (fuel * gasoline_price) + (time * (50.0 / 60.0))

    def __init__(self, db: Session):
        self.db = db
        self.repository = EventRepository(db)
        self.fuel_service = FuelPriceService()

    def get_esg_dashboard_report(self, email: str) -> RelatorioESGResponse:
        resultado = self.repository.get_aggregated_b2b_dashboard(email)

        # Se não houver frota ou resultados
        if not resultado or not resultado.frota_total:
            return RelatorioESGResponse(
                co2_evitado_kg=0.0,
                combustivel_evitado_litros=0.0,
                tempo_economizado_minutos=0.0,
                frota_total=0,
                economia_financeira=0.0,
                roi_percentual=0.0
            )

        # Valores base do banco
        co2 = resultado.co2_evitado_kg or 0.0
        combustivel = resultado.combustivel_evitado_litros or 0.0
        tempo = resultado.tempo_economizado_minutos or 0.0
        frota = resultado.frota_total or 0

        # Regras de Negócio: Conversão financeira
        gasoline_price = self.fuel_service.get_average_gasoline_price()
        economia_reais = self.calculate_financial_savings(combustivel, tempo, gasoline_price)

        # ROI = ((Retorno - Custo) / Custo) * 100
        # Custo assumido da solução Taggy por veículo: R$ 30,00 (Mensal)
        custo_taggy = frota * 30.0
        
        if custo_taggy > 0:
            roi = ((economia_reais - custo_taggy) / custo_taggy) * 100
        else:
            roi = 0.0

        return RelatorioESGResponse(
            co2_evitado_kg=round(co2, 2),
            combustivel_evitado_litros=round(combustivel, 2),
            tempo_economizado_minutos=round(tempo, 2),
            frota_total=frota,
            economia_financeira=round(economia_reais, 2),
            roi_percentual=round(roi, 2)
        )

    def get_performance_by_category(self, email: str) -> list[dict]:
        user = self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário B2B não encontrado")

        results = self.repository.get_performance_by_category(user.id)
        
        return [
            {
                "categoria": self.VEHICLE_TRANSLATION.get(row.vehicle_type, row.vehicle_type),
                "co2_evitado_kg": round(row.total_co2 or 0.0, 4),
                "combustivel_evitado_litros": round(row.total_fuel or 0.0, 4)
            } for row in results
        ]

    def get_fleet_ranking(self, email: str) -> list[dict]:
        user = self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário B2B não encontrado")

        results = self.repository.get_fleet_ranking(user.id)
        return [
            {
                "posicao": idx,
                "placa": row.license_plate,
                "tipo": self.VEHICLE_TRANSLATION.get(row.vehicle_type, row.vehicle_type),
                "co2_evitado_kg": round(row.total_co2 or 0.0, 4),
                "transacoes": row.total_transacoes
            } for idx, row in enumerate(results, start=1)
        ]

    def generate_esg_csv_report(self, email: str) -> str:
        user = self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário B2B não encontrado")

        events = self.repository.get_raw_events_for_csv(user.id)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', lineterminator='\n')
        writer.writerow([
            "Data",
            "Placa",
            "Tipo",
            "CO2 Evitado (kg)",
            "Combustível Evitado (L)",
            "Tempo Economizado (min)",
            "Economia Financeira (R$)"
        ])

        gasoline_price = self.fuel_service.get_average_gasoline_price()

        for event in events:
            data_str = event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else ""
            placa = event.license_plate
            tipo = self.VEHICLE_TRANSLATION.get(event.vehicle_type, event.vehicle_type)
            co2 = round(event.co2_saved or 0.0, 2)
            fuel = round(event.fuel_saved or 0.0, 2)
            time = round(event.time_saved or 0.0, 2)
            economia_reais = round(self.calculate_financial_savings(event.fuel_saved, event.time_saved, gasoline_price), 2)
            writer.writerow([data_str, placa, tipo, co2, fuel, time, economia_reais])

        return output.getvalue()
