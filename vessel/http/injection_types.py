"""
HTTP header and cookie value objects for injection
"""

from typing import Optional, Annotated


class HttpHeader:
    """
    HTTP header value object.

    When used as a type hint, the framework will inject the corresponding HTTP header value.

    Two usage patterns are supported:
    1. Auto-conversion from parameter name (snake_case -> Title-Case):
        def get_user(self, user_agent: HttpHeader):
            # user_agent.name -> "User-Agent"
            # user_agent.value -> "Mozilla/5.0 ..."
            pass

    2. Explicit header name specification:
        def get_user(self, agent: HttpHeader["User-Agent"]):
            # agent.name -> "User-Agent"
            # agent.value -> "Mozilla/5.0 ..."
            pass
    """

    def __init__(self, name: str, value: str):
        """
        Initialize HttpHeader with name and value.

        Args:
            name: Header name (e.g., "User-Agent", "Content-Type")
            value: Header value
        """
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"HttpHeader(name='{self.name}', value='{self.value}')"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def __class_getitem__(cls, name: str):
        """
        Support HttpHeader["User-Agent"] syntax for type annotations.
        Returns Annotated[HttpHeader, name] which can be used in type hints.
        """
        return Annotated[cls, name]


class HttpCookie:
    """
    HTTP cookie value object.

    When used as a type hint, the framework will inject the corresponding cookie value.

    Two usage patterns are supported:
    1. Auto-match with parameter name:
        def get_user(self, session_id: HttpCookie):
            # session_id.name -> "session_id"
            # session_id.value -> "abc123..."
            pass

    2. Explicit cookie name specification:
        def get_user(self, token: HttpCookie["access_token"]):
            # token.name -> "access_token"
            # token.value -> "xyz789..."
            pass
    """

    def __init__(self, name: str, value: str):
        """
        Initialize HttpCookie with name and value.

        Args:
            name: Cookie name (e.g., "session_id", "access_token")
            value: Cookie value
        """
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"HttpCookie(name='{self.name}', value='{self.value}')"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def __class_getitem__(cls, name: str):
        """
        Support HttpCookie["session_id"] syntax for type annotations.
        Returns Annotated[HttpCookie, name] which can be used in type hints.
        """
        return Annotated[cls, name]
