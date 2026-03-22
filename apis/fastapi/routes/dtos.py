import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from core.generations.dtos import StartGenerationRequestDTO
from core.users.dtos import LoginUserDTO, RegisterUserDTO

# ================= DTOs for the video generation API


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


# ================= DTOs for the auth API


class RegisterUserRequestDTO(RegisterUserDTO):
    pass


class LoginUserRequestDTO(LoginUserDTO):
    pass


class JWTTokensDTO(BaseModel):
    access_token: str
    refresh_token: str


class CredentialsDTO(JWTTokensDTO):
    pass


class RefreshTokensRequestDTO(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    token_balance: int
    created_at: datetime


class UserWithCredentialsResponse(BaseModel):
    user: UserResponse
    credentials: CredentialsDTO
