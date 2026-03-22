from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreateDTO(BaseModel):
    username: str


class UserUpdateDTO(BaseModel):
    username: str | None = None
    token_balance: int | None = None


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    token_balance: int
    created_at: datetime


class RegisterUserDTO(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str


class LoginUserDTO(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str
