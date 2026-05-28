from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioResponse(BaseModel):
    """
    Contrato do endpoint getUser: identificação básica do usuário final
    e seu saldo atual de mitigação ambiental acumulada (kg de CO2).
    """
    nome: str = Field(..., description="Nome do usuário final")
    saldo_mitigacao_kg: float = Field(..., description="Saldo atual de mitigação acumulada (kg de CO2 poupado)")


class MesEconomiaItem(BaseModel):
    """Economia ambiental consolidada de um único mês do rastro histórico."""
    mes: str = Field(..., description="Mês de referência formatado (ex: 'Maio/2026')")
    co2_evitado_kg: float = Field(..., description="Volume de CO2 poupado no mês (kg)")
    combustivel_evitado_litros: float = Field(..., description="Litros de combustível economizados no mês")
    tempo_economizado_minutos: float = Field(..., description="Tempo (minutos) economizado em filas no mês")


class RastroHistoricoResponse(BaseModel):
    """
    Contrato do endpoint getUserRastroHistorico: dados do usuário, saldo de
    mitigação acumulada e o agrupamento mensal da economia dos últimos 4 meses.
    """
    nome: str = Field(..., description="Nome do usuário final")
    saldo_mitigacao_kg: float = Field(..., description="Saldo atual de mitigação acumulada (kg de CO2 poupado)")
    historico_mensal: list[MesEconomiaItem] = Field(
        ..., description="Agrupamento mensal da economia dos últimos 4 meses de uso (ordem cronológica)"
    )


class ExtratoItem(BaseModel):
    """Detalhe de uma única passagem (pedágio/estacionamento) no extrato do usuário."""
    local: str = Field(..., description="Nome da Praça/Estacionamento do evento")
    data: datetime = Field(..., description="Data da passagem")
    co2_evitado_kg: float = Field(..., description="Valor fracionário de CO2 poupado nesse evento singular (kg)")
