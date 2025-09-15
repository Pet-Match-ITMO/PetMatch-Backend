from .base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, Boolean


class User(Base):
    __tablename__ = "users"
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    username = mapped_column(String(50), unique=True, nullable=False)
    password = mapped_column(String(128), nullable=False)
    is_active = mapped_column(Boolean, default=True)
