from uuid import UUID

from sqlalchemy import select

from dbs.inmemory.engine import get_db_session
from dbs.inmemory.tokens.dbes import TokenUsageDBE
from dbs.inmemory.tokens.interfaces import TokenUsageDAOInterface


class TokenUsageDAO(TokenUsageDAOInterface):
    async def create(self, generation_id: UUID, amount: int) -> TokenUsageDBE:
        async with get_db_session() as session:
            usage_dbe = TokenUsageDBE(
                generation_id=generation_id,
                amount=amount,
            )
            session.add(usage_dbe)
            await session.commit()
            return usage_dbe

    async def get_by_generation_id(self, generation_id: UUID) -> TokenUsageDBE | None:
        async with get_db_session() as session:
            stmt = select(TokenUsageDBE).where(TokenUsageDBE.id == generation_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
