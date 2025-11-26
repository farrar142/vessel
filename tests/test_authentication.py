"""
Authentication System 테스트
"""

import pytest
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Get, Post
from vessel.web.application import Application
from vessel.web.http.request import HttpRequest
from vessel.web.auth import AuthMiddleware, Authentication, Authenticator
from vessel.decorators.di.component import Component


class TestBasicAuthentication:
    """기본 인증 테스트"""

    def test_authentication_injection(self):
        """Authentication 객체가 성공적으로 주입되는지 테스트"""

        # 테스트용 인증기 구현
        class TestAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                # Authorization 헤더에서 토큰 추출
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == "valid_token":
                        return Authentication(
                            user_id="user123", username="testuser", authenticated=True
                        )
                return None

            def supports(self, request: HttpRequest) -> bool:
                auth_header = request.headers.get("Authorization")
                return auth_header is not None and auth_header.startswith("Bearer ")

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(TestAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class UserController:
            @Get("/profile")
            def get_profile(self, authentication: Authentication) -> dict:
                return {
                    "user_id": authentication.user_id,
                    "username": authentication.username,
                    "authenticated": authentication.authenticated,
                }

        app = Application("__main__")
        app.initialize()

        # 인증된 요청
        request = HttpRequest(
            method="GET",
            path="/api/profile",
            headers={"Authorization": "Bearer valid_token"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_id"] == "user123"
        assert response.body["username"] == "testuser"
        assert response.body["authenticated"] is True

    def test_authentication_failure(self):
        """인증 실패 시 401 에러 반환 테스트"""

        class TestAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == "valid_token":
                        return Authentication(user_id="user123", authenticated=True)
                return None

            def supports(self, request: HttpRequest) -> bool:
                return request.headers.get("Authorization") is not None

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(TestAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class SecureController:
            @Get("/secure")
            def secure_endpoint(self, authentication: Authentication) -> dict:
                return {"message": "secure data"}

        app = Application("__main__")
        app.initialize()

        # 인증 헤더 없음
        request = HttpRequest(method="GET", path="/api/secure")

        response = app.handle_request(request)
        assert response.status_code == 401
        assert "authentication required" in response.body.get("message", "").lower()

    def test_invalid_token(self):
        """잘못된 토큰으로 인증 실패 테스트"""

        class TestAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == "valid_token":
                        return Authentication(user_id="user123", authenticated=True)
                return None

            def supports(self, request: HttpRequest) -> bool:
                return request.headers.get("Authorization") is not None

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(TestAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class SecureController:
            @Get("/data")
            def get_data(self, authentication: Authentication) -> dict:
                return {"data": "secret"}

        app = Application("__main__")
        app.initialize()

        # 잘못된 토큰
        request = HttpRequest(
            method="GET",
            path="/api/data",
            headers={"Authorization": "Bearer invalid_token"},
        )

        response = app.handle_request(request)
        assert response.status_code == 401


class TestMultipleAuthenticators:
    """여러 인증기 등록 테스트"""

    def test_multiple_authenticators(self):
        """여러 인증기 중 적절한 것이 선택되는지 테스트"""

        class BearerAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == "bearer_token":
                        return Authentication(
                            user_id="bearer_user",
                            auth_type="bearer",
                            authenticated=True,
                        )
                return None

            def supports(self, request: HttpRequest) -> bool:
                auth_header = request.headers.get("Authorization")
                return auth_header is not None and auth_header.startswith("Bearer ")

        class ApiKeyAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                api_key = request.headers.get("X-API-Key")
                if api_key == "valid_api_key":
                    return Authentication(
                        user_id="api_user", auth_type="apikey", authenticated=True
                    )
                return None

            def supports(self, request: HttpRequest) -> bool:
                return request.headers.get("X-API-Key") is not None

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(BearerAuthenticator())
                self.register(ApiKeyAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class ResourceController:
            @Get("/resource")
            def get_resource(self, authentication: Authentication) -> dict:
                return {
                    "user_id": authentication.user_id,
                    "auth_type": authentication.auth_type,
                }

        app = Application("__main__")
        app.initialize()

        # Bearer 인증
        request1 = HttpRequest(
            method="GET",
            path="/api/resource",
            headers={"Authorization": "Bearer bearer_token"},
        )
        response1 = app.handle_request(request1)
        assert response1.status_code == 200
        assert response1.body["auth_type"] == "bearer"

        # API Key 인증
        request2 = HttpRequest(
            method="GET",
            path="/api/resource",
            headers={"X-API-Key": "valid_api_key"},
        )
        response2 = app.handle_request(request2)
        assert response2.status_code == 200
        assert response2.body["auth_type"] == "apikey"


class TestCustomAuthentication:
    """사용자 정의 Authentication 클래스 테스트"""

    def test_custom_authentication_class(self):
        """Authentication을 확장한 커스텀 클래스 사용 테스트"""

        # 커스텀 Authentication 클래스
        class UserAuthentication(Authentication):
            def __init__(self, user_id: str, username: str, roles: list[str], **kwargs):
                super().__init__(user_id=user_id, authenticated=True, **kwargs)
                self.username = username
                self.roles = roles

            def has_role(self, role: str) -> bool:
                return role in self.roles

        class JwtAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> UserAuthentication:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    # 간단한 JWT 파싱 시뮬레이션
                    if token == "admin_jwt_token":
                        return UserAuthentication(
                            user_id="admin123",
                            username="admin",
                            roles=["admin", "user"],
                        )
                    elif token == "user_jwt_token":
                        return UserAuthentication(
                            user_id="user456", username="john", roles=["user"]
                        )
                return None

            def supports(self, request: HttpRequest) -> bool:
                auth_header = request.headers.get("Authorization")
                return auth_header is not None and auth_header.startswith("Bearer ")

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(JwtAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class AdminController:
            @Get("/admin")
            def admin_panel(self, authentication: UserAuthentication) -> dict:
                if authentication.has_role("admin"):
                    return {
                        "message": "Welcome Admin",
                        "username": authentication.username,
                    }
                return {"error": "Forbidden"}

        app = Application("__main__")
        app.initialize()

        # Admin 사용자
        request = HttpRequest(
            method="GET",
            path="/api/admin",
            headers={"Authorization": "Bearer admin_jwt_token"},
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["message"] == "Welcome Admin"
        assert response.body["username"] == "admin"


class TestOptionalAuthentication:
    """선택적 인증 테스트"""

    def test_optional_authentication(self):
        """Optional[Authentication]으로 선택적 인증 지원 테스트"""

        class TestAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == "valid_token":
                        return Authentication(user_id="user123", authenticated=True)
                return None

            def supports(self, request: HttpRequest) -> bool:
                return request.headers.get("Authorization") is not None

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(TestAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory
        from typing import Optional

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class PublicController:
            @Get("/content")
            def get_content(
                self, authentication: Optional[Authentication] = None
            ) -> dict:
                if authentication and authentication.authenticated:
                    return {
                        "content": "premium content",
                        "user": authentication.user_id,
                    }
                return {"content": "free content"}

        app = Application("__main__")
        app.initialize()

        # 인증된 요청
        request1 = HttpRequest(
            method="GET",
            path="/api/content",
            headers={"Authorization": "Bearer valid_token"},
        )
        response1 = app.handle_request(request1)
        assert response1.status_code == 200
        assert response1.body["content"] == "premium content"

        # 인증 없는 요청
        request2 = HttpRequest(method="GET", path="/api/content")
        response2 = app.handle_request(request2)
        assert response2.status_code == 200
        assert response2.body["content"] == "free content"


class TestAuthMiddlewareFactory:
    """AuthMiddleware Factory 패턴 테스트"""

    def test_factory_method_with_container(self):
        """Factory 메서드로 AuthMiddleware를 컨테이너에 등록하고 사용"""

        class TestAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                token = request.headers.get("Authorization", "").replace("Bearer ", "")
                if token == "factory_token":
                    return Authentication(user_id="factory_user", authenticated=True)
                return None

            def supports(self, request: HttpRequest) -> bool:
                return request.headers.get("Authorization") is not None

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(TestAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class TestController:
            @Get("/test")
            def test_endpoint(self, authentication: Authentication) -> dict:
                return {"user": authentication.user_id}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/test",
            headers={"Authorization": "Bearer factory_token"},
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user"] == "factory_user"


class TestAuthenticatorPriority:
    """인증기 우선순위 테스트"""

    def test_authenticator_execution_order(self):
        """인증기가 등록 순서대로 실행되는지 테스트"""

        execution_order = []

        class FirstAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                execution_order.append("first")
                return None

            def supports(self, request: HttpRequest) -> bool:
                return True

        class SecondAuthenticator(Authenticator):
            def authenticate(self, request: HttpRequest) -> Authentication:
                execution_order.append("second")
                if request.headers.get("X-Auth") == "valid":
                    return Authentication(user_id="user", authenticated=True)
                return None

            def supports(self, request: HttpRequest) -> bool:
                return True

        @Component
        class TestAuthMiddleware(AuthMiddleware):
            def __init__(self):
                super().__init__()
                self.register(FirstAuthenticator())
                self.register(SecondAuthenticator())

        from vessel.web.middleware.chain import MiddlewareChain
        from vessel.decorators.di.configuration import Configuration
        from vessel.decorators.di.factory import Factory

        @Configuration
        class MiddlewareConfig:
            @Factory
            def middleware_chain(
                self, auth_middleware: TestAuthMiddleware
            ) -> MiddlewareChain:
                chain = MiddlewareChain()
                chain.get_default_group().add(auth_middleware)
                return chain

        @Controller("/api")
        class TestController:
            @Get("/test")
            def test(self, authentication: Authentication) -> dict:
                return {"ok": True}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/test", headers={"X-Auth": "valid"}
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert execution_order == ["first", "second"]
