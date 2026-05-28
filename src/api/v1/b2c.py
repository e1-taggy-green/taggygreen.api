from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.user_schema import UsuarioResponse, RastroHistoricoResponse, ExtratoItem
from src.database.session import get_db
from src.services.b2c_service import B2CService

# Router do Hub B2C: histórico de sustentabilidade individualizado do usuário final.
router = APIRouter(prefix="/api/v1/b2c", tags=["B2C Histórico Individual"])


@router.get("/usuarios/{user_id}", response_model=UsuarioResponse, status_code=200)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    getUser — Retorna o nome do usuário final e seu saldo atual de
    mitigação ambiental acumulada (kg de CO2 poupado).
    """
    service = B2CService(db)
    return service.get_user(user_id)


@router.get("/usuarios/{user_id}/rastro-historico", response_model=RastroHistoricoResponse, status_code=200)
async def get_user_rastro_historico(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    getUserRastroHistorico — Retorna nome, saldo de mitigação acumulada e o
    agrupamento mensal da economia dos últimos 4 meses de uso do usuário.
    """
    service = B2CService(db)
    return service.get_user_rastro_historico(user_id)


@router.get("/usuarios/{user_id}/extrato", response_model=list[ExtratoItem], status_code=200)
async def get_user_extrato(
    user_id: int,
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de passagens recentes a retornar"),
    db: Session = Depends(get_db),
):
    """
    getUserExtrato — Retorna as últimas passagens (pedágio/estacionamento)
    do usuário, detalhando o nome da Praça/Estacionamento, a data da passagem
    e o valor fracionário de CO2 poupado naquele evento singular.
    """
    service = B2CService(db)
    return service.get_user_extrato(user_id, limit)
