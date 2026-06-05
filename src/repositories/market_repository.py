from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.product import Product
from src.models.redemption import Redemption


class MarketplaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_products_paginated(self, page: int, size: int) -> tuple[list[Product], int]:
        # Retorna a fatia de produtos da página solicitada e o total geral.
        # Todos os produtos são considerados ativos (não existe flag is_active no model).
        total = self.db.query(func.count(Product.id)).scalar() or 0
        items = (
            self.db.query(Product)
            .order_by(Product.id)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return items, total

    def get_product_by_id(self, product_id: int) -> Product | None:
        # Busca uma recompensa exclusivamente pelo seu ID (chave primária).
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_featured_products(self, limit: int = 3) -> list[Product]:
        """Retorna os 'limit' produtos de maior valor em pontos (destaques).

        Critério: ordenação por cost_points DESC (empate: menor id primeiro).
        Usa .limit() para trazer apenas o necessário direto do banco,
        evitando carregar todos os produtos na memória Python.
        """
        return (
            self.db.query(Product)
            .order_by(Product.cost_points.desc(), Product.id.asc())
            .limit(limit)
            .all()
        )

    def sum_redemptions_cost_by_user(self, user_id: int) -> int:
        # Soma o custo (Product.cost_points) de todos os resgates já feitos pelo
        # usuário, unindo Redemption -> Product. Usado no cálculo do saldo real.
        total = (
            self.db.query(func.sum(Product.cost_points))
            .join(Redemption, Redemption.product_id == Product.id)
            .filter(Redemption.user_id == user_id)
            .scalar()
        )
        return total or 0

    def create_redemption(self, user_id: int, product_id: int, cost: float) -> Redemption:
        # Cria o resgate e faz flush (sem commit): o controle transacional —
        # commit/rollback — pertence ao service. O parâmetro 'cost' é ignorado,
        # pois o model Redemption não armazena custo.
        redemption = Redemption(user_id=user_id, product_id=product_id)
        self.db.add(redemption)
        self.db.flush()
        return redemption
