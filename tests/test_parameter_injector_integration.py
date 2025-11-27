"""
ParameterInjector 시스템 전체 통합 테스트
모든 injector들이 올바르게 동작하고 우선순위에 따라 작동하는지 검증
"""

import pytest
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field

from vessel import Application, Controller, Get, Post
from vessel.web.http.request import HttpRequest
from vessel.web.http.injection_types import HttpHeader, HttpCookie
from vessel.web.http.request_body import RequestBody
from vessel.web.http.uploaded_file import UploadedFile


class TestParameterInjectorIntegration:
    """모든 ParameterInjector가 함께 동작하는 통합 테스트"""

    def test_http_request_injection(self):
        """HttpRequest 객체 주입 테스트 (Priority 0)"""

        @Controller("/api")
        class RequestController:
            @Get("/request-info")
            def get_request_info(self, request: HttpRequest) -> dict:
                return {
                    "method": request.method,
                    "path": request.path,
                    "has_body": request.body is not None,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="GET", path="/api/request-info")
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["method"] == "GET"
        assert response.body["path"] == "/api/request-info"
        assert response.body["has_body"] is False

    def test_http_header_injection(self):
        """HttpHeader 주입 테스트 (Priority 100)"""

        @Controller("/api")
        class HeaderController:
            @Get("/headers")
            def get_headers(
                self,
                user_agent: HttpHeader["User-Agent"],
                authorization: HttpHeader["Authorization"],
            ) -> dict:
                return {
                    "user_agent": user_agent.value,
                    "authorization": authorization.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/headers",
            headers={
                "User-Agent": "TestAgent/1.0",
                "Authorization": "Bearer token123",
            },
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["user_agent"] == "TestAgent/1.0"
        assert response.body["authorization"] == "Bearer token123"

    def test_http_cookie_injection(self):
        """HttpCookie 주입 테스트 (Priority 110)"""

        @Controller("/api")
        class CookieController:
            @Get("/cookies")
            def get_cookies(
                self, session_id: HttpCookie["session_id"], token: HttpCookie["token"]
            ) -> dict:
                return {"session_id": session_id.value, "token": token.value}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/cookies",
            cookies={"session_id": "abc123", "token": "xyz789"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["session_id"] == "abc123"
        assert response.body["token"] == "xyz789"

    def test_request_body_dataclass_injection(self):
        """RequestBody[Dataclass] 주입 테스트 (Priority 150)"""

        @dataclass
        class UserData:
            username: str
            age: int
            email: str

        @Controller("/api")
        class DataclassController:
            @Post("/users")
            def create_user(self, body: RequestBody[UserData]) -> dict:
                return {
                    "username": body.username,
                    "age": body.age,
                    "email": body.email,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/users",
            body={"username": "john", "age": 30, "email": "john@example.com"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["username"] == "john"
        assert response.body["age"] == 30
        assert response.body["email"] == "john@example.com"

    def test_request_body_pydantic_injection(self):
        """RequestBody[BaseModel] 주입 테스트 (Priority 150)"""

        class UserModel(BaseModel):
            username: str = Field(min_length=3)
            age: int = Field(ge=0, le=150)
            email: str

        @Controller("/api")
        class PydanticController:
            @Post("/users")
            def create_user(self, body: RequestBody[UserModel]) -> dict:
                return {
                    "username": body.username,
                    "age": body.age,
                    "email": body.email,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/users",
            body={"username": "john", "age": 30, "email": "john@example.com"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["username"] == "john"
        assert response.body["age"] == 30

    def test_file_upload_injection(self):
        """UploadedFile 주입 테스트 (Priority 200)"""

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile["file"]) -> dict:
                return {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": file.size,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "test.txt",
                    "content": b"test content",
                    "content_type": "text/plain",
                }
            },
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["filename"] == "test.txt"
        assert response.body["content_type"] == "text/plain"
        assert response.body["size"] == 12

    def test_query_and_path_parameter_injection(self):
        """Query 파라미터와 Path 파라미터 주입 테스트 (Priority 999)"""

        @Controller("/api")
        class ParamController:
            @Get("/users/{user_id}")
            def get_user(self, user_id: int, include_details: bool = False) -> dict:
                return {"user_id": user_id, "include_details": include_details}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/users/123",
            query_params={"include_details": "true"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["user_id"] == 123
        assert response.body["include_details"] is True

    def test_default_value_injection(self):
        """기본값 주입 테스트 (Priority 999)"""

        @Controller("/api")
        class DefaultController:
            @Get("/greet")
            def greet(self, name: str = "World", greeting: str = "Hello") -> dict:
                return {"message": f"{greeting} {name}"}

        app = Application("__main__")
        app.initialize()

        # 파라미터 없음 - 기본값 사용
        request = HttpRequest(method="GET", path="/api/greet")
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["message"] == "Hello World"

        # 일부 파라미터만 제공
        request = HttpRequest(
            method="GET", path="/api/greet", query_params={"name": "Alice"}
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["message"] == "Hello Alice"

        # 모든 파라미터 제공
        request = HttpRequest(
            method="GET",
            path="/api/greet",
            query_params={"name": "Bob", "greeting": "Hi"},
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["message"] == "Hi Bob"

    def test_multiple_injectors_together(self):
        """여러 injector가 동시에 작동하는 복합 시나리오"""

        @dataclass
        class TaskData:
            title: str
            description: str
            priority: int = 3

        @Controller("/api/projects")
        class ComplexController:
            @Post("/{project_id}/tasks")
            def create_task(
                self,
                project_id: int,
                body: RequestBody[TaskData],
                authorization: HttpHeader["Authorization"],
                session: HttpCookie["session"],
                notify: bool = False,
            ) -> dict:
                return {
                    "project_id": project_id,
                    "title": body.title,
                    "description": body.description,
                    "priority": body.priority,
                    "notify": notify,
                    "auth": authorization.value,
                    "session": session.value,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/projects/42/tasks",
            query_params={"notify": "true"},
            body={"title": "Important Task", "description": "Do this ASAP"},
            headers={"Authorization": "Bearer token123"},
            cookies={"session": "session-abc"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["project_id"] == 42
        assert response.body["title"] == "Important Task"
        assert response.body["description"] == "Do this ASAP"
        assert response.body["priority"] == 3  # default value
        assert response.body["notify"] is True
        assert response.body["auth"] == "Bearer token123"
        assert response.body["session"] == "session-abc"

    def test_optional_parameters(self):
        """Optional 파라미터 테스트"""

        @Controller("/api")
        class OptionalController:
            @Get("/user")
            def get_user(
                self,
                auth: Optional[HttpHeader["Authorization"]] = None,
                admin: bool = False,
            ) -> dict:
                return {
                    "auth": auth.value if auth else None,
                    "admin": admin,
                }

        app = Application("__main__")
        app.initialize()

        # Authorization 없음
        request = HttpRequest(method="GET", path="/api/user")
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] is None
        assert response.body["admin"] is False

        # Authorization 있음
        request = HttpRequest(
            method="GET", path="/api/user", headers={"Authorization": "Bearer xyz"}
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["auth"] == "Bearer xyz"

    def test_type_conversion(self):
        """자동 타입 변환 테스트"""

        @Controller("/api")
        class TypeController:
            @Get("/convert")
            def convert_types(
                self, age: int, price: float, active: bool, tags: str
            ) -> dict:
                return {
                    "age": age,
                    "age_type": type(age).__name__,
                    "price": price,
                    "price_type": type(price).__name__,
                    "active": active,
                    "active_type": type(active).__name__,
                    "tags": tags,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/convert",
            query_params={
                "age": "30",
                "price": "19.99",
                "active": "true",
                "tags": "python,test",
            },
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["age"] == 30
        assert response.body["age_type"] == "int"
        assert response.body["price"] == 19.99
        assert response.body["price_type"] == "float"
        assert response.body["active"] is True
        assert response.body["active_type"] == "bool"
        assert response.body["tags"] == "python,test"

    def test_validation_error_handling(self):
        """Validation 에러 처리 테스트"""

        class StrictModel(BaseModel):
            username: str = Field(min_length=5, max_length=20)
            age: int = Field(ge=18, le=100)

        @Controller("/api")
        class ValidationController:
            @Post("/validate")
            def validate_data(self, body: RequestBody[StrictModel]) -> dict:
                return {"username": body.username, "age": body.age}

        app = Application("__main__")
        app.initialize()

        # username too short
        request = HttpRequest(
            method="POST",
            path="/api/validate",
            body={"username": "abc", "age": 25},
        )
        response = app.handle_request(request)
        assert response.status_code == 400
        assert "details" in response.body

        # age too young
        request = HttpRequest(
            method="POST",
            path="/api/validate",
            body={"username": "validuser", "age": 15},
        )
        response = app.handle_request(request)
        assert response.status_code == 400
        assert "details" in response.body

        # Valid data
        request = HttpRequest(
            method="POST",
            path="/api/validate",
            body={"username": "validuser", "age": 25},
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["username"] == "validuser"
        assert response.body["age"] == 25

    def test_missing_required_parameter(self):
        """필수 파라미터 누락 테스트"""

        @Controller("/api")
        class RequiredController:
            @Get("/required")
            def required_params(self, name: str, age: int) -> dict:
                return {"name": name, "age": age}

        app = Application("__main__")
        app.initialize()

        # Missing both parameters
        request = HttpRequest(method="GET", path="/api/required")
        response = app.handle_request(request)
        assert response.status_code == 400

        # Missing one parameter
        request = HttpRequest(
            method="GET", path="/api/required", query_params={"name": "Alice"}
        )
        response = app.handle_request(request)
        assert response.status_code == 400

        # All parameters provided
        request = HttpRequest(
            method="GET",
            path="/api/required",
            query_params={"name": "Alice", "age": "30"},
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["name"] == "Alice"
        assert response.body["age"] == 30

    def test_injector_priority_order(self):
        """Injector 우선순위 테스트 - 우선순위가 낮은 injector가 먼저 실행됨"""

        @dataclass
        class RequestData:
            data: str

        @Controller("/api")
        class PriorityController:
            @Post("/priority/{id}")
            def test_priority(
                self,
                request: HttpRequest,  # Priority 0
                authorization: HttpHeader["Authorization"],  # Priority 100
                session: HttpCookie["session"],  # Priority 110
                body: RequestBody[RequestData],  # Priority 150
                id: int,  # Priority 999
                optional: str = "default",  # Priority 999
            ) -> dict:
                return {
                    "request_method": request.method,
                    "auth": authorization.value,
                    "session": session.value,
                    "body_data": body.data,
                    "id": id,
                    "optional": optional,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/priority/123",
            query_params={"optional": "custom"},
            body={"data": "test"},
            headers={"Authorization": "Bearer xyz"},
            cookies={"session": "sess123"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["request_method"] == "POST"
        assert response.body["auth"] == "Bearer xyz"
        assert response.body["session"] == "sess123"
        assert response.body["body_data"] == "test"
        assert response.body["id"] == 123
        assert response.body["optional"] == "custom"

    def test_nested_dataclass_with_request_body(self):
        """중첩된 dataclass RequestBody 테스트"""

        @dataclass
        class Address:
            street: str
            city: str
            zip_code: str

        @dataclass
        class Person:
            name: str
            age: int
            address: Address

        @Controller("/api")
        class NestedController:
            @Post("/person")
            def create_person(self, body: RequestBody[Person]) -> dict:
                return {
                    "name": body.name,
                    "age": body.age,
                    "street": body.address.street,
                    "city": body.address.city,
                    "zip_code": body.address.zip_code,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/person",
            body={
                "name": "John",
                "age": 30,
                "address": {
                    "street": "123 Main St",
                    "city": "NYC",
                    "zip_code": "10001",
                },
            },
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["name"] == "John"
        assert response.body["age"] == 30
        assert response.body["street"] == "123 Main St"
        assert response.body["city"] == "NYC"
        assert response.body["zip_code"] == "10001"

    def test_list_type_parameters(self):
        """리스트 타입 파라미터 테스트"""

        @dataclass
        class TodoList:
            title: str
            items: list[str]

        @Controller("/api")
        class ListController:
            @Post("/todos")
            def create_todos(self, body: RequestBody[TodoList]) -> dict:
                return {
                    "title": body.title,
                    "item_count": len(body.items),
                    "items": body.items,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/todos",
            body={"title": "My Tasks", "items": ["Task 1", "Task 2", "Task 3"]},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["title"] == "My Tasks"
        assert response.body["item_count"] == 3
        assert response.body["items"] == ["Task 1", "Task 2", "Task 3"]


class TestParameterInjectorEdgeCases:
    """ParameterInjector 엣지 케이스 테스트"""

    def test_empty_request_body(self):
        """빈 request body 처리"""

        @dataclass
        class EmptyData:
            value: str = "default"

        @Controller("/api")
        class EmptyController:
            @Post("/empty")
            def handle_empty(self, body: RequestBody[EmptyData]) -> dict:
                return {"value": body.value}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(method="POST", path="/api/empty", body={})
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["value"] == "default"

    def test_multiple_files_upload(self):
        """여러 파일 동시 업로드 테스트"""

        @Controller("/api")
        class MultiFileController:
            @Post("/upload-multiple")
            def upload_files(
                self, file1: UploadedFile["file1"], file2: UploadedFile["file2"]
            ) -> dict:
                return {
                    "file1_name": file1.filename,
                    "file1_size": file1.size,
                    "file2_name": file2.filename,
                    "file2_size": file2.size,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload-multiple",
            body={
                "file1": {
                    "filename": "doc1.txt",
                    "content": b"Document 1",
                    "content_type": "text/plain",
                },
                "file2": {
                    "filename": "doc2.pdf",
                    "content": b"PDF Content",
                    "content_type": "application/pdf",
                },
            },
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["file1_name"] == "doc1.txt"
        assert response.body["file1_size"] == 10
        assert response.body["file2_name"] == "doc2.pdf"
        assert response.body["file2_size"] == 11

    def test_special_characters_in_parameters(self):
        """특수 문자가 포함된 파라미터 처리"""

        @Controller("/api")
        class SpecialController:
            @Get("/search")
            def search(self, query: str, tags: str = "") -> dict:
                return {"query": query, "tags": tags}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="GET",
            path="/api/search",
            query_params={"query": "hello world", "tags": "python,test"},
        )
        response = app.handle_request(request)

        assert response.status_code == 200
        # URL decoding은 프레임워크에서 처리된다고 가정

    def test_seperate_field_parameters(self):
        @dataclass
        class FirstData:
            field1: str
            field2: int

        class SecondData(BaseModel):
            field3: str
            field4: float

        @Controller("/api")
        class SeparateFieldController:
            @Post("/test")
            def echo(
                self,
                first: FirstData,
                second: SecondData,
            ) -> dict:
                return {
                    "first_field1": first.field1,
                    "first_field2": first.field2,
                    "second_field3": second.field3,
                    "second_field4": second.field4,
                }

        app = Application("__main__")
        app.initialize()
        request = HttpRequest(
            method="POST",
            path="/api/test",
            body={
                "first": {
                    "field1": "value1",
                    "field2": 10,
                },
                "second": {
                    "field3": "value3",
                    "field4": 20.5,
                },
            },
        )
        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["first_field1"] == "value1"
        assert response.body["first_field2"] == 10
        assert response.body["second_field3"] == "value3"
        assert response.body["second_field4"] == 20.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
