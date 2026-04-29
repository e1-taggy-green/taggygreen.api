from fastapi import APIRouter
from src.schemas.esg import ESGSavingResult, CalculateSavingsRequest
from src.services.esg_engine import ESGEngine

router = APIRouter(
    prefix="/api/v1/esg",
    tags=["Motor Matemático ESG"]
)

@router.post("/calculate-savings", response_model=ESGSavingResult, summary="Calcula a Economia ESG (TaggyGreen)")
def calculate_esg_savings(request: CalculateSavingsRequest):
    """
    Recebe dados de passagem e fatores de emissão, e retorna o cálculo comparativo.
    (Quanto de CO2, tempo e combustível foi poupado com o uso da Tag)
    """
    engine = ESGEngine()
    return engine.calculate_savings(
        base_fuel_l=request.base_fuel_l,
        vehicle_factors=request.vehicle_factors,
        idle_time_min=request.idle_time_min
    )