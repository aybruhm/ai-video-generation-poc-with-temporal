from core.users.dtos import LoginUserDTO, RegisterUserDTO, UserDTO
from core.users.service import UserDBE, UserService
from utils.password import hash_password, verify_password


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def _map_dto_to_dbe(self, dto: RegisterUserDTO) -> UserDBE:
        return UserDBE(
            username=dto.username,
            password=hash_password(dto.password),
        )

    def _map_dbe_to_dto(self, dbe: UserDBE) -> UserDTO:
        return self.user_service._map_dbe_to_dto(
            dbe=dbe,
        )

    async def register(self, register_dto: RegisterUserDTO) -> UserDTO:
        user_dbe = self._map_dto_to_dbe(register_dto)
        user_dto = await self.user_service.create_user(user_dbe=user_dbe)
        return user_dto

    async def login(self, login_dto: LoginUserDTO) -> UserDTO | None:
        user_dbe = await self.user_service.user_dao.get_by_username(
            username=login_dto.username
        )
        if not user_dbe:
            return None

        if verify_password(
            stored_password=user_dbe.password,  # type: ignore
            provided_password=login_dto.password,
        ):
            return self._map_dbe_to_dto(dbe=user_dbe)

        return None
