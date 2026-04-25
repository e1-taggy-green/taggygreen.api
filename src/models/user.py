from sqlalchemy import Column, Integer, String
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    user_type = Column(String) # 'b2c' ou 'b2b'
    points = Column(Integer, default=0)
