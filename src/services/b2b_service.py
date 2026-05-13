from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.repositories.event_repository import EventRepository
from src.schemas.dashboard_schema import RelatorioESGResponse

class B2BService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = EventRepository(db)

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
        # Gasolina: R$ 5,50/L
        # Tempo Homem-Hora: R$ 50,00/h -> 50 / 60 por minuto
        economia_reais = (combustivel * 5.50) + (tempo * (50.0 / 60.0))

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
                "categoria": row.vehicle_type,
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
                "co2_evitado_kg": round(row.total_co2 or 0.0, 4),
                "transacoes": row.total_transacoes
            } for idx, row in enumerate(results, start=1)
        ]
