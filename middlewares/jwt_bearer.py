import logging
import traceback
from typing import Any, Dict
from uuid import UUID

from fastapi import Request
from fastapi.security import APIKeyCookie
from jwt import DecodeError, ExpiredSignatureError, decode
from starlette.exceptions import HTTPException

from core.users.service import UserService
from dbs.inmemory.users.dao import UserDAO
from services.exceptions import InternalServerErrorException, UnauthorizedException
from utils.env_utils import env
from utils.jwt import create_user_token_hash

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# JWT Configuration
_JWT_KEY = env.JWT_KEY
_JWT_ALGORITHM = env.JWT_ALGORITHM


class JWTCookie(APIKeyCookie):
    """
    JWT Cookie token authentication middleware for FastAPI.

    This class handles JWT token verification and user authentication
    from HTTP-only cookies with Redis caching for improved performance.
    """

    def __init__(
        self,
        auto_error: bool = True,
        name: str = "access_token",
    ):
        """
        Initialize the JWT Cookie authentication middleware.
        """

        self.user_service = UserService(dao=UserDAO())
        super().__init__(name=name, auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Main authentication method called for each request.
        """

        try:
            # Get the token from the cookie using the parent class method
            access_token = await super().__call__(request)
            if not access_token:
                raise UnauthorizedException(
                    detail="Invalid authentication scheme. Expected access_token from cookies.",
                )

            # Verify JWT token and set user context
            is_valid = await self.verify_jwt_token(
                request=request,
                token=access_token,
            )
            if not is_valid:
                raise UnauthorizedException(detail="Invalid token or expired token.")

            return access_token

        except UnauthorizedException as e:
            raise e
        except HTTPException as e:
            raise UnauthorizedException(detail="Not authenticated") from e
        except Exception:
            logger.error("Authentication error: %s", traceback.format_exc())
            raise InternalServerErrorException(
                detail="Authentication failed due to an internal error."
            )

    async def verify_jwt_token(
        self,
        request: Request,
        token: str,
    ) -> bool:
        """
        Verify JWT token and set user context in request state.

        Args:
            request (Request): The FastAPI request object.
            token (str): The JWT token to verify.

        Returns:
            bool: True if token is valid, False otherwise.
        """

        try:
            if not _JWT_KEY:
                raise InternalServerErrorException(
                    detail="JWT key not configured",
                )

            auth_context = await self.decode_jwt_token(token=token)
            if auth_context is None:
                return False

            user_id = auth_context.get("sub", "00000000-0000-0000-0000-000000000000")
            if hasattr(request.state, "user_id") and request.state.user_id != user_id:
                return False

            # Get user from database
            user = await self.user_service.get_user(user_id=UUID(user_id))
            if not user:
                return False

            # Verify user hash matches
            expected_hash = create_user_token_hash(
                str(user.id),  # type: ignore
                user.username,
            )
            if auth_context.get("uh") != expected_hash:
                return False

            # Set user context in request state
            request.state.user_id = UUID(user_id)
            request.state.username = user.username

            return True

        except DecodeError:
            logger.warning("Invalid JWT token format")
            return False
        except ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return False
        except Exception as e:
            logger.error("JWT verification error: %s", str(e))
            return False

    async def decode_jwt_token(
        self,
        token: str,
    ) -> Dict[str, Any] | None:
        try:
            auth_context = decode(
                jwt=token,
                key=_JWT_KEY,
                algorithms=[_JWT_ALGORITHM or "HS256"],
            )
            return auth_context
        except Exception as e:
            traceback.print_exc()
            logger.error("JWT decoding error: %s", str(e))
            return None

