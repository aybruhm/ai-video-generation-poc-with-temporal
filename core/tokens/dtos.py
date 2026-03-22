from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenUsageCreateDTO(BaseModel):
    generation_id: str
    amount: int


class TokenUsageDTO(BaseModel):
    id: UUID
    generation_id: UUID
    amount: int
    created_at: datetime
