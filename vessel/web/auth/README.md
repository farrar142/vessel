# vessel.web.auth 모듈

인증 시스템을 위한 핵심 컴포넌트들을 제공합니다.

## 모듈 구조

```
vessel/web/auth/
├── __init__.py           # 패키지 진입점, 모든 클래스 export
├── middleware.py         # AuthMiddleware, Authentication, Authenticator
└── injector.py           # AuthenticationInjector, AuthenticationException
```

## Export 클래스

### vessel.web.auth

모든 인증 관련 클래스는 `vessel.web.auth`에서 직접 import할 수 있습니다:

```python
from vessel.web.auth import (
    # Core Classes
    Authentication,          # 인증 정보 클래스
    Authenticator,          # 인증기 추상 클래스
    AuthenticatorRegistry,  # 인증기 레지스트리
    AuthMiddleware,         # 인증 미들웨어
    
    # Injector
    AuthenticationInjector,    # 파라미터 주입기
    AuthenticationException,   # 인증 예외
)
```

## 파일 설명

### middleware.py

인증 미들웨어와 관련된 핵심 클래스들:

- **Authentication**: 인증 정보를 담는 기본 클래스
- **Authenticator**: 인증기 추상 클래스 (사용자 구현 필요)
- **AuthenticatorRegistry**: 인증기들을 관리하는 레지스트리
- **AuthMiddleware**: 요청을 인증하는 미들웨어

### injector.py

파라미터 주입과 관련된 클래스들:

- **AuthenticationInjector**: `Authentication` 타입 파라미터를 자동 주입
- **AuthenticationException**: 인증 실패 시 발생하는 예외 (401 에러)

## 사용 예제

```python
from vessel.web.auth import AuthMiddleware, Authenticator, Authentication
from vessel.decorators.di.component import Component
from vessel.decorators.di.configuration import Configuration
from vessel.decorators.di.factory import Factory
from vessel.web.middleware.chain import MiddlewareChain

# 1. 인증기 구현
class JwtAuthenticator(Authenticator):
    def authenticate(self, request):
        # JWT 검증 로직
        return Authentication(user_id="user123", authenticated=True)
    
    def supports(self, request):
        return "Authorization" in request.headers

# 2. AuthMiddleware 등록
@Component
class AppAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        self.register(JwtAuthenticator())

# 3. MiddlewareChain 생성
@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(self, auth: AppAuthMiddleware) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(auth)
        return chain

# 4. 컨트롤러에서 사용
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Get

@Controller("/api")
class UserController:
    @Get("/profile")
    def profile(self, authentication: Authentication):
        return {"user_id": authentication.user_id}
```

## 관련 문서

- [Authentication System Guide](../../docs/authentication_system.md): 상세한 사용 가이드
