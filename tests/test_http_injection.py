"""
Test HTTP Header and Cookie injection with value objects
"""

import pytest
from typing import Optional
from vessel.web.http.injection_types import HttpHeader, HttpCookie
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Get
from vessel.web.application import Application
from vessel.web.http.request import HttpRequest


class TestHttpHeaderInjection:
    """Test HTTP header injection with HttpHeader type"""

    def test_inject_single_header(self):
        """Test injecting a single HTTP header with name and value"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, user_agent: HttpHeader) -> dict:
                return {
                    "name": user_agent.name,
                    "value": user_agent.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", headers={"User-Agent": "Mozilla/5.0"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["name"] == "User-Agent"
        assert response.body["value"] == "Mozilla/5.0"

    def test_inject_multiple_headers(self):
        """Test injecting multiple HTTP headers"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, user_agent: HttpHeader, host: HttpHeader) -> dict:
                return {
                    "user_agent": user_agent.value,
                    "user_agent_name": user_agent.name,
                    "host": host.value,
                    "host_name": host.name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0", "Host": "example.com"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["user_agent_name"] == "User-Agent"
        assert response.body["host"] == "example.com"
        assert response.body["host_name"] == "Host"

    def test_header_name_conversion(self):
        """Test parameter name to header name conversion (snake_case -> Title-Case)"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, content_type: HttpHeader, accept_language: HttpHeader
            ) -> dict:
                return {
                    "content_type": content_type.value,
                    "content_type_name": content_type.name,
                    "accept_language": accept_language.value,
                    "accept_language_name": accept_language.name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"Content-Type": "application/json", "Accept-Language": "en-US"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["content_type"] == "application/json"
        assert response.body["content_type_name"] == "Content-Type"
        assert response.body["accept_language"] == "en-US"
        assert response.body["accept_language_name"] == "Accept-Language"

    def test_missing_required_header(self):
        """Test missing required header raises error"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, authorization: HttpHeader) -> dict:
                return {"auth": authorization.value}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/user", headers={})

        response = app.handle_request(request)
        assert response.status_code == 400
        assert "authorization" in response.body[
            "error"
        ].lower() or "Authorization" in str(response.body)

    def test_optional_header(self):
        """Test optional HTTP header with Optional type hint"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, authorization: Optional[HttpHeader] = None) -> dict:
                if authorization:
                    return {"auth": authorization.value, "name": authorization.name}
                return {"auth": None}

        app = Application("__main__")
        app.initialize()

        # Test without header
        request = HttpRequest(method="GET", path="/api/user", headers={})

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] is None

        # Test with header
        request = HttpRequest(
            method="GET", path="/api/user", headers={"Authorization": "Bearer token123"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] == "Bearer token123"
        assert response.body["name"] == "Authorization"


class TestHttpCookieInjection:
    """Test HTTP cookie injection with HttpCookie type"""

    def test_inject_single_cookie(self):
        """Test injecting a single HTTP cookie with name and value"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, session_id: HttpCookie) -> dict:
                return {
                    "name": session_id.name,
                    "value": session_id.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", cookies={"session_id": "abc123"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["name"] == "session_id"
        assert response.body["value"] == "abc123"

    def test_inject_multiple_cookies(self):
        """Test injecting multiple HTTP cookies"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, session_id: HttpCookie, access_token: HttpCookie
            ) -> dict:
                return {
                    "session_id": session_id.value,
                    "session_id_name": session_id.name,
                    "access_token": access_token.value,
                    "access_token_name": access_token.name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"session_id": "abc123", "access_token": "xyz789"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["session_id"] == "abc123"
        assert response.body["session_id_name"] == "session_id"
        assert response.body["access_token"] == "xyz789"
        assert response.body["access_token_name"] == "access_token"

    def test_missing_required_cookie(self):
        """Test missing required cookie raises error"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, access_token: HttpCookie) -> dict:
                return {"token": access_token.value}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/user", cookies={})

        response = app.handle_request(request)
        assert response.status_code == 400
        # Check error message contains reference to missing cookie
        assert "error" in response.body or "errors" in response.body

    def test_optional_cookie(self):
        """Test optional HTTP cookie with Optional type hint"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, remember_me: Optional[HttpCookie] = None) -> dict:
                if remember_me:
                    return {"value": remember_me.value, "name": remember_me.name}
                return {"value": None}

        app = Application("__main__")
        app.initialize()

        # Test without cookie
        request = HttpRequest(method="GET", path="/api/user", cookies={})

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["value"] is None

        # Test with cookie
        request = HttpRequest(
            method="GET", path="/api/user", cookies={"remember_me": "true"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["value"] == "true"
        assert response.body["name"] == "remember_me"


class TestMixedInjection:
    """Test mixing headers, cookies, and body parameters"""

    def test_headers_cookies_and_body(self):
        """Test using headers, cookies, and body parameters together"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                user_agent: HttpHeader,
                session_id: HttpCookie,
                name: str,
            ) -> dict:
                return {
                    "user_agent": user_agent.value,
                    "session_id": session_id.value,
                    "name": name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0"},
            cookies={"session_id": "abc123"},
            body={"name": "John"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["session_id"] == "abc123"
        assert response.body["name"] == "John"

    def test_example_from_user(self):
        """Test the exact example from user request"""

        @Controller("/api")
        class UserController:
            @Get("/profile")
            def get_profile(
                self, user_agent: HttpHeader, access_token: HttpCookie
            ) -> dict:
                return {
                    "user_agent_name": user_agent.name,
                    "user_agent_value": user_agent.value,
                    "token_name": access_token.name,
                    "token_value": access_token.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/profile",
            headers={"User-Agent": "Mozilla/5.0"},
            cookies={"access_token": "secret123"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent_name"] == "User-Agent"
        assert response.body["user_agent_value"] == "Mozilla/5.0"
        assert response.body["token_name"] == "access_token"
        assert response.body["token_value"] == "secret123"


class TestExplicitNameSpecification:
    """Test explicit name specification with HttpHeader["Name"] syntax"""

    def test_bracket_syntax_header(self):
        """Test HttpHeader["User-Agent"] bracket syntax"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, agent: HttpHeader["User-Agent"]) -> dict:
                return {
                    "name": agent.name,
                    "value": agent.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", headers={"User-Agent": "Chrome/90.0"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["name"] == "User-Agent"
        assert response.body["value"] == "Chrome/90.0"

    def test_bracket_syntax_cookie(self):
        """Test HttpCookie["session_id"] bracket syntax"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, sid: HttpCookie["session_id"]) -> dict:
                return {
                    "name": sid.name,
                    "value": sid.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", cookies={"session_id": "xyz789"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["name"] == "session_id"
        assert response.body["value"] == "xyz789"

    def test_mixed_auto_and_bracket_headers(self):
        """Test mixing auto-conversion and bracket syntax for headers"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                user_agent: HttpHeader,  # Auto: user_agent -> User-Agent
                lang: HttpHeader["Accept-Language"],  # Bracket: explicit name
            ) -> dict:
                return {
                    "user_agent": user_agent.value,
                    "user_agent_name": user_agent.name,
                    "lang": lang.value,
                    "lang_name": lang.name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["user_agent_name"] == "User-Agent"
        assert response.body["lang"] == "en-US"
        assert response.body["lang_name"] == "Accept-Language"

    def test_mixed_auto_and_bracket_cookies(self):
        """Test mixing auto-match and bracket syntax for cookies"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                session_id: HttpCookie,  # Auto: parameter name
                token: HttpCookie["access_token"],  # Bracket: explicit name
            ) -> dict:
                return {
                    "session_id": session_id.value,
                    "session_id_name": session_id.name,
                    "token": token.value,
                    "token_name": token.name,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"session_id": "abc123", "access_token": "xyz789"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["session_id"] == "abc123"
        assert response.body["session_id_name"] == "session_id"
        assert response.body["token"] == "xyz789"
        assert response.body["token_name"] == "access_token"

    def test_bracket_syntax_with_optional(self):
        """Test bracket syntax with Optional type"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, auth: Optional[HttpHeader["Authorization"]] = None
            ) -> dict:
                if auth:
                    return {"auth": auth.value, "name": auth.name}
                return {"auth": None}

        app = Application("__main__")
        app.initialize()

        # Without header
        request = HttpRequest(method="GET", path="/api/user", headers={})
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] is None

        # With header
        request = HttpRequest(
            method="GET", path="/api/user", headers={"Authorization": "Bearer abc"}
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] == "Bearer abc"
        assert response.body["name"] == "Authorization"
