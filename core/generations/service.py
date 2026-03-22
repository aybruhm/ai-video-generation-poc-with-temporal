from uuid import UUID

from core.generations.dtos import GenerationDTO, GenerationUpdateDTO
from dbs.inmemory.generations.dbes import GenerationDBE
from dbs.inmemory.generations.interfaces import GenerationDAOInterface


class GenerationService:
    def __init__(self, dao: GenerationDAOInterface):
        self.generation_dao = dao

    def _map_dbe_to_dto(self, dbe: GenerationDBE) -> GenerationDTO:
        return GenerationDTO(
            id=dbe.id,  # type: ignore[arg-type]
            status=dbe.status,  # type: ignore[arg-type]
            output_url=dbe.output_url,  # type: ignore[arg-type]
        )

    async def get_generation(self, generation_id: UUID) -> GenerationDTO | None:
        generation_dbe = await self.generation_dao.get(generation_id=generation_id)
        if generation_dbe is None:
            return None

        generation_dto = self._map_dbe_to_dto(dbe=generation_dbe)
        return generation_dto

    async def update_generation(
        self,
        generation_id: UUID,
        update_dto: GenerationUpdateDTO,
    ) -> None:
        await self.generation_dao.update(
            generation_id=generation_id,
            values_to_update=update_dto.model_dump(),
        )
