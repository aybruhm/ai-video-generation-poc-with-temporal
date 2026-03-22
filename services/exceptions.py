from http import HTTPStatus
from typing import TypedDict, Unpack

from fastapi import HTTPException


class ForbiddenExceptionKwargs(TypedDict, total=False):
    """Additional keyword arguments for ForbiddenException.

    Attributes:
        reason: The reason for the forbidden action
        status: The subscription status of the user
    """

    reason: str
    status: str


def code_to_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Unknown Status Code"


class BadRequestException(HTTPException):
    def __init__(
        self,
        code: int = 400,
        detail: str = "Bad Request",
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail})


class NotFoundException(HTTPException):
    def __init__(
        self,
        code: int = 404,
        detail: str = "Not Found",
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail})


class UnauthorizedException(HTTPException):
    def __init__(
        self,
        code: int = 401,
        detail: str = "Unauthorized",
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail})


class ForbiddenException(HTTPException):
    def __init__(
        self,
        code: int = HTTPStatus.FORBIDDEN,
        detail: str = "Forbidden",
        **kwargs: Unpack[ForbiddenExceptionKwargs],
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail, **kwargs})


class UnprocessableContentException(HTTPException):
    def __init__(
        self,
        code: int = 422,
        detail: str = "Unprocessable Content",
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail})


class InternalServerErrorException(HTTPException):
    def __init__(
        self,
        code: int = 500,
        detail: str = "Internal Server Error",
    ):
        self.code = code
        self.detail = detail

        super().__init__(self.code, {"message": self.detail})
