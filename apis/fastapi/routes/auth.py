from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse

from core.users.auth import AuthService
from middlewares.jwt_bearer import JWTCookie
from services.dependencies import get_current_user
from services.exceptions import BadRequestException, UnauthorizedException
from utils.jwt import (
    _JWT_ACCESS_EXP,
    _JWT_REFRESH_EXP,
    sign_access_token,
    sign_refresh_token,
)

from .dtos import (
    CredentialsDTO,
    JWTTokensDTO,
    LoginUserRequestDTO,
    RegisterUserRequestDTO,
    UserResponse,
    UserWithCredentialsResponse,
)


class UsersAuthAPIRouter:
    def __init__(
        self,
        jwt_cookie: JWTCookie,
        auth_service: AuthService,
    ):
        self.jwt_cookie = jwt_cookie
        self.auth_service = auth_service
        self.users_service = auth_service.user_service

        self.router = APIRouter(prefix="/auth", tags=["Auth"])

        # register routes
        self.router.add_api_route(
            "/register",
            self.register_user,
            methods=["POST"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/login",
            self.login_user,
            methods=["POST"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/me",
            self.get_user,
            methods=["GET"],
            dependencies=[Depends(get_current_user)],
            response_model=UserResponse,
        )

    def _set_http_only_cookies(
        self,
        *,
        response: Response,
        access_token: str,
        refresh_token: str,
    ):
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=_JWT_ACCESS_EXP,
            httponly=True,
            secure=False,  #! NOTE: set secure=True in production
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=_JWT_REFRESH_EXP,
            httponly=True,
            secure=False,  #! NOTE: set secure=True in production
            samesite="lax",
        )

    async def register_user(
        self,
        request: Request,
        register_dto: RegisterUserRequestDTO,
    ):
        """Create a new user profile."""

        existing_user = await self.users_service.get_user_by_username(
            username=register_dto.username
        )
        if existing_user:
            raise BadRequestException(
                detail="Account already registered",
            )

        user = await self.auth_service.register(register_dto=register_dto)
        return user

    async def login_user(self, request: Request, login_dto: LoginUserRequestDTO):
        user = await self.auth_service.login(login_dto=login_dto)
        if not user:
            raise BadRequestException(detail="Email or password is incorrect")

        access_token = await sign_access_token(
            user_data={
                "id": user.id,
                "username": user.username,
            }
        )
        refresh_token = await sign_refresh_token(
            user_data={
                "id": user.id,
                "username": user.username,
            }
        )

        user_response = UserResponse(**user.model_dump())
        credentials_response = CredentialsDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        uwc_response = UserWithCredentialsResponse(
            user=user_response,
            credentials=credentials_response,
        )

        response = JSONResponse(content=uwc_response.model_dump(mode="json"))
        self._set_http_only_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return response

    async def verify(self, request: Request):
        try:
            # Use the middleware to verify the token
            await self.jwt_cookie(request)
            return True
        except UnauthorizedException as e:
            raise e
        except Exception:
            raise UnauthorizedException(
                detail="Your session has expired or is invalid. Please log in again to continue."
            )

    async def get_user(
        self,
        request: Request,
    ):
        """Get user profile by ID."""

        user = await self.users_service.get_user(user_id=request.state.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
