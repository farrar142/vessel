# Web Framework - Controllers & Routing

> 테스트 기반: `tests/test_handler.py`, `tests/test_application.py`

## 개요

Vessel은 데코레이터 기반의 웹 라우팅을 제공합니다.

## @Controller 데코레이터

컨트롤러 클래스를 정의하고 베이스 경로를 설정합니다:

```python
from vessel import Controller

@Controller("/api/users")
class UserController:
    pass
```

## HTTP 메서드 데코레이터

### 사용 가능한 데코레이터

```python
from vessel import Get, Post, Put, Delete, Patch

@Controller("/api/users")
class UserController:
    @Get("/")  # GET /api/users/
    def list_users(self):
        return {"users": []}
    
    @Get("/{id}")  # GET /api/users/123
    def get_user(self, id: str):
        return {"id": id}
    
    @Post("/")  # POST /api/users/
    def create_user(self):
        return {"message": "created"}
    
    @Put("/{id}")  # PUT /api/users/123
    def update_user(self, id: str):
        return {"message": "updated"}
    
    @Delete("/{id}")  # DELETE /api/users/123
    def delete_user(self, id: str):
        return {"message": "deleted"}
    
    @Patch("/{id}")  # PATCH /api/users/123
    def patch_user(self, id: str):
        return {"message": "patched"}
```

## 경로 파라미터 (Path Parameters)

### 기본 사용법

중괄호 `{name}` 으로 경로 파라미터를 선언하고, 핸들러 함수의 인자로 받습니다:

```python
@Controller("/api")
class ProductController:
    @Get("/products/{product_id}")
    def get_product(self, product_id: str) -> dict:
        return {"product_id": product_id}
```

### 타입 변환

타입 힌트를 사용하면 자동으로 변환됩니다:

```python
@Controller("/api")
class ProductController:
    @Get("/products/{product_id}")
    def get_product(self, product_id: int) -> dict:  # str → int 자동 변환
        return {"product_id": product_id, "type": type(product_id).__name__}

# GET /api/products/123 → product_id는 int 123
```

**지원 타입:**
- `int`
- `str` (기본)
- `float`
- `bool`

### 여러 경로 파라미터

```python
@Controller("/api")
class PostController:
    @Get("/users/{user_id}/posts/{post_id}")
    def get_post(self, user_id: int, post_id: int) -> dict:
        return {
            "user_id": user_id,
            "post_id": post_id
        }
```

## 쿼리 파라미터 (Query Parameters)

### 기본 사용법

함수 파라미터로 선언하면 쿼리 파라미터를 받습니다:

```python
@Controller("/api")
class SearchController:
    @Get("/search")
    def search(self, q: str) -> dict:
        return {"query": q}

# GET /api/search?q=python → {"query": "python"}
```

### 타입 변환

```python
@Controller("/api")
class ProductController:
    @Get("/products")
    def list_products(self, page: int, size: int) -> dict:
        return {
            "page": page,
            "size": size,
            "type_page": type(page).__name__,
            "type_size": type(size).__name__
        }

# GET /api/products?page=1&size=20
# → {"page": 1, "size": 20, "type_page": "int", "type_size": "int"}
```

### 기본값 사용

```python
@Controller("/api")
class ProductController:
    @Get("/products")
    def list_products(self, page: int = 1, size: int = 10) -> dict:
        return {"page": page, "size": size}

# GET /api/products → {"page": 1, "size": 10}
# GET /api/products?page=2 → {"page": 2, "size": 10}
# GET /api/products?page=3&size=20 → {"page": 3, "size": 20}
```

### Boolean 변환

```python
@Controller("/api")
class ProductController:
    @Get("/products")
    def list_products(self, active: bool = True) -> dict:
        return {"active": active, "type": type(active).__name__}

# GET /api/products?active=true → {"active": True, ...}
# GET /api/products?active=false → {"active": False, ...}
# GET /api/products?active=1 → {"active": True, ...}
# GET /api/products?active=0 → {"active": False, ...}
```

## 요청 본문 (Request Body)

### dict로 받기

```python
@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: dict) -> dict:
        return {
            "name": body.get("name"),
            "email": body.get("email")
        }

# POST /api/users
# Body: {"name": "John", "email": "john@example.com"}
```

### 데이터 클래스로 받기

타입 힌트를 사용하면 자동으로 검증 및 변환됩니다:

```python
from dataclasses import dataclass

@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: CreateUserRequest) -> dict:
        return {
            "name": body.name,
            "email": body.email,
            "age": body.age,
            "age_type": type(body.age).__name__
        }

# POST /api/users
# Body: {"name": "John", "email": "john@example.com", "age": "25"}
# → age는 자동으로 int로 변환
```

## 응답 (Response)

### dict 반환

```python
@Get("/user")
def get_user(self) -> dict:
    return {"id": 1, "name": "John"}

# 자동으로 JSON으로 변환되어 응답
# Status: 200
# Content-Type: application/json
# Body: {"id": 1, "name": "John"}
```

### HttpResponse 반환

더 세밀한 제어가 필요하면 `HttpResponse`를 직접 반환:

```python
from vessel import HttpResponse, HttpStatus

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: dict) -> HttpResponse:
        return HttpResponse(
            status_code=HttpStatus.CREATED,  # 201
            body={"id": 123, "name": body["name"]},
            headers={"Location": "/api/users/123"}
        )
```

### 상태 코드

```python
from vessel import HttpStatus

# 성공 응답
HttpStatus.OK  # 200
HttpStatus.CREATED  # 201
HttpStatus.NO_CONTENT  # 204

# 클라이언트 에러
HttpStatus.BAD_REQUEST  # 400
HttpStatus.UNAUTHORIZED  # 401
HttpStatus.FORBIDDEN  # 403
HttpStatus.NOT_FOUND  # 404

# 서버 에러
HttpStatus.INTERNAL_SERVER_ERROR  # 500
```

## HttpRequest 주입

`HttpRequest` 객체를 직접 받을 수 있습니다:

```python
from vessel import HttpRequest

@Controller("/api")
class DebugController:
    @Get("/debug")
    def debug_request(self, request: HttpRequest) -> dict:
        return {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "query": request.query_params,
            "body": request.body
        }
```

## 의존성 주입

컨트롤러에서도 의존성 주입을 사용할 수 있습니다:

```python
from vessel import Controller, Component

@Component
class UserService:
    def get_user(self, user_id: int):
        return {"id": user_id, "name": "John"}

@Controller("/api")
class UserController:
    service: UserService  # 👈 필드 주입
    
    @Get("/users/{id}")
    def get_user(self, id: int) -> dict:
        return self.service.get_user(id)
```

## 파라미터 주입 우선순위

같은 이름의 파라미터가 여러 곳에 있을 때의 우선순위:

1. **경로 파라미터** (Path Parameter)
2. **쿼리 파라미터** (Query Parameter)
3. **본문** (Body)

```python
@Controller("/api")
class TestController:
    @Get("/items/{id}")  # /api/items/123?id=456
    def get_item(self, id: str) -> dict:
        return {"id": id}

# GET /api/items/123?id=456
# → {"id": "123"}  (경로 파라미터가 우선)
```

## 에러 처리

### ValidationError

잘못된 타입이나 필수 파라미터 누락 시 자동으로 400 에러 반환:

```python
@Controller("/api")
class ProductController:
    @Get("/products/{id}")
    def get_product(self, id: int) -> dict:
        return {"id": id}

# GET /api/products/abc
# → 400 Bad Request
# {
#   "error": "Validation Error",
#   "details": ["Parameter 'id': invalid int value: 'abc'"]
# }
```

### 커스텀 에러 핸들러

```python
from vessel import Application, HttpResponse, HttpStatus

app = Application("__main__")

@app.error_handler(ValueError)
def handle_value_error(error: ValueError) -> HttpResponse:
    return HttpResponse(
        status_code=HttpStatus.BAD_REQUEST,
        body={"error": str(error)}
    )

app.initialize()
```

## 전체 예제

```python
from vessel import Application, Controller, Get, Post, Component
from dataclasses import dataclass

# 서비스 계층
@Component
class UserService:
    def find_by_id(self, user_id: int):
        return {"id": user_id, "name": "John", "email": "john@example.com"}
    
    def create(self, name: str, email: str):
        return {"id": 123, "name": name, "email": email}

# 요청 DTO
@dataclass
class CreateUserRequest:
    name: str
    email: str

# 컨트롤러
@Controller("/api/users")
class UserController:
    service: UserService
    
    @Get("/")
    def list_users(self, page: int = 1, size: int = 10) -> dict:
        return {
            "users": [],
            "page": page,
            "size": size
        }
    
    @Get("/{id}")
    def get_user(self, id: int) -> dict:
        return self.service.find_by_id(id)
    
    @Post("/")
    def create_user(self, body: CreateUserRequest) -> dict:
        return self.service.create(body.name, body.email)

# 애플리케이션 시작
app = Application("__main__")
app.initialize()

if __name__ == "__main__":
    app.run(port=8000)
```
