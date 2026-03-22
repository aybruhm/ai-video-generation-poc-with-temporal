from uuid import UUID

from pydantic import BaseModel


class GenerationDTO(BaseModel):
    id: UUID
    status: str
    output_url: str | None = None


class GenerationUpdateDTO(BaseModel):
    status: str
    output_url: str | None = None


class StartGenerationRequestDTO(BaseModel):
    prompt: str
    model: str
    duration: str | int
    aspect_ratio: str = "16:9"
    token_cost: int


class StartGenerationResponseDTO(BaseModel):
    generation_id: str
    handle_id: str