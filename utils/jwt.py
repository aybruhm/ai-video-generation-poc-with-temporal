import hashlib
import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jwt import encode

from services.exceptions import InternalServerErrorException
from utils.env_utils import env

# Configure logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# JWT Configuration
_JWT_KEY = env.JWT_KEY
_JWT_ACCESS_EXP = env.JWT_EXP  # 15 minutes default
_JWT_ALGORITHM = env.JWT_ALGORITHM
_JWT_REFRESH_EXP = (_JWT_ACCESS_EXP * 24 * 7) or 604800  # 7 days default


def create_user_token_hash(
    user_id: str,
    username: str,
) -> str:
    """
    Create unique hash for user.

    Args:
        user_id (str): The user's ID.
        username (str): The user's username.

    Returns:
        str: The unique hash for the user.
    """

    data = f"{user_id}:{username}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


async def sign_access_token(user_data: Dict[str, Any]) -> str:
    """
    Sign a JWT access token for a user.

    Args:
        user_data (dict): The user data.

    Returns:
        str: The signed JWT access token.

    Raises:
        InternalServerErrorException: If JWT key is not configured.
    """

    try:
        if not _JWT_KEY:
            raise InternalServerErrorException(
                detail="JWT key not configured",
            )

        exp_time = int(
            (
                datetime.now(timezone.utc) + timedelta(seconds=_JWT_ACCESS_EXP)
            ).timestamp()
        )

        auth_context = {
            "uh": create_user_token_hash(
                user_id=user_data["id"],
                username=user_data["username"],
            ),
            "sub": f"{user_data['id']}",
            "exp": exp_time,
            "token_type": "access",
        }

        access_token = encode(
            payload=auth_context,
            key=_JWT_KEY,
            algorithm=_JWT_ALGORITHM,
        )
        return access_token

    except Exception as exc:
        traceback.print_exc()
        raise InternalServerErrorException(
            detail="Failed to sign JWT access token",
        ) from exc


async def sign_refresh_token(user_data: Dict[str, Any]) -> str:
    """
    Sign a JWT refresh token for a user.

    Args:
        user_data (Dict[str, Any]): The user data.

    Returns:
        str: The signed JWT refresh token.

    Raises:
        InternalServerErrorException: If JWT key is not configured.
    """

    try:
        if not _JWT_KEY:
            raise InternalServerErrorException(
                detail="JWT key not configured",
            )

        exp_time = int(
            (
                datetime.now(timezone.utc) + timedelta(seconds=_JWT_REFRESH_EXP)
            ).timestamp()
        )

        auth_context = {
            "uh": create_user_token_hash(
                user_id=user_data["id"],
                username=user_data["username"],
            ),
            "sub": f"{user_data['id']}",
            "exp": exp_time,
            "token_type": "refresh",
        }

        refresh_token = encode(
            payload=auth_context,
            key=_JWT_KEY,
            algorithm=_JWT_ALGORITHM,
        )

        return refresh_token

    except Exception as exc:
        traceback.print_exc()
        raise InternalServerErrorException(
            detail="Failed to sign JWT refresh token",
        ) from exc
