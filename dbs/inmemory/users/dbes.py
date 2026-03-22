from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, Integer, String, func

from dbs.inmemory.base import Base


class UserDBE(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid4)
    username = Column(String)
    token_balance = Column(Integer, default=300)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
