# Middleware System

> 테스트 기반: `tests/test_middleware_integration.py`

## 개요

Vessel의 미들웨어 시스템은 요청 처리 전후에 공통 로직을 실행할 수 있게 해줍니다.
- 요청 전처리 (로깅, 인증, 검증 등)
- 응답 후처리 (헤더 추가, 로깅 등)
- 조기 반환 (인증 실패 시 즉시 401 응답 등)

## Middleware 인터페이스

```python
from vessel import Middleware, HttpRequest, HttpResponse
from typing import Callable

class MyMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        """
        request: 현재 요청
        next: 다음 미들웨어 또는 핸들러를 실행하는 함수
        """
        # 1. 요청 전처리
        print(f"Request: {request.method} {request.path}")
        
        # 2. 다음 단계 실행
        response = next(request)
        
        # 3. 응답 후처리
        print(f"Response: {response.status_code}")
        
        return response
```

## 미들웨어 등록

### 자동 등록 (@Component)

`@Component`로 등록된 미들웨어는 자동으로 감지되고 등록됩니다:

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse
from typing import Callable

@Component
class LoggingMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        print(f"[LOG] {request.method} {request.path}")
        response = next(request)
        print(f"[LOG] Response {response.status_code}")
        return response
```

### 수동 등록 (MiddlewareChain)

더 세밀한 제어가 필요하면 `MiddlewareChain`을 직접 구성:

```python
from vessel import Configuration, Factory, MiddlewareChain, Component

@Component
class LoggingMiddleware(Middleware):
    # ...

@Component
class AuthMiddleware(Middleware):
    # ...

@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(
        self,
        logging: LoggingMiddleware,
        auth: AuthMiddleware
    ) -> MiddlewareChain:
        chain = MiddlewareChain()
        
        # 순서대로 추가
        chain.get_default_group().add(logging)
        chain.get_default_group().add(auth)
        
        return chain
```

## 의존성 주입

미들웨어도 의존성 주입을 사용할 수 있습니다:

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse
from typing import Callable

@Component
class UserService:
    def log_request(self, user_id: str, path: str):
        print(f"User {user_id} accessed {path}")

@Component
class UserTrackingMiddleware(Middleware):
    service: UserService  # 👈 필드 주입
    
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        user_id = request.headers.get("X-User-ID", "anonymous")
        self.service.log_request(user_id, request.path)
        
        return next(request)
```

## 조기 반환 (Early Return)

미들웨어에서 `next()`를 호출하지 않고 직접 응답을 반환하면, 이후 미들웨어와 핸들러는 실행되지 않습니다:

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse, HttpStatus
from typing import Callable

@Component
class RateLimitMiddleware(Middleware):
    def __init__(self):
        self.request_count = {}
    
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        ip = request.headers.get("X-Forwarded-For", "unknown")
        
        # IP별 요청 횟수 확인
        count = self.request_count.get(ip, 0)
        
        if count >= 100:  # 제한 초과
            # 조기 반환: next()를 호출하지 않음
            return HttpResponse(
                status_code=HttpStatus.TOO_MANY_REQUESTS,
                body={"error": "Rate limit exceeded"}
            )
        
        # 제한 내: 계속 진행
        self.request_count[ip] = count + 1
        return next(request)
```

## 실행 순서

미들웨어는 등록된 순서대로 실행됩니다:

```python
@Component
class FirstMiddleware(Middleware):
    def process(self, request, next):
        print("1. Before")
        response = next(request)
        print("6. After")
        return response

@Component
class SecondMiddleware(Middleware):
    def process(self, request, next):
        print("2. Before")
        response = next(request)
        print("5. After")
        return response

@Component
class ThirdMiddleware(Middleware):
    def process(self, request, next):
        print("3. Before")
        response = next(request)
        print("4. After")
        return response

# 핸들러는 마지막에 실행됨
# 출력:
# 1. Before
# 2. Before
# 3. Before
# [Handler 실행]
# 4. After
# 5. After
# 6. After
```

## 실전 예제

### CORS Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse
from typing import Callable

@Component
class CORSMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        # OPTIONS 요청 (preflight)은 즉시 응답
        if request.method == "OPTIONS":
            return HttpResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "3600"
                }
            )
        
        # 일반 요청은 처리 후 CORS 헤더 추가
        response = next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
```

### Request ID Middleware

```python
import uuid
from vessel import Component, Middleware, HttpRequest, HttpResponse
from typing import Callable

@Component
class RequestIDMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        # 요청에 고유 ID 생성
        request_id = str(uuid.uuid4())
        
        # Request context에 저장
        if not hasattr(request, 'context'):
            request.context = {}
        request.context['request_id'] = request_id
        
        # 헤더에도 추가
        request.headers['X-Request-ID'] = request_id
        
        # 처리
        response = next(request)
        
        # 응답에도 Request ID 추가
        response.headers['X-Request-ID'] = request_id
        
        return response
```

### Timing Middleware

```python
import time
from vessel import Component, Middleware, HttpRequest, HttpResponse
from typing import Callable

@Component
class TimingMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        start_time = time.time()
        
        response = next(request)
        
        duration = time.time() - start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        print(f"[TIMING] {request.method} {request.path} - {duration:.3f}s")
        
        return response
```

### IP Whitelist Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse, HttpStatus
from typing import Callable

@Component
class IPWhitelistMiddleware(Middleware):
    def __init__(self):
        self.allowed_ips = ["127.0.0.1", "192.168.1.100"]
    
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        client_ip = request.headers.get("X-Forwarded-For", "unknown")
        
        if client_ip not in self.allowed_ips:
            return HttpResponse(
                status_code=HttpStatus.FORBIDDEN,
                body={"error": "Access denied"}
            )
        
        return next(request)
```

### Request Validation Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse, HttpStatus
from typing import Callable

@Component
class RequestValidationMiddleware(Middleware):
    def process(
        self,
        request: HttpRequest,
        next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        # Content-Type 검증
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            
            if not content_type.startswith("application/json"):
                return HttpResponse(
                    status_code=HttpStatus.UNSUPPORTED_MEDIA_TYPE,
                    body={"error": "Content-Type must be application/json"}
                )
        
        # User-Agent 검증
        if not request.headers.get("User-Agent"):
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": "User-Agent header is required"}
            )
        
        return next(request)
```

## 내장 미들웨어

### AuthMiddleware

인증 시스템을 위한 특수 미들웨어 (별도 문서 참조):

```python
from vessel import Component, AuthMiddleware, Authenticator

@Component
class MyAuthMiddleware(AuthMiddleware):
    def __init__(self):
        super().__init__()
        self.register(JWTAuthenticator())
```

## 전체 예제

```python
from vessel import (
    Application, Controller, Get, Post,
    Component, Middleware, HttpRequest, HttpResponse,
    Configuration, Factory, MiddlewareChain
)
from typing import Callable
import time
import uuid

# 1. Logging Middleware
@Component
class LoggingMiddleware(Middleware):
    def process(self, request, next):
        print(f"→ {request.method} {request.path}")
        response = next(request)
        print(f"← {response.status_code}")
        return response

# 2. Request ID Middleware
@Component
class RequestIDMiddleware(Middleware):
    def process(self, request, next):
        request_id = str(uuid.uuid4())
        request.headers['X-Request-ID'] = request_id
        
        response = next(request)
        response.headers['X-Request-ID'] = request_id
        return response

# 3. Timing Middleware
@Component
class TimingMiddleware(Middleware):
    def process(self, request, next):
        start = time.time()
        response = next(request)
        duration = time.time() - start
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response

# 4. CORS Middleware
@Component
class CORSMiddleware(Middleware):
    def process(self, request, next):
        if request.method == "OPTIONS":
            return HttpResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        
        response = next(request)
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

# 미들웨어 순서 설정
@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(
        self,
        logging: LoggingMiddleware,
        request_id: RequestIDMiddleware,
        timing: TimingMiddleware,
        cors: CORSMiddleware
    ) -> MiddlewareChain:
        chain = MiddlewareChain()
        group = chain.get_default_group()
        
        # 순서: logging → request_id → timing → cors
        group.add(logging)
        group.add(request_id)
        group.add(timing)
        group.add(cors)
        
        return chain

# 컨트롤러
@Controller("/api")
class HelloController:
    @Get("/hello")
    def hello(self) -> dict:
        return {"message": "Hello, World!"}

# 애플리케이션
app = Application("__main__")
app.initialize()

if __name__ == "__main__":
    app.run(port=8000)
```

**실행 흐름:**
```
→ GET /api/hello          (LoggingMiddleware)
[Request ID 생성]          (RequestIDMiddleware)
[Timer 시작]               (TimingMiddleware)
[CORS 헤더 추가]           (CORSMiddleware)
[Handler 실행]
[Timer 종료]               (TimingMiddleware)
← 200                      (LoggingMiddleware)
```

## 정리

### ✅ 지원하는 기능
- 요청 전처리/후처리
- 조기 반환 (Early Return)
- 의존성 주입
- 자동 감지 (@Component)
- 수동 순서 제어 (MiddlewareChain)
- 체인 실행

### ❌ 지원하지 않는 기능
- 경로별 미들웨어 (모든 경로에 적용)
- 조건부 미들웨어 (직접 구현 필요)
- 비동기 미들웨어 (동기만 지원)
- 미들웨어 그룹핑 (단일 체인만 지원)

### 권장 사항

1. **순서 주의**: 미들웨어 순서가 중요합니다
   - 로깅 → 인증 → 타이밍 → CORS 순서 권장

2. **조기 반환 활용**: 인증 실패, Rate Limit 등에서 조기 반환

3. **의존성 주입 사용**: 서비스 로직은 주입받아 사용

4. **가벼운 로직**: 미들웨어는 모든 요청에 실행되므로 가볍게 유지
