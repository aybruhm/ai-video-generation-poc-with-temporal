from uuid import UUID

from temporalio import activity

from core.temporal.types import DeductTokensDTO
from core.tokens.service import TokenService, TokenUsageCreateDTO
from core.users.service import UserService
from dbs.inmemory.tokens.dao import TokenUsageDAO
from dbs.inmemory.users.dao import UserDAO

# Initialize DAOs
user_dao = UserDAO()
token_dao = TokenUsageDAO()

# Initialize services
user_service = UserService(dao=user_dao)
token_service = TokenService(dao=token_dao)


@activity.defn
async def deduct_tokens(input: DeductTokensDTO) -> None:
    """
    Deducts tokens post-generation. Uses generation_id as idempotency key
    so retries don't double-deduct.
    """

    user = await user_service.get_user(user_id=UUID(input.user_id))
    if not user:
        raise ValueError(f"User {input.user_id} not found")

    # Check idempotency — if already deducted for this generation, skip
    token_usage = await token_service.get_by_generation_id(
        generation_id=UUID(input.generation_id)
    )
    if token_usage:
        activity.logger.warning(
            f"Token deduction for {input.generation_id} already recorded. Skipping."
        )
        return

    await token_service.create(
        TokenUsageCreateDTO(
            generation_id=input.generation_id,
            amount=input.amount,
        )
    )
    await user_service.deduct_tokens(
        user_id=UUID(input.user_id),
        amount=input.amount,
    )

    activity.logger.info(f"Deducted {input.amount} tokens from user {input.user_id}")
