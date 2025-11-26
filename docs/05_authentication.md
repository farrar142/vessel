# Authentication System

> 테스트 기반: `tests/test_authentication.py`

## 개요

Vessel은 미들웨어 기반의 인증 시스템을 제공합니다.
- `Authenticator`: 인증 로직을 구현하는 인터페이스
- `AuthMiddleware`: 인증 미들웨어
- `Authentication`: 인증 정보를 담는 객체 (핸들러에 주입됨)

## 기본 구조

### 1. Authenticator 구현

인증 로직을 정의합니다:

```python
from vessel import Authenticator, HttpRequest, Authentication

class BearerTokenAuthenticator(Authenticator):
    def authenticate(self, request: HttpRequest) -> Authentication:
        """
        인증 로직 구현
        성공 시: Authentication 객체 반환
        실패 시: None 반환
        """
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]  # "Bearer " 제거
        
        # 토큰 검증 (예시)
        if token == "valid_token":
            return Authentication(
                user_id="user123",
                username="john",
                authenticated=True
            )
        
        return None
    
    def supports(self, request: HttpRequest) -> bool:
        """
        이 인증기가 해당 요청을 처리할 수 있는지 확인
        """
        auth_header = request.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")
```

### 2. AuthMiddleware 등록

```python
from vessel import Component, AuthMiddleware

@Component
class MyAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        # 인증기 등록
        self.register(BearerTokenAuthenticator())
```

### 3. MiddlewareChain 설정

```python
from vessel import Configuration, Factory, MiddlewareChain

@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(self, auth_middleware: MyAuthMiddleware) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(auth_middleware)
        return chain
```

### 4. 컨트롤러에서 사용

```python
from vessel import Controller, Get, Authentication

@Controller("/api")
class UserController:
    @Get("/profile")
    def get_profile(self, authentication: Authentication) -> dict:
        return {
            "user_id": authentication.user_id,
            "username": authentication.username,
            "authenticated": authentication.authenticated
        }
```

## Authentication 객체

```python
from vessel import Authentication

auth = Authentication(
    user_id="user123",
    username="john",
    authenticated=True,
    roles=["admin", "user"],  # 선택적
    metadata={"email": "john@example.com"}  # 선택적
)

# 속성 접근
auth.user_id         # "user123"
auth.username        # "john"
auth.authenticated   # True
auth.roles          # ["admin", "user"]
auth.metadata       # {"email": "john@example.com"}
```

## 실전 예제

### JWT 토큰 인증

```python
import jwt
from datetime import datetime, timedelta
from vessel import Authenticator, HttpRequest, Authentication, Component, AuthMiddleware

class JWTAuthenticator(Authenticator):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def authenticate(self, request: HttpRequest) -> Authentication:
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]
        
        try:
            # JWT 토큰 검증
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            return Authentication(
                user_id=payload["user_id"],
                username=payload["username"],
                authenticated=True,
                roles=payload.get("roles", []),
                metadata={"exp": payload["exp"]}
            )
        except jwt.ExpiredSignatureError:
            return None  # 토큰 만료
        except jwt.InvalidTokenError:
            return None  # 유효하지 않은 토큰
    
    def supports(self, request: HttpRequest) -> bool:
        auth_header = request.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")

@Component
class JWTAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        secret = "your-secret-key-here"
        self.register(JWTAuthenticator(secret))
```

### API 키 인증

```python
from vessel import Authenticator, HttpRequest, Authentication, Component, AuthMiddleware

@Component
class ApiKeyService:
    def __init__(self):
        # 실제로는 DB에서 조회
        self.api_keys = {
            "key-12345": {"user_id": "user1", "app_name": "Mobile App"},
            "key-67890": {"user_id": "user2", "app_name": "Web App"}
        }
    
    def validate_key(self, api_key: str):
        return self.api_keys.get(api_key)

class ApiKeyAuthenticator(Authenticator):
    def __init__(self, api_key_service: ApiKeyService):
        self.api_key_service = api_key_service
    
    def authenticate(self, request: HttpRequest) -> Authentication:
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return None
        
        key_info = self.api_key_service.validate_key(api_key)
        
        if key_info:
            return Authentication(
                user_id=key_info["user_id"],
                username=key_info["app_name"],
                authenticated=True,
                metadata={"api_key": api_key, "app": key_info["app_name"]}
            )
        
        return None
    
    def supports(self, request: HttpRequest) -> bool:
        return request.headers.get("X-API-Key") is not None

@Component
class ApiKeyAuthMiddleware(AuthMiddleware):
    api_key_service: ApiKeyService
    
    def __init__(self):
        super().__init__()
    
    def post_construct(self):
        # 의존성 주입 후 초기화
        self.register(ApiKeyAuthenticator(self.api_key_service))
```

### 여러 인증 방식 지원

하나의 `AuthMiddleware`에 여러 `Authenticator`를 등록할 수 있습니다:

```python
@Component
class MultiAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        # JWT 토큰 인증
        self.register(JWTAuthenticator("secret-key"))
        # API 키 인증
        self.register(ApiKeyAuthenticator())
        # Basic 인증
        self.register(BasicAuthenticator())

# 요청 시 supports()가 True인 첫 번째 Authenticator가 사용됨
```

### 인증 실패 처리

인증이 필요한 엔드포인트에 인증 없이 접근하면 **401 Unauthorized** 에러가 자동으로 반환됩니다:

```python
@Controller("/api")
class SecureController:
    @Get("/secure-data")
    def get_secure_data(self, authentication: Authentication) -> dict:
        return {"data": "sensitive information"}

# Authorization 헤더 없이 요청
# → 401 Unauthorized
# {
#   "error": "Unauthorized",
#   "message": "Authentication required"
# }
```

### 선택적 인증

인증은 필요하지만 실패해도 괜찮은 경우:

```python
from typing import Optional

@Controller("/api")
class DataController:
    @Get("/data")
    def get_data(
        self,
        request: HttpRequest
    ) -> dict:
        # request에서 직접 인증 정보를 확인
        auth = request.context.get("authentication")
        
        if auth and auth.authenticated:
            # 인증된 사용자에게는 더 많은 정보 제공
            return {
                "data": "full data",
                "user": auth.username
            }
        else:
            # 비인증 사용자에게는 제한된 정보
            return {
                "data": "limited data"
            }
```

**주의:** 현재 Vessel은 `Optional[Authentication]`을 지원하지 않습니다. 위와 같이 `HttpRequest`를 통해 수동으로 확인해야 합니다.

### Role 기반 권한 확인

```python
from vessel import Controller, Get, Authentication, HttpResponse, HttpStatus

@Controller("/api/admin")
class AdminController:
    @Get("/users")
    def list_users(self, authentication: Authentication) -> HttpResponse:
        # 역할 확인
        if "admin" not in authentication.roles:
            return HttpResponse(
                status_code=HttpStatus.FORBIDDEN,
                body={"error": "Admin access required"}
            )
        
        return HttpResponse(
            status_code=HttpStatus.OK,
            body={"users": []}
        )
```

## 전체 예제

```python
from vessel import (
    Application, Controller, Get, Post,
    Authenticator, AuthMiddleware, Authentication,
    HttpRequest, HttpResponse, HttpStatus,
    Component, Configuration, Factory,
    MiddlewareChain
)
import jwt
from datetime import datetime, timedelta

# JWT 토큰 생성 유틸리티
class JWTService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_token(self, user_id: str, username: str, roles: list) -> str:
        payload = {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

# JWT Authenticator
class JWTAuthenticator(Authenticator):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def authenticate(self, request: HttpRequest) -> Authentication:
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return Authentication(
                user_id=payload["user_id"],
                username=payload["username"],
                authenticated=True,
                roles=payload.get("roles", [])
            )
        except:
            return None
    
    def supports(self, request: HttpRequest) -> bool:
        auth_header = request.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")

# Auth Middleware
@Component
class JWTAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        self.register(JWTAuthenticator("secret-key-123"))

# Middleware 설정
@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(self, auth_middleware: JWTAuthMiddleware) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(auth_middleware)
        return chain

# 로그인 컨트롤러 (토큰 발급)
@Controller("/auth")
class AuthController:
    def __init__(self):
        self.jwt_service = JWTService("secret-key-123")
    
    @Post("/login")
    def login(self, body: dict) -> HttpResponse:
        username = body.get("username")
        password = body.get("password")
        
        # 실제로는 DB에서 검증
        if username == "admin" and password == "admin123":
            token = self.jwt_service.create_token(
                user_id="1",
                username="admin",
                roles=["admin", "user"]
            )
            return HttpResponse(
                status_code=HttpStatus.OK,
                body={"token": token}
            )
        
        return HttpResponse(
            status_code=HttpStatus.UNAUTHORIZED,
            body={"error": "Invalid credentials"}
        )

# 보호된 컨트롤러
@Controller("/api")
class UserController:
    @Get("/profile")
    def get_profile(self, authentication: Authentication) -> dict:
        return {
            "user_id": authentication.user_id,
            "username": authentication.username,
            "roles": authentication.roles
        }
    
    @Get("/admin/data")
    def admin_data(self, authentication: Authentication) -> HttpResponse:
        if "admin" not in authentication.roles:
            return HttpResponse(
                status_code=HttpStatus.FORBIDDEN,
                body={"error": "Admin access required"}
            )
        
        return HttpResponse(
            status_code=HttpStatus.OK,
            body={"sensitive": "data"}
        )

# 애플리케이션 실행
app = Application("__main__")
app.initialize()

if __name__ == "__main__":
    app.run(port=8000)
```

**사용 예시:**

```bash
# 1. 로그인 (토큰 받기)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# → {"token": "eyJ0eXAiOiJKV1QiLCJ..."}

# 2. 프로필 조회 (인증 필요)
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ..."
# → {"user_id":"1","username":"admin","roles":["admin","user"]}

# 3. 관리자 데이터 (admin 역할 필요)
curl http://localhost:8000/api/admin/data \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ..."
# → {"sensitive":"data"}
```

## 정리

### ✅ 지원하는 기능
- 미들웨어 기반 인증
- 여러 Authenticator 등록
- Authentication 객체 자동 주입
- 인증 실패 시 자동 401 응답
- Role 기반 접근 제어 (수동)

### ❌ 지원하지 않는 기능
- Optional 인증 (모든 Authentication은 필수)
- 자동 Role 검증 (수동으로 확인 필요)
- 세션 관리 (직접 구현 필요)
- OAuth/OIDC (직접 구현 필요)
