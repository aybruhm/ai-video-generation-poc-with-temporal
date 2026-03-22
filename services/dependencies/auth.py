from fastapi import Depends, Request

from middlewares.jwt_bearer import JWTCookie
from services.dependencies.types import CurrentUserContext
from services.exceptions import UnauthorizedException


class AuthDependencies:
    """
    Authentication dependencies for FastAPI routes.
    """

    @staticmethod
    def get_current_user(
        request: Request,
        token: str = Depends(JWTCookie()),
    ) -> CurrentUserContext:
        """
        Get the current authenticated user from the request.
        """

        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", None)

        if not user_id or not username:
            raise UnauthorizedException(detail="User information not available")

        user_context = CurrentUserContext(
            id=user_id,
            username=username,
            token=token,
        )
        return user_context
