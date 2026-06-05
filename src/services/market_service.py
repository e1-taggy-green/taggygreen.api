from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.repositories.market_repository import MarketplaceRepository
from src.repositories.event_repository import EventRepository
from src.repositories.user_repository import UserRepository
from src.schemas.market_schema import (
    ProdutoResponse,
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
        # UserRepository injetado para validar existência do usuário no resgate.
        self.user_repository = UserRepository(db)



    def get_destaques(self) -> list[ProdutoResponse]:
        """getDestaqueMP — Retorna os 3 produtos parceiros em destaque
        (os de maior valor em Pontos de Carbono), conforme contrato Swagger.
        """
        produtos = self.market_repository.get_featured_products(limit=3)
        if not produtos:
            raise HTTPException(status_code=404, detail="Nenhuma recompensa disponível")
        return [
            ProdutoResponse(
                id=p.id,
                nome=p.name,
                pontos_custo=p.cost_points,
            )
            for p in produtos
        ]

    def get_produtos_paginados(self, page: int, size: int) -> ProdutosPaginadosResponse:
        """getProdutosMP — Lista paginada das recompensas disponíveis.

        Retorna apenas 'items' e 'total', sem expor 'page'/'size' no
        response body (conforme Swagger).
        """
        produtos, total = self.market_repository.get_products_paginated(page, size)
        items = [
            ProdutoResponse(
                id=produto.id,
                nome=produto.name,
                pontos_custo=produto.cost_points,
            )
            for produto in produtos
        ]
        return ProdutosPaginadosResponse(total=total, items=items)

    def resgatar_produto(self, email: str, product_id: int) -> ResgateResponse:
        """updateSaldo — Processa o resgate de forma atômica.

        Fluxo:
        1. Valida que o USUÁRIO existe buscando por e-mail (404 se não).
        2. Valida que o PRODUTO existe (404 se não).
        3. Calcula saldo real do usuário (eventos − resgates).
        4. Saldo insuficiente → rollback + 400 (conforme Swagger).
        5. Registra o resgate + commit.
        """
        try:
            # 1. Valida existência do usuário (impede resgate fantasma) buscando por e-mail.
            usuario = self.user_repository.get_user_by_email(email)
            if not usuario:
                raise HTTPException(
                    status_code=404, detail="Usuário não encontrado"
                )
            user_id = usuario.id

            # 2. Valida que a recompensa existe.
            produto = self.market_repository.get_product_by_id(product_id)
            if not produto:
                raise HTTPException(
                    status_code=404, detail="Produto não encontrado"
                )

            # 3. Obtém o saldo atual do usuário (diretamente da coluna points)
            saldo_real = usuario.points

            # 4. Saldo insuficiente: aborta a transação e retorna 400.
            if saldo_real < produto.cost_points:
                self.db.rollback()
                raise HTTPException(
                    status_code=400, detail="saldo insuficiente"
                )

            # 5. Saldo suficiente: registra o resgate, atualiza saldo e confirma (commit).
            self.market_repository.create_redemption(
                user_id=user_id,
                product_id=product_id,
                cost=produto.cost_points,
            )
            
            saldo_atualizado = saldo_real - produto.cost_points
            self.user_repository.update_balance(user_id, saldo_atualizado)
            
            self.db.commit()

            return ResgateResponse(saldo_atualizado=saldo_atualizado)
        except HTTPException:
            # Erros de negócio (404/400) já trataram seu próprio estado: re-propaga.
            raise
        except Exception:
            # Qualquer falha inesperada de banco: desfaz a transação e re-lança.
            self.db.rollback()
            raise
