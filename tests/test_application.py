"""
Application 클래스 테스트
"""

import pytest
from vessel import Application, Component, Controller, Get, Post
from vessel.http.request import HttpRequest, HttpResponse


class TestApplication:
    """Application 클래스 기본 테스트"""

    def test_application_creation(self):
        """Application 생성 테스트"""
        app = Application("__main__", debug=True, port=9000)

        assert app.packages == ["__main__"]  # 이제 list로 변경됨
        assert app.debug is True
        assert app.port == 9000
        assert app.is_initialized is False
        assert app.is_running is False

    def test_application_initialization(self):
        """Application 초기화 테스트"""

        @Component
        class TestService:
            pass

        @Controller("/test")
        class TestController:
            service: TestService

            @Get
            def test_handler(self):
                return {"result": "ok"}

        app = Application("__main__", debug=False)
        app.initialize()

        assert app.is_initialized is True
        assert app.route_handler is not None
        assert app.container_manager is not None

        # 서비스 주입 확인
        service = app.get_instance(TestService)
        assert service is not None

    def test_method_chaining(self):
        """메서드 체이닝 테스트"""
        app = Application("__main__")

        result = app.initialize()
        assert result is app

    def test_handle_request(self):
        """HTTP 요청 처리 테스트"""

        @Component
        class DataService:
            def get_data(self):
                return {"message": "Hello"}

        @Controller("/api")
        class ApiController:
            service: DataService

            @Get("/hello")
            def hello(self):
                return self.service.get_data()

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/hello")
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body == {"message": "Hello"}

    def test_cors_headers(self):
        """CORS 헤더 테스트"""

        @Controller("/api")
        class ApiController:
            @Get
            def test(self):
                return {"result": "ok"}

        app = Application("__main__", enable_cors=True)
        app.initialize()

        request = HttpRequest(method="GET", path="/api")
        response = app.handle_request(request)

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    def test_error_handler(self):
        """에러 핸들러 테스트"""

        @Controller("/api")
        class ApiController:
            @Get("/error")
            def error(self):
                raise ValueError("Test error")

        def handle_value_error(error):
            return HttpResponse(
                status_code=400, body={"error": "Custom error", "message": str(error)}
            )

        app = Application("__main__")
        app.initialize()  # 먼저 초기화
        app.add_error_handler(ValueError, handle_value_error)  # 그 다음 에러 핸들러 추가

        request = HttpRequest(method="GET", path="/api/error")
        response = app.handle_request(request)

        assert response.status_code == 400
        assert response.body["error"] == "Custom error"
        assert response.body["message"] == "Test error"

    def test_default_error_handling(self):
        """기본 에러 처리 테스트"""

        @Controller("/api")
        class ApiController:
            @Get("/error")
            def error(self):
                raise RuntimeError("Unhandled error")

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/error")
        response = app.handle_request(request)

        assert response.status_code == 500
        assert "error" in response.body
        assert "message" in response.body

    def test_get_instance(self):
        """get_instance 테스트"""

        @Component
        class MyService:
            def __init__(self):
                self.value = "test"

        app = Application("__main__")
        app.initialize()

        service = app.get_instance(MyService)
        assert service is not None
        assert service.value == "test"

    def test_get_instance_before_initialization(self):
        """초기화 전 get_instance 호출 시 에러"""
        app = Application("__main__")

        with pytest.raises(RuntimeError, match="not initialized"):
            app.get_instance(type)

    def test_handle_request_before_initialization(self):
        """초기화 전 handle_request 호출 시 에러"""
        app = Application("__main__")
        request = HttpRequest(method="GET", path="/test")

        with pytest.raises(RuntimeError, match="not initialized"):
            app.handle_request(request)

    def test_multiple_packages(self):
        """여러 패키지 스캔 테스트"""
        app = Application("package1", "package2", "package3")

        assert len(app.packages) == 3
        assert "package1" in app.packages
        assert "package2" in app.packages
        assert "package3" in app.packages


class TestApplicationIntegration:
    """Application 통합 테스트"""

    def test_full_application_flow(self):
        """전체 애플리케이션 플로우 테스트"""

        # 서비스 계층
        @Component
        class UserService:
            def __init__(self):
                self.users = {}
                self.next_id = 1

            def create_user(self, name: str):
                user_id = self.next_id
                self.next_id += 1
                user = {"id": user_id, "name": name}
                self.users[user_id] = user
                return user

            def get_user(self, user_id: int):
                return self.users.get(user_id)

        @Component
        class LogService:
            def __init__(self):
                self.logs = []

            def log(self, message: str):
                self.logs.append(message)

        # 컨트롤러 계층
        @Controller("/api/users")
        class UserController:
            user_service: UserService
            log_service: LogService

            @Post
            def create_user(self, name: str):
                self.log_service.log(f"Creating user: {name}")
                user = self.user_service.create_user(name)
                return user

            @Get("/{user_id}")
            def get_user(self, user_id: int):
                self.log_service.log(f"Getting user: {user_id}")
                return self.user_service.get_user(user_id)

        # Application 생성
        app = Application("__main__", debug=True)
        app.initialize()

        # 사용자 생성 요청
        create_request = HttpRequest(
            method="POST", path="/api/users", body={"name": "Alice"}
        )
        create_response = app.handle_request(create_request)

        assert create_response.status_code == 200
        assert create_response.body["name"] == "Alice"
        assert create_response.body["id"] == 1

        # 로그 확인
        log_service = app.get_instance(LogService)
        assert len(log_service.logs) == 1
        assert "Creating user: Alice" in log_service.logs[0]

        # 사용자 조회 요청
        get_request = HttpRequest(method="GET", path="/api/users/1")
        get_response = app.handle_request(get_request)

        assert get_response.status_code == 200
        assert get_response.body["name"] == "Alice"
        assert get_response.body["id"] == 1

        # 로그 확인
        assert len(log_service.logs) == 2
        assert "Getting user: 1" in log_service.logs[1]
