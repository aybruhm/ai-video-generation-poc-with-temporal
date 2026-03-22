from abc import ABC, abstractmethod
from uuid import UUID

from dbs.inmemory.users.dbes import UserDBE


class UserDAOInterface(ABC):
    @abstractmethod
    async def create(self, user_dbe: UserDBE) -> UserDBE:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserDBE | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UserDBE | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user_id: UUID, values_to_update: dict) -> UserDBE | None:
        raise NotImplementedError
