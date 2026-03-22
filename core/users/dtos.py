from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
