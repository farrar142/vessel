"""
Authentication Middleware and Components
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from vessel.http.request import HttpRequest
from vessel.web.middleware.chain import Middleware


class Authentication:
    """
    기본 인증 정보 클래스

    사용자는 이 클래스를 확장하여 자신만의 인증 정보를 담을 수 있습니다.

    Example:
        class UserAuthentication(Authentication):
            def __init__(self, user_id: str, username: str, roles: list[str], **kwargs):
                super().__init__(user_id=user_id, authenticated=True, **kwargs)
                self.username = username
                self.roles = roles
    """

    def __init__(self, user_id: str = None, authenticated: bool = False, **kwargs):
        self.user_id = user_id
        self.authenticated = authenticated
        # 추가 속성들을 동적으로 저장
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class Authenticator(ABC):
    """
    인증기 추상 클래스

    프레임워크는 이 추상 클래스만 제공하며,
    사용자는 JWT, HTTP Bearer, Token 등의 구체적인 인증 방식을 구현해야 합니다.

    Example:
        class JwtAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                token = self.extract_token(request)
                payload = jwt.decode(token, SECRET_KEY)
                return Authentication(
                    user_id=payload['user_id'],
                    authenticated=True
                )

            def supports(self, request: HttpRequest) -> bool:
                return 'Authorization' in request.headers
    """

    @abstractmethod
    def authenticate(self, request: HttpRequest) -> Optional[Authentication]:
        """
        요청을 인증하고 Authentication 객체를 반환합니다.

        Args:
            request: HTTP 요청 객체

        Returns:
            인증 성공 시 Authentication 또는 그 하위 클래스 인스턴스
            인증 실패 시 None
        """
        pass

    @abstractmethod
    def supports(self, request: HttpRequest) -> bool:
        """
        이 인증기가 해당 요청을 처리할 수 있는지 확인합니다.

        Args:
            request: HTTP 요청 객체

        Returns:
            처리 가능하면 True, 아니면 False
        """
        pass


class AuthenticatorRegistry:
    """
    인증기들을 관리하는 레지스트리
    """

    def __init__(self):
        self._authenticators: list[Authenticator] = []

    def register(self, authenticator: Authenticator) -> None:
        """
        인증기를 레지스트리에 등록합니다.

        Args:
            authenticator: 등록할 인증기
        """
        if not isinstance(authenticator, Authenticator):
            raise TypeError(
                f"Expected Authenticator instance, got {type(authenticator).__name__}"
            )
        self._authenticators.append(authenticator)

    def authenticate(self, request: HttpRequest) -> Optional[Authentication]:
        """
        등록된 인증기들을 순회하며 인증을 시도합니다.

        Args:
            request: HTTP 요청 객체

        Returns:
            첫 번째로 성공한 인증 결과, 모두 실패하면 None
        """
        for authenticator in self._authenticators:
            if authenticator.supports(request):
                authentication = authenticator.authenticate(request)
                if authentication is not None:
                    return authentication
        return None

    def has_authenticators(self) -> bool:
        """등록된 인증기가 있는지 확인"""
        return len(self._authenticators) > 0


class AuthMiddleware(Middleware):
    """
    인증 미들웨어

    등록된 인증기들을 사용하여 요청을 인증하고,
    컨트롤러 메서드에서 Authentication을 주입받을 수 있도록 합니다.

    Usage:
        # 1. 인증기 구현
        class JwtAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                # JWT 토큰 검증 로직
                token = self.extract_token(request)
                if self.verify_token(token):
                    return Authentication(user_id="user123", authenticated=True)
                return None
            
            def supports(self, request: HttpRequest) -> bool:
                return "Authorization" in request.headers

        # 2. AuthMiddleware를 Component로 등록하고 인증기 추가
        @Component
        class AppAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(JwtAuthenticator())
                self.register(ApiKeyAuthenticator())

        # 3. MiddlewareChain을 Factory로 생성
        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(self, auth_middleware: AppAuthMiddleware) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        # 4. 컨트롤러에서 사용
        @Controller("/api")
        class UserController:
            @Get("/profile")
            def get_profile(self, authentication: Authentication):
                return {"user_id": authentication.user_id}
            
            @Get("/public")
            def public_data(self, authentication: Optional[Authentication] = None):
                if authentication and authentication.authenticated:
                    return {"content": "premium"}
                return {"content": "free"}
    """

    def __init__(self):
        self._registry = AuthenticatorRegistry()

    def register(self, authenticator: Authenticator) -> None:
        """
        인증기를 등록합니다.

        Args:
            authenticator: 등록할 인증기
        """
        self._registry.register(authenticator)

    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """
        요청 처리 전 인증 수행

        Args:
            request: HTTP 요청

        Returns:
            None (항상 다음 핸들러로 진행)
        """
        # 인증 시도
        authentication = self._registry.authenticate(request)

        # 인증 결과를 request에 저장
        if not hasattr(request, "_auth_data"):
            request._auth_data = {}
        request._auth_data["authentication"] = authentication

        # 다음 핸들러로 진행
        return None

    def process_response(self, request: HttpRequest, response: Any) -> Any:
        """
        응답 처리 (아무 작업도 하지 않음)

        Args:
            request: HTTP 요청
            response: HTTP 응답

        Returns:
            원본 응답 그대로 반환
        """
        return response

    def has_authenticators(self) -> bool:
        """등록된 인증기가 있는지 확인"""
        return self._registry.has_authenticators()
