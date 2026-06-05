from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.user_schema import UsuarioResponse, MesEconomiaItem, ExtratoItem, EquivalenciasResponse, AddPointsRequest, AddPointsResponse
from src.database.session import get_db
from src.services.b2c_service import B2CService

# Router do Hub B2C: histórico de sustentabilidade individualizado do usuário final.
router = APIRouter(prefix="/api/v1/b2c", tags=["B2C Histórico Individual"])


@router.get("/user", response_model=UsuarioResponse, status_code=200)
async def get_user(
    email: str = Query("teste.b2c@taggy.com", description="E-mail do usuário final para buscar informações"),
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    """
    getUser — Retorna o nome do usuário final e seu saldo atual de
    mitigação ambiental acumulada (kg de CO2 poupado).
    """
    service = B2CService(db)
    return service.get_user(email)


@router.get("/user/rastro-historico", response_model=list[MesEconomiaItem], status_code=200)
async def get_user_rastro_historico(
    email: str = Query("teste.b2c@taggy.com", description="E-mail do usuário final para buscar o rastro histórico"),
    db: Session = Depends(get_db),
) -> list[MesEconomiaItem]:
    """
    getUserRastroHistorico — Retorna o agrupamento mensal da economia dos 
    últimos 4 meses de uso do usuário.
    """
    service = B2CService(db)
    return service.get_user_rastro_historico(email)


@router.get("/user/extrato", response_model=list[ExtratoItem], status_code=200)
async def get_user_extrato(
    email: str = Query("teste.b2c@taggy.com", description="E-mail do usuário final para buscar o extrato"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de passagens recentes a retornar"),
    db: Session = Depends(get_db),
) -> list[ExtratoItem]:
    """
    getUserExtrato — Retorna as últimas passagens (pedágio/estacionamento)
    do usuário, detalhando o nome da Praça/Estacionamento, a data da passagem
    e o valor de CO2 poupado naquele evento singular.
    """
    service = B2CService(db)
    return service.get_user_extrato(email, limit)


@router.get("/user/equivalencias", response_model=EquivalenciasResponse, status_code=200)
async def get_user_equivalencias(
    email: str = Query("teste.b2c@taggy.com", description="E-mail do usuário final para calcular as equivalências ambientais"),
    db: Session = Depends(get_db),
) -> EquivalenciasResponse:
    """
    getUserEquivalencias — Traduz o CO2 total poupado pelo usuário em
    equivalências ambientais tangíveis (árvores preservadas, litros de
    gasolina e horas de iluminação LED equivalentes).
    """
    service = B2CService(db)
    return service.get_equivalencias(email)


@router.post("/user/add-points", response_model=AddPointsResponse, status_code=200)
async def add_points(
    request: AddPointsRequest,
    db: Session = Depends(get_db),
) -> AddPointsResponse:
    """
    addPoints — Adiciona uma quantidade de pontos ao usuário especificado.
    """
    service = B2CService(db)
    return service.add_points(request.email, request.points)

