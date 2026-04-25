from sqlalchemy.orm import Session
from sqlalchemy import func

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_events_by_user(self, user_id: int):
        pass

    def get_aggregated_b2b_dashboard(self, user_id: int):
        # Utilizar func.sum() para não carregar eventos para a memória atoa.
        pass
