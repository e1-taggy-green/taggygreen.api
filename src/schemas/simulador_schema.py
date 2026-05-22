from pydantic import BaseModel, EmailStr, Field, model_validator


class SimulacaoInput(BaseModel):
    """Contrato de entrada do Simulador para Leads/Prospects (B2B)."""
    nome: str = Field(..., description="Nome do Lead para follow-up comercial")
    email: EmailStr = Field(..., description="E-mail corporativo do Lead")
    empresa: str = Field(..., description="Empresa do Lead (contexto B2B)")
    qtd_carros: int = Field(0, ge=0, description="Quantidade hipotética de carros na frota")
    qtd_caminhoes: int = Field(0, ge=0, description="Quantidade hipotética de caminhões na frota")
    eventos_mensais_por_veiculo: int = Field(..., gt=0, description="Eventos (pedágios) mensais por veículo")

    @model_validator(mode="after")
    def validar_frota_nao_vazia(self) -> "SimulacaoInput":
        if self.qtd_carros + self.qtd_caminhoes <= 0:
            raise ValueError("A frota hipotética deve conter ao menos 1 veículo (carro ou caminhão).")
        return self


class SimulacaoOutput(BaseModel):
    """Projeção de mitigação ambiental (mensal e anual) para o Lead."""
    co2_mitigado_kg_mensal: float
    co2_mitigado_kg_anual: float
    combustivel_economizado_l_mensal: float
    combustivel_economizado_l_anual: float
    tempo_economizado_horas_mensal: float
    tempo_economizado_horas_anual: float
