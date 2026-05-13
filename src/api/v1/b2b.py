from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.dashboard_schema import RelatorioESGResponse, PerformanceCategoriaResponse, RankingFrotaResponse
from src.database.session import get_db
from src.services.b2b_service import B2BService

# Configuração do Router para ser incluído no arquivo principal da API
router = APIRouter(prefix="/api/v1/b2b/relatorios", tags=["B2B ESG"])

@router.get("/esg", response_model=RelatorioESGResponse, status_code=200)
async def get_relatorio_esg(
    email: str = Query(..., description="Email corporativo para buscar o dashboard consolidado"),
    db: Session = Depends(get_db)
):
    """
    Endpoint raiz do painel corporativo (B2B).
    Agrupa todas as passagens da frota atrelada ao Email fornecido e calcula o 
    total consolidado de externalidades evitadas.
    """
    service = B2BService(db)
    return service.get_esg_dashboard_report(email)

@router.get("/performance/categoria", response_model=list[PerformanceCategoriaResponse], status_code=200)
async def get_performance_categoria(
    email: str = Query(..., description="Email corporativo da frota B2B"),
    db: Session = Depends(get_db)
):
    """
    Agrega o desempenho ambiental (CO2 e Combustível poupados) fatiado por tipo de veículo.
    """
    service = B2BService(db)
    return service.get_performance_by_category(email)

@router.get("/performance/ranking", response_model=list[RankingFrotaResponse], status_code=200)
async def get_ranking_frota(
    email: str = Query(..., description="Email corporativo da frota B2B"),
    db: Session = Depends(get_db)
):
    """
    Lista os 5 veículos (placas) mais eficientes com base no número de transações e mitigação.
    """
    service = B2BService(db)
    return service.get_fleet_ranking(email)