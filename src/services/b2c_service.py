import math
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.repositories.event_repository import EventRepository
from src.models.user import User
from src.schemas.user_schema import (
    UsuarioResponse,
    MesEconomiaItem,
    ExtratoItem,
    EquivalenciasResponse,
    AddPointsResponse,
)


class B2CService:
    """
    Serviço do Hub B2C: histórico de sustentabilidade individualizado do
    usuário final (motorista). Diferente do B2B (que agrega por frota/CNPJ),
    todas as consultas aqui filtram exclusivamente pelo e-mail e userID correspondente.
    """

    # Tradução do event_type para o nome legível do local de passagem.
    # Não existe coluna de "nome da praça" nos models, então o rótulo amigável
    # é derivado do tipo de evento já persistido (mesmo padrão do B2B).
    EVENT_TYPE_TRANSLATION = {"toll": "Praça de Pedágio", "parking": "Estacionamento"}

    MONTH_NAMES_PT = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }

    MONTHS_WINDOW = 4

    # Fatores de conversão do CO2 poupado em equivalências ambientais tangíveis,
    # usados para traduzir o saldo de mitigação em métricas do dia a dia.
    CO2_POR_ARVORE_KG = 15.0  # Absorção média anual de CO2 de 1 árvore
    FATOR_CO2_PARA_LITROS = 0.42  # Conversão CO2 → litros de gasolina
    FATOR_CO2_PARA_LED_HORAS = 8.5  # Conversão CO2 → horas de LED

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.event_repository = EventRepository(db)

    def _get_user_by_email_or_404(self, email: str) -> User:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user

    def _calcular_data_corte(self) -> datetime:
        # Calcula o primeiro dia do mês inicial da janela (current month + 3 anteriores),
        # de forma a cobrir exatamente os últimos 4 meses a partir da data atual.
        hoje = datetime.now()
        total_meses = (hoje.year * 12 + (hoje.month - 1)) - (self.MONTHS_WINDOW - 1)
        ano = total_meses // 12
        mes = total_meses % 12 + 1
        return datetime(ano, mes, 1)

    def _formatar_mes(self, label: str) -> str:
        # O label vem do SQLite no formato 'YYYY-MM'; converte para 'Mês/Ano' em PT.
        ano, mes = label.split("-")
        return f"{self.MONTH_NAMES_PT[int(mes)]}/{ano}"

    def get_user(self, email: str) -> UsuarioResponse:
        # 1. Valida o usuário por e-mail e obtém seus dados.
        user = self._get_user_by_email_or_404(email)
        # 2. Retorna o saldo diretamente da coluna points do usuário.
        saldo = user.points
        return UsuarioResponse(userName=user.name, userPoints=saldo)

    def get_user_rastro_historico(self, email: str) -> list[MesEconomiaItem]:
        # 1. Valida o usuário por e-mail e obtém seus dados.
        user = self._get_user_by_email_or_404(email)
        
        data_corte = self._calcular_data_corte()
        linhas = self.event_repository.get_monthly_savings_by_user(user.id, data_corte)
        return [
            MesEconomiaItem(
                mes=self._formatar_mes(linha.mes),
                co2_economizado=round(linha.co2_saved or 0.0, 4),
            )
            for linha in linhas
        ]

    def get_user_extrato(self, email: str, limit: int = 10) -> list[ExtratoItem]:
        # 1. Valida o usuário por e-mail.
        user = self._get_user_by_email_or_404(email)
        
        eventos = self.event_repository.get_extrato_by_user(user.id, limit)
        return [
            ExtratoItem(
                nome=self.EVENT_TYPE_TRANSLATION.get(evento.event_type, evento.event_type),
                data=evento.created_at,
                registro_economia=round(evento.co2_saved or 0.0, 4),
            )
            for evento in eventos
        ]

    def get_equivalencias(self, email: str) -> EquivalenciasResponse:
        # 1. Valida o usuário por e-mail e obtém seus dados.
        user = self._get_user_by_email_or_404(email)
        # 2. Saldo total de mitigação ambiental acumulada (kg de CO2 poupado).
        co2_total = self.event_repository.get_total_co2_saved_by_user(user.id)
        # 3. Traduz o CO2 poupado nas equivalências ambientais exibidas no front.
        return EquivalenciasResponse(
            arvores=math.floor(co2_total / self.CO2_POR_ARVORE_KG),
            combustivel_litros=round(co2_total * self.FATOR_CO2_PARA_LITROS),
            horas_led=round(co2_total * self.FATOR_CO2_PARA_LED_HORAS),
            co2_total_kg=round(co2_total),
        )

    def add_points(self, email: str, points: int) -> AddPointsResponse:
        user = self._get_user_by_email_or_404(email)
        user.points += points
        self.user_repository.update_balance(user.id, user.points)
        self.db.commit()
        return AddPointsResponse(saldo_atualizado=user.points)
