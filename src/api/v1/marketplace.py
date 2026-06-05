from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.market_schema import (
    ProdutoResponse,
    ProdutosPaginadosResponse,
    ResgateRequest,
    ResgateResponse,
)
from src.database.session import get_db
from src.services.market_service import MarketService

# Router do Marketplace: programa de fidelidade B2C (recompensas e resgates).
# Prefixo inclui /b2c conforme contrato Swagger oficial (openapi.yaml).
router = APIRouter(prefix="/api/v1/b2c/marketplace", tags=["B2C - Marketplace"])


@router.get("/destaques", response_model=list[ProdutoResponse], status_code=200)
async def get_destaques_mp(
    db: Session = Depends(get_db),
) -> list[ProdutoResponse]:
    """
    getDestaqueMP — Retorna os 3 produtos parceiros em destaque
    (os de maior valor em Pontos de Carbono).
    """
    service = MarketService(db)
    return service.get_destaques()


@router.get("/produtos", response_model=ProdutosPaginadosResponse, status_code=200)
async def get_produtos_mp(
    page: int = Query(1, ge=1, description="Página da listagem de recompensas"),
    size: int = Query(10, ge=1, le=50, description="Quantidade de recompensas por página"),
    db: Session = Depends(get_db),
) -> ProdutosPaginadosResponse:
    """
    getProdutosMP — Retorna a listagem paginada das recompensas disponíveis,
    com o Nome do Produto e o Valor em Pontos de Carbono.
    """
    service = MarketService(db)
    return service.get_produtos_paginados(page, size)


@router.post("/resgatar", response_model=ResgateResponse, status_code=200)
async def resgatar_produto(
    request: ResgateRequest,
    db: Session = Depends(get_db),
) -> ResgateResponse:
    """
    updateSaldo — Processa o resgate de uma recompensa: valida o usuário e
    o saldo real, abate os Pontos de Carbono e garante (transação atômica)
    que o saldo nunca fique negativo. Retorna 400 quando o saldo é insuficiente.
    """
    service = MarketService(db)
    return service.resgatar_produto(request.email, request.product_id)
