# Async/Sync 호환성 가이드

## 개요

Vessel 프레임워크는 **완벽한 하위 호환성**을 유지하면서 async/await를 지원합니다. 기존 동기 코드는 수정 없이 그대로 작동하며, 새로운 비동기 코드도 자유롭게 사용할 수 있습니다.

## 핵심 원칙

### 투명한 Async 지원

모든 요청 처리 메서드(`handle_request`)는 **양방향 호환**됩니다:

```python
# ✅ 방법 1: 동기 호출 (기존 코드 - 호환성)
response = app.handle_request(request)

# ✅ 방법 2: 비동기 호출 (새로운 스타일 - 성능)
response = await app.handle_request(request)
```

두 방식 모두 정확히 같은 결과를 반환합니다!

## 작동 원리

### 지능형 컨텍스트 감지

프레임워크는 호출 컨텍스트를 자동으로 감지합니다:

```python
def handle_request(self, request):
    coro = self._handle_request_async(request)
    
    try:
        # 이미 async 컨텍스트에 있는지 확인
        loop = asyncio.get_running_loop()
        # ✅ Async 컨텍스트 → 코루틴 반환 (await 가능)
        return coro
    except RuntimeError:
        # ✅ Sync 컨텍스트 → asyncio.run()으로 실행
        return asyncio.run(coro)
```

### 계층별 호환성

```
Application.handle_request()      ← Sync/Async 호환
    ↓
RequestHandler.handle_request()   ← Sync/Async 호환
    ↓
RouteHandler.handle_request()     ← Sync/Async 호환
    ↓
Handler Method (sync or async)    ← 자동 처리
```

모든 계층에서 동일한 패턴을 사용하여 일관성을 유지합니다.

## 사용 예시

### 1. 기존 코드 (100% 호환)

```python
from vessel import Application
from vessel.web.http.request import HttpRequest

app = Application("myapp")
app.initialize()

# 동기 호출 - 변경 없음!
request = HttpRequest(method="GET", path="/api/users")
response = app.handle_request(request)
print(response.body)
```

### 2. 새로운 비동기 코드

```python
import asyncio
from vessel import Application
from vessel.web.http.request import HttpRequest

app = Application("myapp")
app.initialize()

async def main():
    # 비동기 호출
    request = HttpRequest(method="GET", path="/api/users")
    response = await app.handle_request(request)
    print(response.body)

asyncio.run(main())
```

### 3. 동시 요청 처리

```python
async def process_multiple():
    requests = [
        app.handle_request(HttpRequest(method="GET", path="/api/user/1")),
        app.handle_request(HttpRequest(method="GET", path="/api/user/2")),
        app.handle_request(HttpRequest(method="GET", path="/api/user/3")),
    ]
    
    # 모든 요청을 동시에 처리
    responses = await asyncio.gather(*requests)
    return responses
```

## 마이그레이션 전략

### 단계별 전환

기존 프로젝트를 점진적으로 async로 전환할 수 있습니다:

#### Phase 1: 핸들러만 async로 변경

```python
@Controller("/api")
class UserController:
    service: UserService  # 기존 sync 서비스
    
    @Get("/users/{id}")
    async def get_user(self, id: int):  # 핸들러만 async
        # sync 서비스는 자동으로 async로 변환됨
        user = self.service.get_user(id)
        return user
```

#### Phase 2: 서비스도 async로 변경

```python
@Component
class AsyncUserService:
    async def get_user(self, id: int):  # 서비스를 async로
        result = await db.query_async(...)
        return result

@Controller("/api")
class UserController:
    service: AsyncUserService  # async 서비스
    
    @Get("/users/{id}")
    async def get_user(self, id: int):
        user = await self.service.get_user(id)  # await 사용
        return user
```

#### Phase 3: 테스트 코드 업데이트 (선택사항)

```python
# 기존 방식 (여전히 작동)
def test_get_user():
    response = app.handle_request(request)
    assert response.status_code == 200

# 새로운 방식 (더 나은 성능)
@pytest.mark.asyncio
async def test_get_user():
    response = await app.handle_request(request)
    assert response.status_code == 200
```

## 성능 고려사항

### Sync vs Async 오버헤드

동기 호출 시 약간의 오버헤드가 있습니다:

```python
# Sync 호출: asyncio.run() 오버헤드 (~0.1-0.5ms)
response = app.handle_request(request)

# Async 호출: 오버헤드 없음
response = await app.handle_request(request)
```

하지만 대부분의 경우 이 오버헤드는 무시할 수 있습니다.

### 언제 Async를 사용해야 하나?

**Async를 사용하세요:**
- 동시에 여러 요청을 처리할 때
- I/O 바운드 작업 (DB, HTTP, 파일)이 많을 때
- 높은 동시성이 필요할 때

**Sync를 사용하세요:**
- 간단한 CRUD 작업
- CPU 바운드 작업
- 레거시 라이브러리를 사용할 때

## 테스트 가이드

### 기존 테스트 (호환성)

```python
def test_endpoint():
    """기존 동기 테스트 - 수정 불필요"""
    app = Application("myapp")
    app.initialize()
    
    request = HttpRequest(method="GET", path="/api/test")
    response = app.handle_request(request)
    
    assert response.status_code == 200
```

### 새로운 Async 테스트

```python
@pytest.mark.asyncio
async def test_endpoint():
    """새로운 비동기 테스트"""
    app = Application("myapp")
    app.initialize()
    
    request = HttpRequest(method="GET", path="/api/test")
    response = await app.handle_request(request)
    
    assert response.status_code == 200
```

### 혼합 테스트

```python
class TestAPI:
    def test_sync(self):
        """동기 테스트"""
        response = app.handle_request(request)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_async(self):
        """비동기 테스트"""
        response = await app.handle_request(request)
        assert response.status_code == 200
```

## 주의사항

### 1. 중첩된 Event Loop 방지

```python
# ❌ 잘못된 사용
async def handler():
    # async 컨텍스트 내에서 sync 호출하면 새로운 이벤트 루프 생성 시도
    response = app.handle_request(request)  # RuntimeError!

# ✅ 올바른 사용
async def handler():
    response = await app.handle_request(request)
```

### 2. DevServer의 제한

```python
# DevServer는 asyncio.run()을 사용
# 프로덕션에서는 Uvicorn/Hypercorn 사용 권장
app.run()  # 개발용만
```

## 프로덕션 배포

### Uvicorn (권장)

```python
# asgi.py
from vessel import Application

app = Application("myapp")
app.initialize()

# ASGI 호환을 위한 래퍼
async def application(scope, receive, send):
    if scope["type"] == "http":
        # HTTP 요청을 HttpRequest로 변환
        request = convert_asgi_to_httprequest(scope, receive)
        response = await app.handle_request(request)  # async 호출
        await send_response(response, send)

# 실행: uvicorn asgi:application --workers 4
```

## FAQ

### Q: 기존 코드를 수정해야 하나요?
**A:** 아니요! 기존 동기 코드는 그대로 작동합니다.

### Q: 성능이 더 나빠지나요?
**A:** 동기 호출 시 약간의 오버헤드가 있지만 무시할 수 있는 수준입니다. 비동기 호출은 오버헤드가 없습니다.

### Q: 언제 async로 전환해야 하나요?
**A:** 필요할 때 점진적으로 전환하세요. 급할 필요 없습니다.

### Q: 테스트를 모두 수정해야 하나요?
**A:** 아니요! 기존 테스트는 그대로 작동합니다. 새로운 테스트만 async로 작성하세요.

## 결론

Vessel 프레임워크의 async 지원은:

✅ **완벽한 하위 호환성** - 기존 코드 수정 불필요  
✅ **점진적 마이그레이션** - 필요한 부분만 async로 변경  
✅ **투명한 통합** - sync/async를 자유롭게 혼용  
✅ **성능 최적화** - async 호출 시 오버헤드 없음  

기존 동기 코드를 유지하면서 새로운 비동기 코드를 추가할 수 있는 완벽한 솔루션입니다!
