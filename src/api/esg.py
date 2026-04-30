from fastapi import APIRouter
from src.schemas.esg import ESGSavingResult, CalculateSavingsRequest, VehicleFactorsEnum
from src.services.esg_engine import ESGEngine

router = APIRouter(
    prefix="/api/v1/esg",
    tags=["Motor Matemático ESG"]
)

@router.post("/calculate-savings", response_model=ESGSavingResult, summary="Calcula a Economia ESG (TaggyGreen)")
def calculate_esg_savings(request: CalculateSavingsRequest):
    """
    Recebe os dados agregados da frota e retorna o cálculo de economia total.
    (Quanto de CO2, tempo e combustível foi poupado com o uso da Tag)
    """
    engine = ESGEngine()
    
    # Busca as constantes no código (Enum) usando o tipo enviado pelo frontend
    factors = VehicleFactorsEnum[request.vehicle_type.name].value
    
    return engine.calculate_savings(
        vehicle_factors=factors,
        vehicles_count=request.vehicles_count,
        event_type=request.event_type,
        occurrences=request.occurrences
    )