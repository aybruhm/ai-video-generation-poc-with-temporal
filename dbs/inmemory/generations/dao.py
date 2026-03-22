from typing import Any
from uuid import UUID

from sqlalchemy import select

from dbs.inmemory.engine import get_db_session
from dbs.inmemory.generations.dbes import GenerationDBE
from dbs.inmemory.generations.interfaces import GenerationDAOInterface


class GenerationDAO(GenerationDAOInterface):
    async def get(self, generation_id: UUID) -> GenerationDBE | None:
        async with get_db_session() as session:
            stmt = select(GenerationDBE).where(GenerationDBE.id == generation_id)
            result = await session.execute(stmt)
            generation_dbe = result.scalar_one_or_none()
            return generation_dbe

    async def update(
        self,
        generation_id: UUID,
        values_to_update: dict[str, Any],
    ) -> None:
        async with get_db_session() as session:
            stmt = (
                select(GenerationDBE)
                .where(GenerationDBE.id == generation_id)
                .with_for_update()
            )
            result = await session.execute(stmt)
            generation_dbe = result.scalar_one_or_none()
            if generation_dbe is None:
                return None

            for key, value in values_to_update.items():
                if hasattr(generation_dbe, key):
                    setattr(generation_dbe, key, value)

            await session.commit()
