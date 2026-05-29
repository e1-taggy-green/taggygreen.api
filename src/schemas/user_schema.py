from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioResponse(BaseModel):
    """
    Contrato do endpoint getUser: identificação básica do usuário final
    e seu saldo atual de mitigação ambiental acumulada.
    """
    userName: str = Field(..., description="Nome do usuário final")
    userPoints: float = Field(..., description="Saldo atual de mitigação acumulada (kg de CO2 poupado)")


class MesEconomiaItem(BaseModel):
    """Economia ambiental de CO2 de um único mês do rastro histórico."""
    mes: str = Field(..., description="Mês de referência formatado (ex: 'Maio/2026')")
    co2_economizado: float = Field(..., description="Volume de CO2 poupado no mês (kg)")


class ExtratoItem(BaseModel):
    """Detalhe de uma única passagem (pedágio/estacionamento) no extrato do usuário."""
    nome: str = Field(..., description="Nome da Praça/Estacionamento do evento")
    data: datetime = Field(..., description="Data da passagem")
    registro_economia: float = Field(..., description="Valor fracionário de CO2 poupado nesse evento singular (kg)")

