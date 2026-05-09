from pydantic import BaseModel, Field

class RelatorioESGResponse(BaseModel):
    """
    Contrato de API contendo os KPIs consolidados de ESG da frota corporativa.
    """
    co2_evitado_kg: float = Field(..., description="Volume total evitado em kg de CO2")
    combustivel_evitado_litros: float = Field(..., description="Litros de Gasolina/Diesel economizados")
    tempo_economizado_minutos: float = Field(..., description="Tempo em minutos ganho nas filas")
    frota_total: int = Field(..., description="Quantidade total de veículos da frota")
    economia_financeira: float = Field(..., description="Economia financeira total em R$")
    roi_percentual: float = Field(..., description="Retorno sobre o Investimento (ROI) em %")
