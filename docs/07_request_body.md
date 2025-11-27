# RequestBody - Dataclass & Pydantic 자동 변환

> 테스트 기반: 
> - Dataclass: `tests/test_parameter_validation.py::TestValidationWithRequestBody`
> - Pydantic: `tests/test_pydantic_request_body.py::TestPydanticRequestBody`

## 개요

`RequestBody[T]` 타입 힌트를 사용하면 HTTP 요청 body 전체를 자동으로 dataclass 또는 Pydantic BaseModel 인스턴스로 변환할 수 있습니다.

**지원하는 타입:**
- Python dataclass
- Pydantic BaseModel (권장)

## 기본 사용법

```python
from dataclasses import dataclass
from vessel import Controller, Post, RequestBody

@dataclass
class CreateUserRequest:
    username: str
    age: int
    email: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        # body는 자동으로 CreateUserRequest 인스턴스로 변환됨
        return {
            "username": body.username,
            "age": body.age,
            "email": body.email,
        }
```

**요청:**
```http
POST /api/users HTTP/1.1
Content-Type: application/json

{
  "username": "john",
  "age": 30,
  "email": "john@example.com"
}
```

**응답:**
```json
{
  "username": "john",
  "age": 30,
  "email": "john@example.com"
}
```

## 주요 기능

### 1. 자동 타입 변환 및 검증

```python
@dataclass
class CreateUserRequest:
    username: str
    age: int  # 자동으로 int로 변환됨
    is_active: bool  # 자동으로 bool로 변환됨

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        assert isinstance(body.age, int)
        assert isinstance(body.is_active, bool)
        return {"created": True}
```

### 2. 기본값 지원

```python
@dataclass
class CreateUserRequest:
    username: str
    age: int = 18  # 기본값
    email: str = "default@example.com"  # 기본값

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        # age와 email이 없으면 기본값 사용
        return {
            "username": body.username,
            "age": body.age,
            "email": body.email,
        }
```

**요청 (필드 누락):**
```json
{
  "username": "john"
}
```

**응답:**
```json
{
  "username": "john",
  "age": 18,
  "email": "default@example.com"
}
```

### 3. 중첩된 Dataclass 지원

```python
@dataclass
class Address:
    city: str
    street: str

@dataclass
class CreateUserRequest:
    username: str
    age: int
    address: Address  # 중첩된 dataclass

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        return {
            "username": body.username,
            "city": body.address.city,
            "street": body.address.street,
        }
```

**요청:**
```json
{
  "username": "john",
  "age": 30,
  "address": {
    "city": "Seoul",
    "street": "Gangnam"
  }
}
```

### 4. 리스트 필드 지원

```python
from typing import List

@dataclass
class CreateUserRequest:
    username: str
    tags: List[str]

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        return {
            "username": body.username,
            "tags": body.tags,
            "tag_count": len(body.tags),
        }
```

**요청:**
```json
{
  "username": "john",
  "tags": ["python", "django", "fastapi"]
}
```

### 5. Dictionary 필드 지원

```python
from typing import Dict

@dataclass
class CreateUserRequest:
    username: str
    metadata: Dict[str, str]

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        return {
            "username": body.username,
            "metadata": body.metadata,
        }
```

**요청:**
```json
{
  "username": "john",
  "metadata": {
    "city": "Seoul",
    "country": "Korea"
  }
}
```

## Validation

### 필수 필드 검증

필수 필드가 누락되면 400 에러가 반환됩니다:

```python
@dataclass
class CreateUserRequest:
    username: str
    email: str  # 필수 필드

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        return {"username": body.username}
```

**잘못된 요청 (email 누락):**
```json
{
  "username": "john"
}
```

**에러 응답:**
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "body.email",
      "message": "Missing required field 'email'"
    }
  ]
}
```

### 타입 검증

타입이 맞지 않으면 400 에러가 반환됩니다:

```python
@dataclass
class CreateUserRequest:
    username: str
    age: int  # int 타입 기대

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        return {"username": body.username}
```

**잘못된 요청 (age가 문자열):**
```json
{
  "username": "john",
  "age": "not_a_number"
}
```

**에러 응답:**
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "body.age",
      "message": "Cannot convert field 'age' to int: ..."
    }
  ]
}
```

## 개별 필드 vs RequestBody

### 개별 필드 방식 (기존)

```python
@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, username: str, age: int, email: str) -> dict:
        # 각 필드를 개별 파라미터로 받음
        return {"username": username, "age": age, "email": email}
```

### RequestBody 방식 (권장)

```python
@dataclass
class CreateUserRequest:
    username: str
    age: int
    email: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        # 전체 body를 dataclass로 받음
        return {
            "username": body.username,
            "age": body.age,
            "email": body.email,
        }
```

## 장점

1. **타입 안정성**: Dataclass를 사용하여 강력한 타입 체킹
2. **가독성**: 요청 구조가 명확하게 정의됨
3. **재사용성**: Dataclass를 다른 곳에서도 사용 가능
4. **자동 검증**: 필수 필드와 타입이 자동으로 검증됨
5. **중첩 구조**: 복잡한 중첩 구조도 쉽게 처리
6. **문서화**: Dataclass 정의가 곧 API 문서

## 주의사항

1. **Dataclass 필수**: `RequestBody`에는 반드시 dataclass를 지정해야 합니다
2. **타입 힌트 필수**: Dataclass의 모든 필드에 타입 힌트가 있어야 합니다
3. **직접 인스턴스화 금지**: `RequestBody`를 직접 인스턴스화하지 마세요

## 예제: 실전 활용

```python
from dataclasses import dataclass, field
from typing import List, Optional
from vessel import Controller, Post, RequestBody

@dataclass
class Address:
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None

@dataclass
class CreateUserRequest:
    username: str
    email: str
    age: int
    addresses: List[Address] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_active: bool = True

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[CreateUserRequest]) -> dict:
        # 복잡한 구조도 쉽게 처리
        user_data = {
            "username": body.username,
            "email": body.email,
            "age": body.age,
            "is_active": body.is_active,
            "addresses": [
                {
                    "street": addr.street,
                    "city": addr.city,
                    "country": addr.country,
                }
                for addr in body.addresses
            ],
            "tags": body.tags,
        }
        
        # DB에 저장하는 로직...
        
        return {"user": user_data, "created": True}
```

**요청:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "age": 30,
  "addresses": [
    {
      "street": "123 Main St",
      "city": "Seoul",
      "country": "Korea"
    }
  ],
  "tags": ["python", "django"]
}
```
