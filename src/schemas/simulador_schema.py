from pydantic import BaseModel, EmailStr, Field, model_validator


class LeadData(BaseModel):
    """Informações de contato e identificação do Lead B2B."""
    nome: str = Field(..., description="Nome do Lead para follow-up comercial")
    email: EmailStr = Field(..., description="E-mail corporativo do Lead")
    telefone: str | None = Field(None, description="Telefone de contato do Lead")
    endereco: str | None = Field(None, description="Endereço da empresa/Lead")


class FrotaData(BaseModel):
    """Dados quantitativos e comportamentais da frota hipotética do Lead."""
    qtd_carros: int = Field(0, ge=0, description="Quantidade hipotética de carros na frota")
    qtd_caminhoes: int = Field(0, ge=0, description="Quantidade hipotética de caminhões na frota")
    
    # Eventos específicos por tipo de veículo
    eventos_pedagio_carros: int = Field(0, ge=0, description="Eventos (pedágios) mensais por carro")
    eventos_estacionamento_carros: int = Field(0, ge=0, description="Eventos (estacionamentos) mensais por carro")
    eventos_pedagio_caminhoes: int = Field(0, ge=0, description="Eventos (pedágios) mensais por caminhão")
    eventos_estacionamento_caminhoes: int = Field(0, ge=0, description="Eventos (estacionamentos) mensais por caminhão")


class SimulacaoRequest(BaseModel):
    """Contrato de entrada do Simulador para Leads/Prospects (B2B) com dados aninhados."""
    lead: LeadData
    frota: FrotaData

    @model_validator(mode="after")
    def validar_frota_nao_vazia(self) -> "SimulacaoRequest":
        if self.frota.qtd_carros + self.frota.qtd_caminhoes <= 0:
            raise ValueError("A frota hipotética deve conter ao menos 1 veículo (carro ou caminhão).")
        return self


class SimulacaoResponse(BaseModel):
    """Projeção de mitigação e economia financeira consolidada para o Lead."""
    economia_co2_kg: float
    economia_gasolina_litros: float
    economia_tempo_minutos: float
    dinheiro_economizado: float
