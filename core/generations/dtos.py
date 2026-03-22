from uuid import UUID

from pydantic import BaseModel


class GenerationDTO(BaseModel):
    id: UUID
    status: str
    output_url: str | None = None


class GenerationUpdateDTO(BaseModel):
    status: str
    output_url: str | None = None
