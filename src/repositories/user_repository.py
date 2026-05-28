from sqlalchemy.orm import Session
from src.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        # Busca o usuário final exclusivamente pelo seu ID (chave primária).
        return self.db.query(User).filter(User.id == user_id).first()

    def update_balance(self, user_id: int, new_balance: float):
        pass
