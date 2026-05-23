from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.schemas.simulador_schema import SimulacaoRequest, SimulacaoResponse
from src.services.simulador_service import SimuladorService

router = APIRouter(
    prefix="/api/v1/simulador",
    tags=["Simulador Lead/Prospect"]
)


@router.post("/simulacao", response_model=SimulacaoResponse, status_code=200, summary="Projeta a mitigação ambiental para um Lead")
def simular_mitigacao(payload: SimulacaoRequest, db: Session = Depends(get_db)) -> SimulacaoResponse:
    """
    Recebe os dados de contato do Lead e os dados hipotéticos da frota,
    retornando a projeção de CO2 mitigado, combustível economizado, tempo
    economizado (em minutos) e retorno financeiro. Persiste as informações no banco.
    """
    service = SimuladorService(db)
    return service.calculate_lead_projection(payload)
