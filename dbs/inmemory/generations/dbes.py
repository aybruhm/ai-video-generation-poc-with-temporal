from uuid import uuid4

from sqlalchemy import UUID, Column, Integer, String

from dbs.inmemory.base import Base


class GenerationDBE(Base):
    __tablename__ = "generations"

    id = Column(UUID, primary_key=True, default=uuid4)
    status = Column(String, default="queued")
    tokens_deducted = Column(Integer)
    output_url = Column(String)
