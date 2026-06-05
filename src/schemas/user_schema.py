from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioResponse(BaseModel):
    """
    Contrato do endpoint getUser: identificação básica do usuário final
    e seu saldo atual de mitigação ambiental acumulada.
    """
    userName: str = Field(..., description="Nome do usuário final")
    userPoints: int = Field(..., description="Saldo atual de pontos Taggy (100 pontos = 1kg CO2 poupado)")


class MesEconomiaItem(BaseModel):
    """Economia ambiental de CO2 de um único mês do rastro histórico."""
    mes: str = Field(..., description="Mês de referência formatado (ex: 'Maio/2026')")
    co2_economizado: float = Field(..., description="Volume de CO2 poupado no mês (kg)")


class ExtratoItem(BaseModel):
    """Detalhe de uma única passagem (pedágio/estacionamento) no extrato do usuário."""
    nome: str = Field(..., description="Nome da Praça/Estacionamento do evento")
    data: datetime = Field(..., description="Data da passagem")
    registro_economia: float = Field(..., description="Valor fracionário de CO2 poupado nesse evento singular (kg)")


class AddPointsRequest(BaseModel):
    """Contrato para a adição de pontos ao usuário."""
    email: str = Field("teste.b2c@taggy.com", description="E-mail do usuário")
    points: int = Field(..., description="Quantidade de pontos a serem adicionados")


class AddPointsResponse(BaseModel):
    """Resposta após adicionar pontos."""
    saldo_atualizado: int = Field(..., description="Saldo atualizado de pontos")

