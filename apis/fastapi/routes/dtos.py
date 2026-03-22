from datetime import datetime

from pydantic import BaseModel

from core.generations.dtos import StartGenerationRequestDTO


class GenerateVideoRequestDTO(StartGenerationRequestDTO):
    pass


class GenerationRunResponseDTO(BaseModel):
    generation_id: str
    workflow_id: str
    status: str


class GenerationStatusResponseDTO(BaseModel):
    generation_id: str
    status: str | None
    start_time: datetime
