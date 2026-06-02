from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.market_schema import (
    ProdutoMPItem,
    ProdutosPaginadosResponse,
    ResgateRequest,
    ResgateResponse,
)
from src.database.session import get_db
from src.services.market_service import MarketService

# Router do Marketplace: programa de fidelidade B2C (recompensas e resgates).
router = APIRouter(prefix="/api/v1/marketplace", tags=["Marketplace Fidelidade B2C"])


@router.get("/destaque", response_model=ProdutoMPItem, status_code=200)
async def get_destaque_mp(
    db: Session = Depends(get_db),
) -> ProdutoMPItem:
    """
    getDestaqueMP — Retorna a recompensa em destaque do Marketplace
    (a de maior valor em Pontos de Carbono).
    """
    service = MarketService(db)
    return service.get_destaque()


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


@router.post("/resgates", response_model=ResgateResponse, status_code=201)
async def update_saldo(
    request: ResgateRequest,
    db: Session = Depends(get_db),
) -> ResgateResponse:
    """
    updateSaldo — Processa o resgate de uma recompensa: valida o saldo real do
    usuário, abate os Pontos de Carbono e garante (transação atômica) que o
    saldo nunca fique negativo. Retorna 422 quando o saldo é insuficiente.
    """
    service = MarketService(db)
    return service.resgatar(request.user_id, request.product_id)
