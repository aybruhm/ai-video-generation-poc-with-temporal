from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID

from dbs.inmemory.generations.dbes import GenerationDBE


class GenerationDAOInterface(ABC):
    @abstractmethod
    async def get(self, generation_id: UUID) -> GenerationDBE | None:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        generation_id: UUID,
        values_to_update: Dict[str, Any],
    ) -> None:
        raise NotImplementedError
