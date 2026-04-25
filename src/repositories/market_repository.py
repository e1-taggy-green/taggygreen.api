from sqlalchemy.orm import Session

class MarketplaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_products_paginated(self, page: int, size: int):
        pass

    def create_redemption(self, user_id: int, product_id: int, cost: float):
        pass
