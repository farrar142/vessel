"""
Type markers for HTTP header and cookie injection
"""

from typing import Optional, Annotated, get_origin, get_args


class HttpHeader:
    """
    Type marker for HTTP header injection.

    When used as a type hint, the framework will inject the corresponding HTTP header value.

    Two usage patterns are supported:
    1. Auto-conversion from parameter name (snake_case -> Title-Case):
        def get_user(self, user_agent: HttpHeader):
            # user_agent -> User-Agent header
            pass

    2. Explicit header name specification:
        def get_user(self, agent: HttpHeader["User-Agent"]):
            # agent parameter gets User-Agent header value
            pass
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize HttpHeader with optional explicit name.

        Args:
            name: Explicit header name (e.g., "User-Agent", "Content-Type")
                  If None, parameter name will be auto-converted.
        """
        self.name = name

    @classmethod
    def __class_getitem__(cls, name: str):
        """
        Support HttpHeader["User-Agent"] syntax for type annotations.
        Returns Annotated[HttpHeader, name] which can be used in type hints.
        """
        return Annotated[cls, name]


class HttpCookie:
    """
    Type marker for HTTP cookie injection.

    When used as a type hint, the framework will inject the corresponding cookie value.

    Two usage patterns are supported:
    1. Auto-match with parameter name:
        def get_user(self, session_id: HttpCookie):
            # session_id -> session_id cookie
            pass

    2. Explicit cookie name specification:
        def get_user(self, token: HttpCookie["access_token"]):
            # token parameter gets access_token cookie value
            pass
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize HttpCookie with optional explicit name.

        Args:
            name: Explicit cookie name (e.g., "session_id", "access_token")
                  If None, parameter name will be used as-is.
        """
        self.name = name

    @classmethod
    def __class_getitem__(cls, name: str):
        """
        Support HttpCookie["session_id"] syntax for type annotations.
        Returns Annotated[HttpCookie, name] which can be used in type hints.
        """
        return Annotated[cls, name]
