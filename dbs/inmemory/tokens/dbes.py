from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dbs.inmemory.base import Base


class TokenUsageDBE(Base):
    __tablename__ = "token_usage"

    id = Column(UUID, primary_key=True, default=uuid4)
    generation_id = Column(
        UUID,
        ForeignKey(
            "generations.id",
            name="fk_token_usage_generation_id",
            ondelete="CASCADE",
        ),
    )
    amount = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    generation = relationship(
        "GenerationDBE",
        back_populates="token_usage",
    )
