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
from typing import Optional, Any

class MyMiddleware(Middleware):
    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """
        요청 처리 전 실행
        
        Args:
            request: HTTP 요청
            
        Returns:
            None: 다음 미들웨어/핸들러로 진행
            Any: 반환값이 있으면 early return (라우트 핸들러 스킵)
        """
        # 요청 전처리
        print(f"Request: {request.method} {request.path}")
        return None  # 다음으로 진행
    
    def process_response(
        self, 
        request: HttpRequest, 
        response: HttpResponse
    ) -> HttpResponse:
        """
        응답 처리 후 실행
        
        Args:
            request: HTTP 요청
            response: HTTP 응답
            
        Returns:
            HttpResponse: 수정된 응답 (또는 원본 응답)
        """
        # 응답 후처리
        print(f"Response: {response.status_code}")
        return response
```

## 미들웨어 등록

### 수동 등록 (@Factory 사용)

미들웨어는 `@Factory`를 통해 `MiddlewareChain`에 수동으로 등록합니다:

```python
from vessel import Component, Configuration, Factory, Middleware, MiddlewareChain
from vessel import HttpRequest, HttpResponse

@Component
class LoggingMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        print(f"[LOG] {request.method} {request.path}")
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        print(f"[LOG] Response {response.status_code}")
        return response

@Configuration
class MiddlewareConfig:
    @Factory
    def middleware_chain(self, logging: LoggingMiddleware) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(logging)
        return chain
```

### 여러 미들웨어 등록

`MiddlewareChain`에 여러 미들웨어를 순서대로 추가:

```python
from vessel import Configuration, Factory, MiddlewareChain, Component

@Component
class LoggingMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        print(f"[LOG] {request.method} {request.path}")
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response

@Component
class AuthMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # 인증 로직
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response

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

@Component
class UserService:
    def log_request(self, user_id: str, path: str):
        print(f"User {user_id} accessed {path}")

@Component
class UserTrackingMiddleware(Middleware):
    service: UserService  # 👈 필드 주입
    
    def process_request(self, request: HttpRequest):
        user_id = request.headers.get("X-User-ID", "anonymous")
        self.service.log_request(user_id, request.path)
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response
```

## 조기 반환 (Early Return)

`process_request()`에서 `None`이 아닌 값을 반환하면, 이후 미들웨어와 핸들러는 실행되지 않습니다:

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class RateLimitMiddleware(Middleware):
    def __init__(self):
        self.request_count = {}
    
    def process_request(self, request: HttpRequest):
        ip = request.headers.get("X-Forwarded-For", "unknown")
        
        # IP별 요청 횟수 확인
        count = self.request_count.get(ip, 0)
        
        if count >= 100:  # 제한 초과
            # 조기 반환: HttpResponse를 반환하면 핸들러 실행 안 됨
            return HttpResponse(
                status_code=429,
                body={"error": "Rate limit exceeded"}
            )
        
        # 제한 내: 계속 진행
        self.request_count[ip] = count + 1
        return None  # None을 반환하면 다음으로 진행
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response
```

## 실행 순서

미들웨어는 등록된 순서대로 `process_request()`를 실행하고, 역순으로 `process_response()`를 실행합니다:

```python
@Component
class FirstMiddleware(Middleware):
    def process_request(self, request):
        print("1. First - Request")
        return None
    
    def process_response(self, request, response):
        print("6. First - Response")
        return response

@Component
class SecondMiddleware(Middleware):
    def process_request(self, request):
        print("2. Second - Request")
        return None
    
    def process_response(self, request, response):
        print("5. Second - Response")
        return response

@Component
class ThirdMiddleware(Middleware):
    def process_request(self, request):
        print("3. Third - Request")
        return None
    
    def process_response(self, request, response):
        print("4. Third - Response")
        return response

# 실행 순서:
# 1. First - Request (등록 순서대로)
# 2. Second - Request
# 3. Third - Request
# [Handler 실행]
# 4. Third - Response (역순으로)
# 5. Second - Response
# 6. First - Response
```

## 실전 예제

### CORS Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class CORSMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # OPTIONS 요청 (preflight)은 즉시 응답 (early return)
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
        return None  # 일반 요청은 계속 진행
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        # 일반 요청은 처리 후 CORS 헤더 추가
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
```

### Request ID Middleware

```python
import uuid
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class RequestIDMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # 요청에 고유 ID 생성
        request_id = str(uuid.uuid4())
        
        # Request context에 저장
        if not hasattr(request, 'context'):
            request.context = {}
        request.context['request_id'] = request_id
        
        # 헤더에도 추가
        request.headers['X-Request-ID'] = request_id
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        # 응답에도 Request ID 추가
        if hasattr(request, 'context') and 'request_id' in request.context:
            response.headers['X-Request-ID'] = request.context['request_id']
        return response
```

### Timing Middleware

```python
import time
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class TimingMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # 시작 시간을 context에 저장
        if not hasattr(request, 'context'):
            request.context = {}
        request.context['start_time'] = time.time()
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        # 종료 시간 계산
        if hasattr(request, 'context') and 'start_time' in request.context:
            duration = time.time() - request.context['start_time']
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            print(f"[TIMING] {request.method} {request.path} - {duration:.3f}s")
        return response
```

### IP Whitelist Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class IPWhitelistMiddleware(Middleware):
    def __init__(self):
        self.allowed_ips = ["127.0.0.1", "192.168.1.100"]
    
    def process_request(self, request: HttpRequest):
        client_ip = request.headers.get("X-Forwarded-For", "unknown")
        
        if client_ip not in self.allowed_ips:
            # Early return - 허용되지 않은 IP
            return HttpResponse(
                status_code=403,
                body={"error": "Access denied"}
            )
        return None  # 허용된 IP는 계속 진행
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response
```

### Request Validation Middleware

```python
from vessel import Component, Middleware, HttpRequest, HttpResponse

@Component
class RequestValidationMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # Content-Type 검증
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            
            if not content_type.startswith("application/json"):
                return HttpResponse(
                    status_code=415,
                    body={"error": "Content-Type must be application/json"}
                )
        
        # User-Agent 검증
        if not request.headers.get("User-Agent"):
            return HttpResponse(
                status_code=400,
                body={"error": "User-Agent header is required"}
            )
        
        return None  # 검증 통과
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response
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
    Application, Controller, Get,
    Component, Middleware, HttpRequest, HttpResponse,
    Configuration, Factory, MiddlewareChain
)
import time
import uuid

# 1. Logging Middleware
@Component
class LoggingMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        print(f"→ {request.method} {request.path}")
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        print(f"← {response.status_code}")
        return response

# 2. Request ID Middleware
@Component
class RequestIDMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        request_id = str(uuid.uuid4())
        if not hasattr(request, 'context'):
            request.context = {}
        request.context['request_id'] = request_id
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        if hasattr(request, 'context') and 'request_id' in request.context:
            response.headers['X-Request-ID'] = request.context['request_id']
        return response

# 3. Timing Middleware
@Component
class TimingMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        if not hasattr(request, 'context'):
            request.context = {}
        request.context['start_time'] = time.time()
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        if hasattr(request, 'context') and 'start_time' in request.context:
            duration = time.time() - request.context['start_time']
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response

# 4. CORS Middleware
@Component
class CORSMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        if request.method == "OPTIONS":
            return HttpResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
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
→ GET /api/hello                    (LoggingMiddleware - request)
[Request ID 생성]                    (RequestIDMiddleware - request)
[Timer 시작]                         (TimingMiddleware - request)
[CORS preflight 체크]               (CORSMiddleware - request)
[Handler 실행]
[CORS 헤더 추가]                    (CORSMiddleware - response)
[Timer 종료]                         (TimingMiddleware - response)
[Request ID 응답 추가]               (RequestIDMiddleware - response)
← 200                                (LoggingMiddleware - response)
```

## 정리

### ✅ 지원하는 기능
- 요청 전처리 (`process_request`)
- 응답 후처리 (`process_response`)
- 조기 반환 (Early Return)
- 의존성 주입 (필드 주입)
- 미들웨어 그룹 (`MiddlewareGroup`)
- 수동 순서 제어 (`MiddlewareChain`)
- 개별 미들웨어 활성화/비활성화

### ❌ 지원하지 않는 기능
- 자동 감지 (반드시 `@Factory`로 `MiddlewareChain` 구성 필요)
- 경로별 미들웨어 (모든 경로에 적용)
- 비동기 미들웨어 (동기만 지원)

### 권장 사항

1. **순서 주의**: 미들웨어 순서가 중요합니다
   - 로깅 → 인증 → 타이밍 → CORS 순서 권장

2. **조기 반환 활용**: 인증 실패, Rate Limit 등에서 조기 반환

3. **의존성 주입 사용**: 서비스 로직은 주입받아 사용

4. **가벼운 로직**: 미들웨어는 모든 요청에 실행되므로 가볍게 유지
