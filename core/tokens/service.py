from uuid import UUID

from core.tokens.dtos import TokenUsageCreateDTO, TokenUsageDTO
from dbs.inmemory.tokens.interfaces import TokenUsageDAOInterface, TokenUsageDBE


class TokenService:
    def __init__(self, dao: TokenUsageDAOInterface):
        self.token_dao = dao

    def _map_dbe_to_dto(self, dbe: TokenUsageDBE) -> TokenUsageDTO:
        return TokenUsageDTO(
            id=dbe.id,  # type: ignore[arg-type]
            generation_id=dbe.generation_id,  # type: ignore[arg-type]
            amount=dbe.amount,  # type: ignore[arg-type]
            created_at=dbe.created_at,  # type: ignore[arg-type]
        )

    async def create(self, create_dto: TokenUsageCreateDTO):
        usage_dbe = await self.token_dao.create(
            generation_id=UUID(create_dto.generation_id),
            amount=create_dto.amount,
        )
        usage_dto = self._map_dbe_to_dto(dbe=usage_dbe)
        return usage_dto

    async def get_by_generation_id(self, generation_id: UUID):
        usage_dbe = await self.token_dao.get_by_generation_id(
            generation_id=generation_id
        )
        if usage_dbe is None:
            return None

        usage_dto = self._map_dbe_to_dto(dbe=usage_dbe)
        return usage_dto
