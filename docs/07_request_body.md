# RequestBody - Dataclass & Pydantic 자동 변환

> 테스트 기반: `tests/test_parameter_injector_integration.py`

## 개요

HTTP 요청 body를 자동으로 dataclass 또는 Pydantic BaseModel 인스턴스로 변환할 수 있습니다.

**세 가지 사용 패턴:**
1. `RequestBody[T]` - 전체 body를 하나의 모델로 변환 (명시적)
2. 직접 dataclass/BaseModel 파라미터 - body를 자동 변환 (간결함)
3. 여러 dataclass/BaseModel 파라미터 - 중첩된 객체를 각각 변환

**지원하는 타입:**
- Python dataclass
- Pydantic BaseModel

## 기본 사용법

### 패턴 1: RequestBody[T] (명시적)

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

### 패턴 2: 직접 Dataclass/BaseModel 파라미터 (Nested Mode 전용)

```python
from dataclasses import dataclass
from vessel import Controller, Post

@dataclass
class UserData:
    username: str
    age: int
    email: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, user: UserData) -> dict:
        # RequestBody 없이 자동 변환 (Priority 300)
        # 주의: Nested mode만 지원 (파라미터 이름이 body의 키로 존재해야 함)
        return {
            "username": user.username,
            "age": user.age,
            "email": user.email,
        }
```

**요청 (Nested mode - user 키 필수):**
```json
{
  "user": {
    "username": "john",
    "age": 30,
    "email": "john@example.com"
  }
}
```

### 패턴 3: 여러 Dataclass/BaseModel 파라미터 (중첩 객체)

```python
from dataclasses import dataclass
from pydantic import BaseModel
from vessel import Controller, Post

@dataclass
class FirstData:
    field1: str
    field2: int

class SecondData(BaseModel):
    field3: str
    field4: float

@Controller("/api")
class DataController:
    @Post("/create")
    def create(self, first: FirstData, second: SecondData) -> dict:
        # 각 파라미터가 body의 중첩 객체에서 자동 변환됨
        return {
            "first_field1": first.field1,
            "first_field2": first.field2,
            "second_field3": second.field3,
            "second_field4": second.field4,
        }
```

**요청 (패턴 3):**
```http
POST /api/create HTTP/1.1
Content-Type: application/json

{
  "first": {
    "field1": "value1",
    "field2": 10
  },
  "second": {
    "field3": "value3",
    "field4": 20.5
  }
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

## 사용 패턴 비교

### 1. 개별 필드 방식 (간단한 경우)

```python
@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, username: str, age: int, email: str) -> dict:
        # 각 필드를 개별 파라미터로 받음
        return {"username": username, "age": age, "email": email}
```

**요청:**
```json
{
  "username": "john",
  "age": 30,
  "email": "john@example.com"
}
```

### 2. 직접 Dataclass 방식 (Nested mode 전용)

```python
from dataclasses import dataclass

@dataclass
class UserData:
    username: str
    age: int
    email: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, user: UserData) -> dict:
        # Dataclass로 받음 (RequestBody 불필요)
        # 주의: 파라미터 이름이 body의 키로 존재해야 함
        return {
            "username": user.username,
            "age": user.age,
            "email": user.email,
        }
```

**요청 (user 키 필수):**
```json
{
  "user": {
    "username": "john",
    "age": 30,
    "email": "john@example.com"
  }
}
```

### 3. RequestBody[T] 방식 (명시적)

```python
from vessel import RequestBody

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, body: RequestBody[UserData]) -> dict:
        # RequestBody로 명시적 표현
        return {
            "username": body.username,
            "age": body.age,
            "email": body.email,
        }
```

**요청 (동일):**
```json
{
  "username": "john",
  "age": 30,
  "email": "john@example.com"
}
```

### 4. 여러 Dataclass 방식 (복잡한 구조)

```python
@dataclass
class UserData:
    username: str
    age: int

@dataclass
class AddressData:
    city: str
    street: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, user: UserData, address: AddressData) -> dict:
        # 여러 dataclass를 받음
        return {
            "username": user.username,
            "age": user.age,
            "city": address.city,
            "street": address.street,
        }
```

**요청 (중첩 구조):**
```json
{
  "user": {
    "username": "john",
    "age": 30
  },
  "address": {
    "city": "Seoul",
    "street": "Gangnam"
  }
}
```

## Pydantic 지원

Pydantic BaseModel도 동일하게 지원됩니다:

```python
from pydantic import BaseModel, Field
from vessel import Controller, Post

class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=0, le=150)
    email: str

@Controller("/api")
class UserController:
    @Post("/users")
    def create_user(self, user: UserModel) -> dict:
        # Pydantic의 강력한 검증 기능 활용
        return {
            "username": user.username,
            "age": user.age,
            "email": user.email,
        }
```

**Pydantic 장점:**
- 더 강력한 검증 (min_length, ge, le 등)
- 자동 타입 변환
- 상세한 에러 메시지

## 두 가지 변환 모드

### Nested Mode (중첩 모드) - 직접 Dataclass/Pydantic 사용

직접 dataclass/Pydantic 파라미터는 **반드시 nested mode로만 작동**합니다:

```python
@dataclass
class UserData:
    name: str
    age: int

@Post("/create")
def create(self, user: UserData) -> dict:
    return {"name": user.name}
```

**요청 (파라미터 이름과 일치하는 키 필수):**
```json
{
  "user": {
    "name": "john",
    "age": 30
  }
}
```

### Flat Mode (평면 모드) - RequestBody[T] 사용

Flat mode를 사용하려면 **반드시 `RequestBody[T]`를 사용**해야 합니다:

```python
@Post("/create")
def create(self, user: RequestBody[UserData]) -> dict:
    return {"name": user.name}
```

**요청 (파라미터 이름 없이 필드 직접):**
```json
{
  "name": "john",
  "age": 30
}
```

**중요:** 직접 dataclass/Pydantic 파라미터로 flat mode를 시도하면 400 에러가 발생합니다.

## 장점

1. **타입 안정성**: Dataclass/Pydantic을 사용하여 강력한 타입 체킹
2. **가독성**: 요청 구조가 명확하게 정의됨
3. **재사용성**: Model을 다른 곳에서도 사용 가능
4. **자동 검증**: 필수 필드와 타입이 자동으로 검증됨
5. **중첩 구조**: 복잡한 중첩 구조도 쉽게 처리
6. **문서화**: Model 정의가 곧 API 문서
7. **유연성**: 세 가지 사용 패턴 지원

## 우선순위 시스템

Parameter Injection 우선순위:
- 0: HttpRequest
- 100: HttpHeader
- 110: HttpCookie
- **150: RequestBody[T]**
- 180: Authentication
- 200: UploadedFile
- **300: Dataclass (직접 사용)**
- **310: Pydantic BaseModel (직접 사용)**
- 999: DefaultValue

## 주의사항

1. **타입 힌트 필수**: 모든 필드에 타입 힌트가 있어야 합니다
2. **직접 인스턴스화 금지**: `RequestBody`를 직접 인스턴스화하지 마세요
3. **여러 파라미터 사용 시**: 중첩 구조 필요 (Nested Mode)

## 실전 예제

### 예제 1: 복잡한 중첩 구조

```python
from dataclasses import dataclass, field
from typing import List, Optional
from vessel import Controller, Post

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
    def create_user(self, user: CreateUserRequest) -> dict:
        # 복잡한 구조도 쉽게 처리 (RequestBody 생략 가능)
        user_data = {
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "is_active": user.is_active,
            "addresses": [
                {
                    "street": addr.street,
                    "city": addr.city,
                    "country": addr.country,
                }
                for addr in user.addresses
            ],
            "tags": user.tags,
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

### 예제 2: Dataclass와 Pydantic 혼합 사용

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field
from vessel import Controller, Post

@dataclass
class UserBasicInfo:
    username: str
    age: int

class UserSettings(BaseModel):
    theme: str = "light"
    language: str = Field(default="en", pattern="^(en|ko|ja)$")
    notifications_enabled: bool = True

@Controller("/api")
class UserController:
    @Post("/users/complete")
    def create_complete_user(
        self,
        basic: UserBasicInfo,
        settings: UserSettings
    ) -> dict:
        return {
            "username": basic.username,
            "age": basic.age,
            "theme": settings.theme,
            "language": settings.language,
            "notifications": settings.notifications_enabled,
        }
```

**요청:**
```json
{
  "basic": {
    "username": "john",
    "age": 30
  },
  "settings": {
    "theme": "dark",
    "language": "ko"
  }
}
```

### 예제 3: 다른 Injector와 함께 사용

```python
from dataclasses import dataclass
from vessel import Controller, Post
from vessel.web.http.injection_types import HttpHeader
from vessel.web.http.uploaded_file import UploadedFile

@dataclass
class PostData:
    title: str
    content: str
    tags: List[str]

@Controller("/api")
class PostController:
    @Post("/posts")
    def create_post(
        self,
        post: PostData,
        authorization: HttpHeader["Authorization"],
        thumbnail: UploadedFile["thumbnail"],
        notify: bool = False
    ) -> dict:
        # 여러 Injector가 함께 작동
        return {
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "thumbnail": thumbnail.filename,
            "auth": authorization.value,
            "notify": notify,
        }
```

**요청:**
```http
POST /api/posts?notify=true HTTP/1.1
Authorization: Bearer token123
Content-Type: multipart/form-data

{
  "post": {
    "title": "My Post",
    "content": "Content here",
    "tags": ["python", "web"]
  },
  "thumbnail": {
    "filename": "image.jpg",
    "content": <binary data>,
    "content_type": "image/jpeg"
  }
}
```

## 정리

### 언제 무엇을 사용할까?

**개별 필드** - 파라미터가 3개 이하이고 단순한 경우:
```python
def create(self, name: str, age: int) -> dict:
# body: {"name": "john", "age": 30}
```

**RequestBody[T] (Flat mode)** - 필드를 직접 body에 넣고 싶은 경우 (권장):
```python
def create(self, user: RequestBody[UserData]) -> dict:
# body: {"username": "john", "age": 30, "email": "..."}
```

**직접 Dataclass (Nested mode)** - 파라미터 이름으로 그룹화하고 싶은 경우:
```python
def create(self, user: UserData) -> dict:
# body: {"user": {"username": "john", "age": 30, "email": "..."}}
```

**여러 Dataclass (Nested mode)** - 복잡한 구조를 논리적으로 분리하고 싶은 경우:
```python
def create(self, user: UserData, settings: SettingsData) -> dict:
# body: {
#   "user": {"username": "john", ...},
#   "settings": {"theme": "dark", ...}
# }
```

**Pydantic** - 강력한 검증이 필요한 경우:
```python
class UserModel(BaseModel):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

# RequestBody[T] for flat mode
def create(self, user: RequestBody[UserModel]) -> dict:
# body: {"email": "...", "age": 30}

# Direct parameter for nested mode
def create(self, user: UserModel) -> dict:
# body: {"user": {"email": "...", "age": 30}}
```

### 핵심 규칙

1. **Flat mode = RequestBody[T]**: 필드를 body에 직접 넣으려면 `RequestBody[T]` 사용
2. **Nested mode = 직접 파라미터**: 파라미터 이름으로 그룹화하려면 직접 dataclass/Pydantic 사용
3. **여러 모델 = 반드시 Nested**: 여러 dataclass/Pydantic 파라미터는 항상 nested mode
