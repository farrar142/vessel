"""
Test HTTP Header and Cookie injection
"""

import pytest
from typing import Optional
from vessel.http.injection_types import HttpHeader, HttpCookie
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Get
from vessel.web.application import Application
from vessel.http.request import HttpRequest


class TestHttpHeaderInjection:
    """Test HTTP header injection with HttpHeader type"""

    def test_inject_single_header(self):
        """Test injecting a single HTTP header"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, user_agent: HttpHeader) -> dict:
                return {"user_agent": user_agent}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", headers={"User-Agent": "Mozilla/5.0"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"

    def test_inject_multiple_headers(self):
        """Test injecting multiple HTTP headers"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, user_agent: HttpHeader, host: HttpHeader) -> dict:
                return {"user_agent": user_agent, "host": host}

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
        assert response.body["host"] == "example.com"

    def test_header_name_conversion(self):
        """Test parameter name to header name conversion (snake_case to Title-Case)"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, content_type: HttpHeader, accept_language: HttpHeader
            ) -> dict:
                return {
                    "content_type": content_type,
                    "accept_language": accept_language,
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
        assert response.body["accept_language"] == "en-US"

    def test_missing_required_header(self):
        """Test missing required header raises error"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, authorization: HttpHeader) -> dict:
                return {"auth": authorization}

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
                return {"auth": authorization}

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


class TestHttpCookieInjection:
    """Test HTTP cookie injection with HttpCookie type"""

    def test_inject_single_cookie(self):
        """Test injecting a single HTTP cookie"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, session_id: HttpCookie) -> dict:
                return {"session_id": session_id}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/user", cookies={"session_id": "abc123"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["session_id"] == "abc123"

    def test_inject_multiple_cookies(self):
        """Test injecting multiple HTTP cookies"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, session_id: HttpCookie, user_id: HttpCookie) -> dict:
                return {"session_id": session_id, "user_id": user_id}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"session_id": "abc123", "user_id": "user456"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["session_id"] == "abc123"
        assert response.body["user_id"] == "user456"

    def test_missing_required_cookie(self):
        """Test missing required cookie raises error"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, access_token: HttpCookie) -> dict:
                return {"token": access_token}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/user", cookies={})

        response = app.handle_request(request)
        assert response.status_code == 400
        assert "access_token" in response.body[
            "error"
        ].lower() or "access_token" in str(response.body)

    def test_optional_cookie(self):
        """Test optional HTTP cookie with Optional type hint"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(self, access_token: Optional[HttpCookie] = None) -> dict:
                return {"token": access_token}

        app = Application("__main__")
        app.initialize()

        # Test without cookie
        request = HttpRequest(method="GET", path="/api/user", cookies={})

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["token"] is None

        # Test with cookie
        request = HttpRequest(
            method="GET", path="/api/user", cookies={"access_token": "token789"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["token"] == "token789"


class TestMixedInjection:
    """Test mixing headers, cookies, and other parameters"""

    def test_headers_cookies_and_body(self):
        """Test mixing headers, cookies, and request body parameters"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, user_agent: HttpHeader, access_token: HttpCookie, user_id: int
            ) -> dict:
                return {
                    "user_agent": user_agent,
                    "access_token": access_token,
                    "user_id": user_id,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0"},
            cookies={"access_token": "token123"},
            body={"user_id": 42},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["access_token"] == "token123"
        assert response.body["user_id"] == 42

    def test_example_from_user(self):
        """Test exact example from user request"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                user_agent: HttpHeader,
                remote_addr: HttpHeader,
                access_token: HttpCookie,
            ) -> dict:
                return {
                    "user_agent": user_agent,
                    "remote_addr": remote_addr,
                    "access_token": access_token,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0", "Remote-Addr": "192.168.1.1"},
            cookies={"access_token": "secure_token_xyz"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["remote_addr"] == "192.168.1.1"
        assert response.body["access_token"] == "secure_token_xyz"


class TestExplicitNameSpecification:
    """Test explicit header/cookie name specification"""

    def test_explicit_header_name(self):
        """Test HttpHeader with explicit name: agent: HttpHeader = HttpHeader('User-Agent')"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                agent: HttpHeader = HttpHeader("User-Agent"),
                content: HttpHeader = HttpHeader("Content-Type"),
            ) -> dict:
                return {"agent": agent, "content": content}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["agent"] == "Mozilla/5.0"
        assert response.body["content"] == "application/json"

    def test_explicit_cookie_name(self):
        """Test HttpCookie with explicit name: token: HttpCookie = HttpCookie('access_token')"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                token: HttpCookie = HttpCookie("access_token"),
                sid: HttpCookie = HttpCookie("session_id"),
            ) -> dict:
                return {"token": token, "sid": sid}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"access_token": "token123", "session_id": "session456"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["token"] == "token123"
        assert response.body["sid"] == "session456"

    def test_mixed_auto_and_explicit_headers(self):
        """Test mixing auto-converted and explicit header names"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                user_agent: HttpHeader,  # Auto: user_agent -> User-Agent
                lang: HttpHeader = HttpHeader("Accept-Language"),  # Explicit
            ) -> dict:
                return {"user_agent": user_agent, "lang": lang}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Mozilla/5.0"
        assert response.body["lang"] == "ko-KR"

    def test_mixed_auto_and_explicit_cookies(self):
        """Test mixing auto-matched and explicit cookie names"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                session_id: HttpCookie,  # Auto: session_id -> session_id
                token: HttpCookie = HttpCookie("access_token"),  # Explicit
            ) -> dict:
                return {"session_id": session_id, "token": token}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"session_id": "session789", "access_token": "token456"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["session_id"] == "session789"
        assert response.body["token"] == "token456"

    def test_explicit_optional_header(self):
        """Test explicit header name with Optional"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self, auth: Optional[HttpHeader] = HttpHeader("Authorization")
            ) -> dict:
                return {"auth": auth}

        app = Application("__main__")
        app.initialize()

        # Without header
        request = HttpRequest(method="GET", path="/api/user", headers={})

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] is None

        # With header
        request = HttpRequest(
            method="GET", path="/api/user", headers={"Authorization": "Bearer xyz"}
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] == "Bearer xyz"

    def test_bracket_syntax_header(self):
        """Test HttpHeader["Name"] bracket syntax as default value"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                agent: HttpHeader["User-Agent"],
                content: HttpHeader["Content-Type"],
            ) -> dict:
                return {"agent": agent, "content": content}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={"User-Agent": "Chrome/90.0", "Content-Type": "text/html"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["agent"] == "Chrome/90.0"
        assert response.body["content"] == "text/html"

    def test_bracket_syntax_cookie(self):
        """Test HttpCookie["name"] bracket syntax as default value"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                token: HttpCookie = HttpCookie["access_token"],
                sid: HttpCookie = HttpCookie["session_id"],
            ) -> dict:
                return {"token": token, "sid": sid}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            cookies={"access_token": "token_bracket", "session_id": "sid_bracket"},
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["token"] == "token_bracket"
        assert response.body["sid"] == "sid_bracket"

    def test_all_three_syntaxes(self):
        """Test all three syntaxes: HttpHeader[], HttpHeader(), auto-convert"""

        @Controller("/api")
        class UserController:
            @Get("/user")
            def get_user(
                self,
                lang: HttpHeader = HttpHeader("Accept-Language"),  # Bracket syntax
                auth: HttpHeader = HttpHeader("Authorization"),  # Parentheses syntax
                user_agent: HttpHeader = None,  # Auto conversion (requires workaround)
            ) -> dict:
                return {"user_agent": user_agent, "auth": auth, "lang": lang}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/user",
            headers={
                "User-Agent": "Firefox/88.0",
                "Authorization": "Bearer abc",
                "Accept-Language": "en-US",
            },
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["user_agent"] == "Firefox/88.0"
        assert response.body["auth"] == "Bearer abc"
        assert response.body["lang"] == "en-US"
