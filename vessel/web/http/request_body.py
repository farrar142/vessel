"""
RequestBody type for automatic body to dataclass conversion
"""

from typing import TYPE_CHECKING, TypeVar, Generic, Annotated, get_args

T = TypeVar("T")


class RequestBodyType(Generic[T]):
    """
    Type marker for automatic request body conversion to dataclass.

    Usage:
        from dataclasses import dataclass

        @dataclass
        class UserData:
            username: str
            age: int

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, body: RequestBody[UserData]) -> dict:
                # body is automatically converted to UserData instance
                return {"username": body.username, "age": body.age}

    Note: Do not instantiate this class directly. Use as type hint only.
    """

    def __class_getitem__(cls, item):
        """Support RequestBody[DataClass] syntax"""
        return Annotated[cls, item]


if TYPE_CHECKING:
    type RequestBody[T] = Annotated[T, RequestBodyType[T]]
else:
    RequestBody = RequestBodyType
