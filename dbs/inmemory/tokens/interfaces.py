from abc import ABC, abstractmethod
from uuid import UUID

from dbs.inmemory.tokens.dbes import TokenUsageDBE


class TokenUsageDAOInterface(ABC):
    @abstractmethod
    async def create(self, generation_id: UUID, amount: int) -> TokenUsageDBE:
        raise NotImplementedError

    @abstractmethod
    async def get_by_generation_id(self, generation_id: UUID) -> TokenUsageDBE | None:
        raise NotImplementedError
