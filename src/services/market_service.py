from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.repositories.market_repository import MarketplaceRepository
from src.repositories.event_repository import EventRepository
from src.schemas.market_schema import (
    ProdutoMPItem,
    ProdutosPaginadosResponse,
    ResgateResponse,
)


class MarketService:
    """
    Serviço do Marketplace (programa de fidelidade B2C). Expõe as recompensas
    e processa os resgates, garantindo — de forma atômica — que o saldo de
    Pontos de Carbono do usuário nunca fique negativo.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.market_repository = MarketplaceRepository(db)
        self.event_repository = EventRepository(db)

    def _get_saldo_real(self, user_id: int) -> float:
        # Saldo real = total de CO2 poupado em eventos - custo de todos os resgates.
        # Esse cálculo é exclusivo da validação do Marketplace nesta task.
        saldo_eventos = self.event_repository.get_total_co2_saved_by_user(user_id)
        custo_resgates = self.market_repository.sum_redemptions_cost_by_user(user_id)
        return round(saldo_eventos - custo_resgates, 4)

    def get_destaque(self) -> ProdutoMPItem:
        # getDestaqueMP: retorna a recompensa em destaque (maior cost_points).
        produto = self.market_repository.get_featured_product()
        if not produto:
            raise HTTPException(status_code=404, detail="Nenhuma recompensa disponível")
        return ProdutoMPItem(
            id=produto.id,
            nome=produto.name,
            custo_pontos_carbono=produto.cost_points,
        )

    def get_produtos_paginados(self, page: int, size: int) -> ProdutosPaginadosResponse:
        # getProdutosMP: lista paginada das recompensas disponíveis.
        produtos, total = self.market_repository.get_products_paginated(page, size)
        items = [
            ProdutoMPItem(
                id=produto.id,
                nome=produto.name,
                custo_pontos_carbono=produto.cost_points,
            )
            for produto in produtos
        ]
        return ProdutosPaginadosResponse(page=page, size=size, total=total, items=items)

    def resgatar(self, user_id: int, product_id: int) -> ResgateResponse:
        # updateSaldo: processa o resgate de uma recompensa de forma atômica.
        try:
            # 1. Valida que a recompensa existe (404 caso contrário).
            produto = self.market_repository.get_product_by_id(product_id)
            if not produto:
                raise HTTPException(status_code=404, detail="Produto não encontrado")

            # 2. Calcula o saldo real do usuário (eventos - resgates anteriores).
            saldo_real = self._get_saldo_real(user_id)

            # 3. Saldo insuficiente: aborta a transação (rollback) e retorna 422.
            #    Isso garante que o saldo nunca fique negativo.
            if saldo_real < produto.cost_points:
                self.db.rollback()
                raise HTTPException(status_code=422, detail="Saldo insuficiente")

            # 4. Saldo suficiente: registra o resgate e confirma a transação (commit).
            redemption = self.market_repository.create_redemption(
                user_id=user_id,
                product_id=product_id,
                cost=produto.cost_points,
            )
            self.db.commit()

            # Saldo restante já considerando o débito recém-confirmado.
            saldo_restante = round(saldo_real - produto.cost_points, 4)
            return ResgateResponse(
                redemption_id=redemption.id,
                user_id=user_id,
                product_id=product_id,
                pontos_debitados=produto.cost_points,
                saldo_restante=saldo_restante,
                mensagem="Resgate realizado com sucesso",
            )
        except HTTPException:
            # Erros de negócio (404/422) já trataram seu próprio estado: re-propaga.
            raise
        except Exception:
            # 5. Qualquer falha inesperada de banco: desfaz a transação e re-lança.
            self.db.rollback()
            raise
