from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int):
        pass

    def update_balance(self, user_id: int, new_balance: float):
        pass
