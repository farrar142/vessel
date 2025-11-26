# Authentication System

인증 시스템은 Vessel 프레임워크에서 요청을 인증하고 사용자 정보를 컨트롤러에 주입하는 기능을 제공합니다.

## 구성 요소

### 1. Authentication (인증 정보 클래스)

사용자 인증 정보를 담는 기본 클래스입니다. 사용자는 이 클래스를 확장하여 자신만의 인증 정보를 정의할 수 있습니다.

```python
from vessel.web.middleware.auth import Authentication

# 기본 사용
auth = Authentication(user_id="user123", authenticated=True)

# 커스텀 속성 추가 (kwargs 사용)
auth = Authentication(
    user_id="user123",
    username="john",
    email="john@example.com",
    authenticated=True
)

# 또는 상속을 통한 확장
class UserAuthentication(Authentication):
    def __init__(self, user_id: str, username: str, roles: list[str], **kwargs):
        super().__init__(user_id=user_id, authenticated=True, **kwargs)
        self.username = username
        self.roles = roles
    
    def has_role(self, role: str) -> bool:
        return role in self.roles
```

### 2. Authenticator (인증기 추상 클래스)

프레임워크는 인증기의 인터페이스만 제공하며, JWT, HTTP Bearer, Token 등의 구체적인 인증 방식은 사용자가 구현합니다.

```python
from vessel.web.middleware.auth import Authenticator, Authentication
from vessel.http.request import HttpRequest

class JwtAuthenticator(Authenticator):
    def authenticate(self, request: HttpRequest) -> Authentication:
        """
        요청에서 JWT 토큰을 추출하고 검증하여 Authentication 반환
        인증 실패 시 None 반환
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]
        try:
            # JWT 토큰 검증 로직
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return Authentication(
                user_id=payload["user_id"],
                username=payload.get("username"),
                authenticated=True
            )
        except jwt.InvalidTokenError:
            return None
    
    def supports(self, request: HttpRequest) -> bool:
        """
        이 인증기가 해당 요청을 처리할 수 있는지 확인
        """
        auth_header = request.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")
```

### 3. AuthMiddleware (인증 미들웨어)

등록된 인증기들을 사용하여 요청을 인증하고, 결과를 request 객체에 저장합니다.

```python
from vessel.web.middleware.auth import AuthMiddleware

# 인증 미들웨어 생성
auth_middleware = AuthMiddleware()

# 인증기 등록 (여러 개 등록 가능)
auth_middleware.register(JwtAuthenticator())
auth_middleware.register(ApiKeyAuthenticator())
```

### 4. AuthenticationInjector (파라미터 주입기)

컨트롤러 메서드의 `Authentication` 파라미터에 인증 정보를 자동으로 주입합니다.

- `Authentication`: 필수 인증 (401 에러 반환)
- `Optional[Authentication]`: 선택적 인증 (None 가능)
- `UserAuthentication`: 커스텀 Authentication 클래스도 지원

## 사용 방법

### 기본 사용 (Configuration + Factory 패턴)

```python
from vessel.decorators.di.component import Component
from vessel.decorators.di.configuration import Configuration
from vessel.decorators.di.factory import Factory
from vessel.web.middleware.auth import AuthMiddleware, Authenticator, Authentication
from vessel.web.middleware.chain import MiddlewareChain
from vessel.http.request import HttpRequest

# 1. 인증기 구현
class JwtAuthenticator(Authenticator):
    def authenticate(self, request: HttpRequest) -> Authentication:
        # JWT 토큰 검증 로직
        token = self.extract_token(request)
        if self.verify_token(token):
            payload = self.decode_token(token)
            return Authentication(
                user_id=payload["user_id"],
                authenticated=True
            )
        return None
    
    def supports(self, request: HttpRequest) -> bool:
        return "Authorization" in request.headers

# 2. AuthMiddleware를 Component로 등록
@Component
class AppAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        self.register(JwtAuthenticator())

# 3. MiddlewareChain을 Factory로 생성
@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(self, auth_middleware: AppAuthMiddleware) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(auth_middleware)
        return chain

# 4. 컨트롤러에서 사용
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Get

@Controller("/api")
class UserController:
    @Get("/profile")
    def get_profile(self, authentication: Authentication) -> dict:
        """인증 필수 엔드포인트"""
        return {
            "user_id": authentication.user_id,
            "authenticated": authentication.authenticated
        }
    
    @Get("/public")
    def public_data(self, authentication: Optional[Authentication] = None) -> dict:
        """선택적 인증 엔드포인트"""
        if authentication and authentication.authenticated:
            return {"content": "premium", "user": authentication.user_id}
        return {"content": "free"}
```

### 여러 인증기 사용

```python
@Component
class AppAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        # 등록 순서대로 실행됨
        self.register(JwtAuthenticator())
        self.register(ApiKeyAuthenticator())
        self.register(BasicAuthenticator())
```

각 인증기의 `supports()` 메서드가 순서대로 호출되며, 첫 번째로 True를 반환하는 인증기의 `authenticate()` 메서드가 실행됩니다.

### 커스텀 Authentication 클래스

```python
class UserAuthentication(Authentication):
    def __init__(self, user_id: str, username: str, roles: list[str], **kwargs):
        super().__init__(user_id=user_id, authenticated=True, **kwargs)
        self.username = username
        self.roles = roles
    
    def has_role(self, role: str) -> bool:
        return role in self.roles

class JwtAuthenticator(Authenticator):
    def authenticate(self, request: HttpRequest) -> UserAuthentication:
        # JWT 검증 후 UserAuthentication 반환
        payload = self.verify_and_decode(request)
        return UserAuthentication(
            user_id=payload["user_id"],
            username=payload["username"],
            roles=payload["roles"]
        )
    
    def supports(self, request: HttpRequest) -> bool:
        return "Authorization" in request.headers

# 컨트롤러에서 사용
@Controller("/admin")
class AdminController:
    @Get("/dashboard")
    def dashboard(self, authentication: UserAuthentication) -> dict:
        if not authentication.has_role("admin"):
            return {"error": "Forbidden"}, 403
        
        return {
            "message": f"Welcome {authentication.username}",
            "roles": authentication.roles
        }
```

## 인증 흐름

1. **요청 수신**: 클라이언트로부터 HTTP 요청 수신
2. **미들웨어 처리**: `AuthMiddleware.process_request()` 실행
3. **인증기 선택**: 등록된 인증기들의 `supports()` 메서드를 순회하여 적합한 인증기 선택
4. **인증 실행**: 선택된 인증기의 `authenticate()` 메서드 실행
5. **결과 저장**: 인증 결과를 `request._auth_data`에 저장
6. **라우팅**: RouteHandler가 컨트롤러 메서드 실행
7. **파라미터 주입**: `AuthenticationInjector`가 `Authentication` 파라미터에 인증 정보 주입
8. **응답 반환**: 컨트롤러 메서드 실행 후 응답 반환

## 인증 실패 처리

### 필수 인증 (Authentication)

인증이 필요한데 실패한 경우 자동으로 401 Unauthorized 응답 반환:

```python
@Get("/secure")
def secure_data(self, authentication: Authentication) -> dict:
    # 인증 실패 시 여기까지 도달하지 않음 (401 에러)
    return {"data": "secret"}
```

### 선택적 인증 (Optional[Authentication])

인증 실패 시에도 None이 주입되어 메서드가 실행됨:

```python
@Get("/content")
def content(self, authentication: Optional[Authentication] = None) -> dict:
    if authentication and authentication.authenticated:
        return {"content": "premium"}
    return {"content": "free"}
```

## 예제: 실전 JWT 인증

```python
import jwt
from datetime import datetime, timedelta
from vessel.decorators.di.component import Component
from vessel.web.middleware.auth import Authenticator, Authentication

@Component
class JwtAuthenticator(Authenticator):
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    
    def authenticate(self, request: HttpRequest) -> Authentication:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]
        
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            # 토큰 만료 확인
            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                return None
            
            return Authentication(
                user_id=payload["user_id"],
                username=payload.get("username"),
                email=payload.get("email"),
                authenticated=True
            )
        except jwt.InvalidTokenError:
            return None
    
    def supports(self, request: HttpRequest) -> bool:
        auth_header = request.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")
    
    @staticmethod
    def create_token(user_id: str, username: str, email: str) -> str:
        """JWT 토큰 생성 (로그인 시 사용)"""
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "exp": datetime.now() + timedelta(hours=24),
            "iat": datetime.now()
        }
        return jwt.encode(payload, JwtAuthenticator.SECRET_KEY, algorithm=JwtAuthenticator.ALGORITHM)

# 로그인 컨트롤러
@Controller("/auth")
class AuthController:
    @Post("/login")
    def login(self, username: str, password: str) -> dict:
        # 사용자 인증 (데이터베이스 확인 등)
        user = self.verify_user(username, password)
        if not user:
            return {"error": "Invalid credentials"}, 401
        
        # JWT 토큰 생성
        token = JwtAuthenticator.create_token(
            user_id=user.id,
            username=user.username,
            email=user.email
        )
        
        return {
            "token": token,
            "token_type": "Bearer"
        }

# 보호된 리소스
@Controller("/api")
class UserController:
    @Get("/profile")
    def profile(self, authentication: Authentication) -> dict:
        return {
            "user_id": authentication.user_id,
            "username": authentication.username,
            "email": authentication.email
        }
```

## 테스트

```python
def test_authentication():
    # 테스트용 인증기
    class TestAuthenticator(Authenticator):
        def authenticate(self, request):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token == "valid_token":
                return Authentication(user_id="test_user", authenticated=True)
            return None
        
        def supports(self, request):
            return "Authorization" in request.headers
    
    # 미들웨어 설정
    @Component
    class TestAuthMiddleware(AuthMiddleware):
        def __init__(self):
            super().__init__()
            self.register(TestAuthenticator())
    
    @Configuration
    class MiddlewareConfig:
        @Factory
        def middleware_chain(self, auth: TestAuthMiddleware) -> MiddlewareChain:
            chain = MiddlewareChain()
            chain.get_default_group().add(auth)
            return chain
    
    # 테스트 실행
    app = Application("__main__")
    app.initialize()
    
    request = HttpRequest(
        method="GET",
        path="/api/profile",
        headers={"Authorization": "Bearer valid_token"}
    )
    
    response = app.handle_request(request)
    assert response.status_code == 200
```

## 주의사항

1. **프레임워크는 인증 구현을 제공하지 않음**: JWT, OAuth, Basic Auth 등은 사용자가 직접 구현해야 합니다.

2. **인증기 등록 순서**: 여러 인증기를 등록할 때 등록 순서대로 실행되므로, 가장 많이 사용되는 인증 방식을 먼저 등록하는 것이 효율적입니다.

3. **Optional 사용**: 선택적 인증이 필요한 경우 반드시 `Optional[Authentication]`과 기본값 `= None`을 함께 사용해야 합니다.

4. **커스텀 Authentication**: Authentication을 확장한 클래스도 파라미터 타입으로 사용할 수 있으며, 자동으로 주입됩니다.

5. **보안**: SECRET_KEY, 토큰 만료 시간 등 보안 관련 설정은 환경 변수나 설정 파일에서 관리하세요.
