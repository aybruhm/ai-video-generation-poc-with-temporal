from uuid import UUID, uuid4

from core.users.dtos import UserCreateDTO, UserDTO, UserUpdateDTO
from dbs.inmemory.users.interfaces import UserDAOInterface, UserDBE


class UserService:
    def __init__(self, dao: UserDAOInterface):
        self.user_dao = dao

    def _map_dto_to_dbe(self, dto: UserCreateDTO) -> UserDBE:
        return UserDBE(
            id=uuid4(),
            username=dto.username,
        )

    def _map_dbe_to_dto(self, dbe: UserDBE) -> UserDTO:
        return UserDTO.model_validate(
            obj=dbe,
            from_attributes=True,
        )

    async def create_user(self, create_dto: UserCreateDTO) -> UserDTO:
        user_dbe = self._map_dto_to_dbe(create_dto)
        user_dbe = await self.user_dao.create(user_dbe)
        user_dto = self._map_dbe_to_dto(dbe=user_dbe)
        return user_dto

    async def get_user(self, user_id: UUID) -> UserDTO | None:
        user_dbe = await self.user_dao.get_by_id(user_id)
        if user_dbe is None:
            return None
        user_dto = self._map_dbe_to_dto(user_dbe)
        return user_dto

    async def update_user(
        self, user_id: UUID, update_dto: UserUpdateDTO
    ) -> UserDTO | None:
        user_dbe = await self.user_dao.update(
            user_id=user_id,
            values_to_update=update_dto.model_dump(
                exclude_unset=True,
            ),
        )
        if user_dbe is None:
            return None

        user_dto = self._map_dbe_to_dto(user_dbe)
        return user_dto

    async def deduct_tokens(self, user_id: UUID, amount: int) -> UserDTO | None:
        user_dbe = await self.user_dao.get_by_id(user_id=user_id)
        if user_dbe is None:
            return None

        if user_dbe.token_balance < amount:  # type: ignore
            raise ValueError(
                f"Insufficient token balance: {user_dbe.token_balance} < {amount}"
            )

        user_dbe.token_balance -= amount  # type: ignore
        user_dbe = await self.user_dao.update(
            user_id=user_id,
            values_to_update={"token_balance": user_dbe.token_balance},
        )
        if not user_dbe:
            return None

        user_dto = self._map_dbe_to_dto(dbe=user_dbe)
        return user_dto
