from sqlalchemy.orm import Session
from src.models.lead import Lead


class LeadRepository:
    """Repositório responsável por realizar operações de persistência do Lead."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_lead_simulation(
        self,
        nome: str,
        email: str,
        telefone: str | None,
        endereco: str | None,
        qtd_carros: int,
        qtd_caminhoes: int,
        eventos_pedagio_carros: int,
        eventos_estacionamento_carros: int,
        eventos_pedagio_caminhoes: int,
        eventos_estacionamento_caminhoes: int,
        economia_co2_kg: float,
        economia_gasolina_litros: float,
        economia_tempo_minutos: float,
        dinheiro_economizado: float,
    ) -> Lead:
        """Cria e persiste uma simulação de Lead no banco de dados."""
        lead = Lead(
            nome=nome,
            email=email,
            telefone=telefone,
            endereco=endereco,
            qtd_carros=qtd_carros,
            qtd_caminhoes=qtd_caminhoes,
            eventos_pedagio_carros=eventos_pedagio_carros,
            eventos_estacionamento_carros=eventos_estacionamento_carros,
            eventos_pedagio_caminhoes=eventos_pedagio_caminhoes,
            eventos_estacionamento_caminhoes=eventos_estacionamento_caminhoes,
            economia_co2_kg=economia_co2_kg,
            economia_gasolina_litros=economia_gasolina_litros,
            economia_tempo_minutos=economia_tempo_minutos,
            dinheiro_economizado=dinheiro_economizado,
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
