# Async/Sync Handler Support

## Overview

Vessel 프레임워크는 `asgiref`를 사용하여 **동기(sync)** 및 **비동기(async)** 핸들러를 모두 지원합니다. 개발자는 핸들러를 `async def`로 정의하거나 일반 `def`로 정의할 수 있으며, 프레임워크가 자동으로 적절하게 처리합니다.

## Key Features

1. **자동 감지 및 변환**: sync 함수는 자동으로 비동기 컨텍스트에서 실행됩니다.
2. **투명한 통합**: 서비스와 핸들러에서 sync/async를 자유롭게 혼용할 수 있습니다.
3. **동시성 지원**: 여러 요청을 비동기적으로 처리할 수 있습니다.
4. **미들웨어 지원**: 미들웨어도 sync/async 모두 지원합니다.

## Basic Usage

### Sync Handler

일반적인 동기 핸들러:

```python
from vessel import Controller, Get, Component

@Component
class UserService:
    def get_user(self, user_id: int):
        # 동기 데이터베이스 조회
        return {"id": user_id, "name": "John"}

@Controller("/api")
class UserController:
    service: UserService
    
    @Get("/users/{user_id}")
    def get_user(self, user_id: int):
        # 동기 핸들러
        return self.service.get_user(user_id)
```

### Async Handler

비동기 핸들러:

```python
import asyncio
from vessel import Controller, Get, Component

@Component
class AsyncUserService:
    async def get_user(self, user_id: int):
        # 비동기 데이터베이스 조회 시뮬레이션
        await asyncio.sleep(0.1)
        return {"id": user_id, "name": "Jane"}

@Controller("/api")
class AsyncUserController:
    service: AsyncUserService
    
    @Get("/users/{user_id}")
    async def get_user(self, user_id: int):
        # 비동기 핸들러
        user = await self.service.get_user(user_id)
        return user
```

### Mixed Sync/Async

동기 및 비동기 컴포넌트를 함께 사용:

```python
@Controller("/api")
class MixedController:
    sync_service: SyncService      # 동기 서비스
    async_service: AsyncService    # 비동기 서비스
    
    @Get("/mixed")
    async def mixed_handler(self):
        # async 핸들러에서 sync 서비스 사용
        sync_result = self.sync_service.get_data()
        
        # async 서비스 사용
        async_result = await self.async_service.fetch_data()
        
        return {
            "sync": sync_result,
            "async": async_result
        }
```

## How It Works

### 1. Async Support Utilities

`vessel.utils.async_support` 모듈은 sync/async 함수를 투명하게 처리하는 유틸리티를 제공합니다:

```python
from vessel.utils.async_support import run_sync_or_async, is_async_callable

# 함수가 async인지 확인
is_async = is_async_callable(my_function)

# ========== run_sync_or_async: 데코레이터 방식 사용 ==========

# 방법 1: 직접 호출 시 사용
result = await run_sync_or_async(my_function)(arg1, arg2)

# 방법 2: 미리 래핑해서 재사용 (권장)
wrapped_function = run_sync_or_async(my_function)
result1 = await wrapped_function(arg1, arg2)
result2 = await wrapped_function(arg3, arg4)

# 방법 3: 메서드 호출 (실제 프레임워크 내부 사용 방식)
response = await run_sync_or_async(self.route_handler.handle_request)(request)
early_response = await run_sync_or_async(self.middleware_chain.execute_request)(request)

# 실제 사용 예시
class MyService:
    def sync_method(self, data):
        return process_data(data)
    
    async def async_method(self, data):
        return await fetch_external_data(data)

service = MyService()

# 두 메서드 모두 동일한 방식으로 호출 가능
result1 = await run_sync_or_async(service.sync_method)("data1")
result2 = await run_sync_or_async(service.async_method)("data2")
```

**왜 데코레이터 방식인가?**

`run_sync_or_async(func)`는 함수를 래핑한 async 함수를 반환합니다:
- sync 함수 → `sync_to_async`로 변환된 async 함수 반환
- async 함수 → 원본 함수 그대로 반환

이렇게 하면:
1. **재사용 가능**: 한 번 래핑하면 여러 번 호출 가능
2. **명확한 의도**: `run_sync_or_async(func)(args)` - "func를 래핑한 후 호출"
3. **타입 안전성**: 반환된 async 함수는 항상 `await` 가능

### 2. Handler Execution Flow

요청 처리 흐름:

```
HttpRequest
    ↓
RequestHandler.handle_request() [async]
    ↓
Middleware Chain [sync/async 자동 처리]
    ↓
RouteHandler.handle_request() [async]
    ↓
RouteHandler._invoke_handler() [async]
    ↓
run_sync_or_async(handler, **kwargs)
    ↓ (sync 함수인 경우)
    sync_to_async(handler)  # asgiref 사용
    ↓
Handler Result
```

### 3. Under the Hood

프레임워크는 `asgiref`의 `sync_to_async`와 `async_to_sync`를 사용합니다:

- **sync_to_async**: 동기 함수를 별도 스레드에서 실행하여 이벤트 루프를 블로킹하지 않습니다.
- **async_to_sync**: 비동기 함수를 동기적으로 실행합니다 (DevServer에서 사용).

## Performance Considerations

### Async의 장점

1. **I/O 바운드 작업**: 데이터베이스 쿼리, HTTP 요청, 파일 I/O 등에서 효율적입니다.
2. **동시성**: 여러 요청을 동시에 처리할 수 있습니다.
3. **리소스 효율성**: 스레드보다 적은 오버헤드로 많은 동시 연결을 처리합니다.

### Sync를 사용해야 할 때

1. **CPU 바운드 작업**: 복잡한 계산이나 데이터 처리
2. **레거시 라이브러리**: async를 지원하지 않는 라이브러리 사용 시
3. **간단한 로직**: 간단한 CRUD 작업이나 즉시 반환되는 작업

### Example: Concurrent Requests

```python
import asyncio

# 동시에 여러 요청 처리
async def process_multiple_requests():
    requests = [
        app.handle_request(HttpRequest(method="GET", path="/api/user/1")),
        app.handle_request(HttpRequest(method="GET", path="/api/user/2")),
        app.handle_request(HttpRequest(method="GET", path="/api/user/3")),
    ]
    
    # 모든 요청을 동시에 처리
    responses = await asyncio.gather(*requests)
    return responses
```

## DevServer Integration

DevServer는 `asyncio.run()`을 사용하여 async 핸들러를 동기적으로 실행합니다:

```python
# vessel/web/server.py
response = asyncio.run(app.handle_request(request))
```

프로덕션에서는 Uvicorn, Hypercorn 등의 ASGI 서버를 사용하는 것이 좋습니다.

## Middleware Support

미들웨어도 sync/async를 자동으로 지원합니다:

```python
from vessel.web.middleware import Middleware

class AsyncMiddleware(Middleware):
    async def process_request(self, request: HttpRequest):
        # 비동기 작업
        await some_async_operation()
        return None  # 계속 진행
    
    async def process_response(self, request: HttpRequest, response: HttpResponse):
        # 비동기 후처리
        await log_response_async(response)
        return response

class SyncMiddleware(Middleware):
    def process_request(self, request: HttpRequest):
        # 동기 작업
        validate_request(request)
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        # 동기 후처리
        add_headers(response)
        return response
```

## Best Practices

### 1. Async를 전파하세요

비동기 함수는 호출 체인 전체에 전파되어야 합니다:

```python
# ✓ 좋은 예
@Component
class AsyncService:
    async def fetch_data(self):
        return await db.query()

@Controller
class AsyncController:
    service: AsyncService
    
    @Get("/data")
    async def get_data(self):  # async 핸들러
        return await self.service.fetch_data()

# ✗ 나쁜 예 (await 없이 async 함수 호출)
@Get("/data")
def get_data(self):  # sync 핸들러
    # 이렇게 하면 코루틴 객체가 반환됩니다!
    return self.service.fetch_data()  # await 없음
```

### 2. 블로킹 작업은 sync_to_async 사용

CPU 집약적이거나 블로킹 작업은 명시적으로 처리:

```python
from asgiref.sync import sync_to_async

@Component
class ProcessingService:
    def heavy_computation(self, data):
        # CPU 집약적 작업
        return complex_calculation(data)
    
    async def async_heavy_computation(self, data):
        # 별도 스레드에서 실행
        return await sync_to_async(self.heavy_computation)(data)
```

### 3. 적절한 타임아웃 설정

비동기 작업에는 타임아웃을 설정하세요:

```python
import asyncio

@Get("/data")
async def get_data(self):
    try:
        result = await asyncio.wait_for(
            self.service.fetch_data(),
            timeout=5.0  # 5초 타임아웃
        )
        return result
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}
```

## Testing

pytest-asyncio를 사용하여 async 핸들러를 테스트할 수 있습니다:

```python
import pytest
from vessel.web.http.request import HttpRequest

@pytest.mark.asyncio
async def test_async_handler(request_handler):
    request = HttpRequest(method="GET", path="/api/data")
    response = await request_handler.handle_request(request)
    
    assert response.status_code == 200
```

## Limitations

1. **DevServer**: 개발 서버는 단일 스레드로 실행되므로 프로덕션에는 적합하지 않습니다.
2. **Legacy Code**: 완전히 동기적인 레거시 코드는 async의 이점을 완전히 활용하지 못할 수 있습니다.
3. **Debugging**: 비동기 코드는 디버깅이 더 어려울 수 있습니다.

## Production Deployment

프로덕션 환경에서는 ASGI 서버를 사용하세요:

### Uvicorn

```bash
pip install uvicorn

# ASGI 앱 생성 (별도 파일)
# asgi.py
from vessel import Application

app = Application("myapp")
app.initialize()

# 실행
uvicorn asgi:app --host 0.0.0.0 --port 8000 --workers 4
```

### Hypercorn

```bash
pip install hypercorn

hypercorn asgi:app --bind 0.0.0.0:8000 --workers 4
```

## See Also

- [asgiref Documentation](https://github.com/django/asgiref)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Middleware Documentation](06_middleware.md)
- [Testing Documentation](../TESTING.md)
