"""
Validation 기능 테스트
"""

import pytest
from vessel import Application, Controller, Post, Get
from vessel.web.http.request import HttpRequest, HttpResponse


# Pydantic 없이 먼저 간단한 검증부터 시작
class TestBasicValidation:
    """기본 타입 검증 테스트"""

    def test_request_body_type_validation_success(self):
        """요청 바디가 예상 타입과 일치하면 성공"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int) -> dict:
                return {"username": username, "age": age}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST", path="/api/users", body={"username": "john", "age": 30}
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["username"] == "john"
        assert response.body["age"] == 30

    def test_request_body_type_validation_failure_wrong_type(self):
        """요청 바디 타입이 맞지 않으면 400 에러"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int) -> dict:
                return {"username": username, "age": age}

        app = Application("__main__")
        app.initialize()

        # age가 문자열로 전달 (int 기대)
        request = HttpRequest(
            method="POST",
            path="/api/users",
            body={"username": "john", "age": "not_a_number"},
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        assert "validation" in response.body.get("error", "").lower()

    def test_request_body_missing_required_field(self):
        """필수 필드가 누락되면 400 에러"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int) -> dict:
                return {"username": username, "age": age}

        app = Application("__main__")
        app.initialize()

        # age 필드 누락
        request = HttpRequest(
            method="POST", path="/api/users", body={"username": "john"}
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        # details 배열에서 필드명 확인
        details = response.body.get("details", [])
        assert any("age" in detail.get("field", "") for detail in details)

    def test_optional_parameter_validation(self):
        """선택적 파라미터는 없어도 됨"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int = 18) -> dict:
                return {"username": username, "age": age}

        app = Application("__main__")
        app.initialize()

        # age 없이 요청
        request = HttpRequest(
            method="POST", path="/api/users", body={"username": "john"}
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["age"] == 18  # 기본값 사용


class TestValidationWithConstraints:
    """제약 조건 검증 테스트"""

    def test_string_length_validation(self):
        """문자열 길이 검증"""
        # TODO: 나중에 구현
        pass

    def test_numeric_range_validation(self):
        """숫자 범위 검증"""
        # TODO: 나중에 구현
        pass

    def test_email_format_validation(self):
        """이메일 형식 검증"""
        # TODO: 나중에 구현
        pass


class TestValidationErrorMessages:
    """검증 에러 메시지 테스트"""

    def test_validation_error_includes_field_name(self):
        """검증 에러에 필드 이름 포함"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int) -> dict:
                return {"username": username, "age": age}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/users",
            body={"username": "john", "age": "invalid"},
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        # details 배열에서 필드명 확인
        details = response.body.get("details", [])
        assert any("age" in detail.get("field", "") for detail in details)

    def test_multiple_validation_errors(self):
        """여러 검증 에러를 한번에 반환"""

        @Controller("/api")
        class UserController:
            @Post("/users")
            def create_user(self, username: str, age: int, email: str) -> dict:
                return {"username": username, "age": age, "email": email}

        app = Application("__main__")
        app.initialize()

        # age는 타입 에러, email은 누락
        request = HttpRequest(
            method="POST",
            path="/api/users",
            body={"username": "john", "age": "invalid"},
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        # details 배열에서 필드명 확인
        details = response.body.get("details", [])
        field_names = [detail.get("field", "") for detail in details]
        # age와 email 둘 다 에러에 포함
        assert "age" in field_names
        assert "email" in field_names


class TestValidationWithQueryParams:
    """Query Parameter 검증 테스트"""

    def test_query_param_type_validation(self):
        """Query 파라미터도 타입 검증"""

        @Controller("/api")
        class UserController:
            @Get("/users")
            def list_users(self, page: int = 1, limit: int = 10) -> dict:
                return {"page": page, "limit": limit}

        app = Application("__main__")
        app.initialize()

        # 정상 요청
        request = HttpRequest(
            method="GET", path="/api/users", query_params={"page": "2", "limit": "20"}
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["page"] == 2
        assert response.body["limit"] == 20

    def test_query_param_validation_failure(self):
        """Query 파라미터 타입 불일치 시 400 에러"""

        @Controller("/api")
        class UserController:
            @Get("/users")
            def list_users(self, page: int = 1) -> dict:
                return {"page": page}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET", path="/api/users", query_params={"page": "not_a_number"}
        )

        response = app.handle_request(request)

        assert response.status_code == 400


class TestValidationWithPathParams:
    """Path Parameter 검증 테스트"""

    def test_path_param_type_validation(self):
        """Path 파라미터도 타입 검증"""

        @Controller("/api")
        class UserController:
            @Get("/users/{user_id}")
            def get_user(self, user_id: int) -> dict:
                return {"user_id": user_id}

        app = Application("__main__")
        app.initialize()

        # 정상 요청
        request = HttpRequest(method="GET", path="/api/users/123")

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["user_id"] == 123

    def test_path_param_validation_failure(self):
        """Path 파라미터 타입 불일치 시 400 에러"""

        @Controller("/api")
        class UserController:
            @Get("/users/{user_id}")
            def get_user(self, user_id: int) -> dict:
                return {"user_id": user_id}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/users/abc")

        response = app.handle_request(request)

        assert response.status_code == 400
