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

class PerformanceCategoriaResponse(BaseModel):
    categoria: str = Field(..., description="Categoria do veículo (ex: car, truck)")
    co2_evitado_kg: float = Field(..., description="Volume total evitado em kg de CO2 pela categoria")
    combustivel_evitado_litros: float = Field(..., description="Litros de combustível economizados pela categoria")

class RankingFrotaResponse(BaseModel):
    posicao: int = Field(..., description="Posição no ranking (1 a 5)")
    placa: str = Field(..., description="Placa do veículo")
    tipo: str = Field(..., description="Tipo/Categoria do veículo (ex: Carro, Caminhão)")
    co2_evitado_kg: float = Field(..., description="Volume total evitado em kg de CO2")
    transacoes: int = Field(..., description="Número de transações (passagens/eventos)")
