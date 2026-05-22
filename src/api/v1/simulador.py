from fastapi import APIRouter
from src.schemas.simulador_schema import SimulacaoInput, SimulacaoOutput
from src.services.simulador_service import SimuladorService

router = APIRouter(
    prefix="/api/v1/simulador",
    tags=["Simulador Lead/Prospect"]
)


@router.post("/simulacao", response_model=SimulacaoOutput, status_code=200, summary="Projeta a mitigação ambiental para um Lead")
def simular_mitigacao(payload: SimulacaoInput) -> SimulacaoOutput:
    """
    Recebe os dados de contato do Lead e os dados hipotéticos da frota,
    retornando a projeção mensal e anual de CO2 mitigado, combustível
    economizado e tempo economizado. Opera em memória (sem persistência).
    """
    service = SimuladorService()
    return service.simular(payload)
