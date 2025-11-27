# Vessel - Python Dependency Injection Framework

Spring IOC 스타일의 Python 의존성 주입 프레임워크입니다.

## 주요 기능

### 1. 의존성 주입
- `@Component`: 컴포넌트 클래스 등록
- `@Factory`: 팩토리 메서드를 통한 빈 생성
- 타입 힌트 기반 자동 의존성 주입
- Topological Sort를 통한 순환 의존성 해결

### 2. HTTP 라우팅
- `@Controller`: HTTP 컨트롤러 정의
- `@RequestMapping`: URL 매핑
- `@Get`, `@Post`, `@Put`, `@Delete`: HTTP 메서드 핸들러

### 3. Async/Sync 지원 (NEW! 🚀)
- **완벽한 하위 호환성**: 기존 동기 코드 수정 불필요
- **투명한 통합**: sync/async 핸들러를 자유롭게 혼용
- **점진적 마이그레이션**: 필요한 부분만 async로 전환
- `asgiref` 기반의 안정적인 구현

### 4. 핸들러 인터셉터
- 핸들러 실행 전/후 처리
- 에러 핸들링
- 중첩 가능한 인터셉터
- 커스텀 인터셉터 생성 가능

## 기본 사용 예제

```python
from vessel import Component, Factory, Controller, RequestMapping, Get

@Component
class MyService:
    def process(self, data: str) -> str:
        return f"Processed: {data}"

@Controller
@RequestMapping("/api")
class MyController:
    service: MyService
    
    @Get()
    def handle(self, request):
        return self.service.process(request.data)
```

## Async/Sync 지원 예제

### 기존 동기 코드 그대로 작동

```python
# 기존 방식 - 아무 변경 없이 계속 사용 가능
response = app.handle_request(request)
```

### Async 핸들러 사용

```python
@Controller
@RequestMapping("/api")
class AsyncController:
    service: MyService
    
    @Get()
    async def fetch_data(self, request):
        # async 핸들러 - 외부 API 호출 등에 유용
        data = await external_api_call()
        return {"data": data}
```

### Async 컨텍스트에서 호출

```python
# Async 환경에서는 await로 호출
async def main():
    response = await app.handle_request(request)
    
# 여러 요청 동시 처리
responses = await asyncio.gather(
    app.handle_request(request1),
    app.handle_request(request2),
    app.handle_request(request3)
)
```

더 자세한 내용은 [Async Support 가이드](docs/08_async_support.md)와 [Async 호환성 가이드](docs/09_async_compatibility.md)를 참조하세요.

## 인터셉터 사용 예제

### 내장 인터셉터 사용

```python
from vessel import Controller, Get, Transaction, Logging

@Controller
@RequestMapping("/api")
class MyController:
    service: MyService
    
    @Get()
    @Logging      # 로깅 인터셉터
    @Transaction  # 트랜잭션 인터셉터
    def handle(self, request):
        return self.service.process(request.data)
```

### 커스텀 인터셉터 만들기

```python
from vessel import HandlerInterceptor
from typing import Any

class PerformanceInterceptor(HandlerInterceptor):
    """성능 측정 인터셉터"""
    
    def before(self, *args, **kwargs) -> tuple:
        self.start_time = time.time()
        return args, kwargs
    
    def after(self, result: Any, *args, **kwargs) -> Any:
        elapsed = time.time() - self.start_time
        print(f"실행 시간: {elapsed*1000:.2f}ms")
        return result
    
    def on_error(self, error: Exception, *args, **kwargs):
        print(f"에러 발생: {error}")
        raise error

# 데코레이터로 만들기
def Performance(func):
    from vessel.decorators.handler import HandlerContainer, register_container
    
    if not hasattr(func, '__pydi_container__'):
        container = HandlerContainer(func, "GET", "")
        func.__pydi_container__ = container
        register_container(func, container)
    
    func.__pydi_container__.add_interceptor(PerformanceInterceptor())
    return func

# 사용
@Controller
class MyController:
    @Get()
    @Performance
    def handle(self, request):
        return {"result": "ok"}
```

## 인터셉터 실행 순서

데코레이터는 아래에서 위로 적용되며, 인터셉터는 다음 순서로 실행됩니다:

```python
@Get()
@Logging        # 3. Logging.before() 실행
@Transaction    # 2. Transaction.before() 실행
def handler():  # 1. 핸들러 실행
    pass        # 4. Transaction.after() 실행
                # 5. Logging.after() 실행
```

더 자세한 예제는 `example.py`와 `custom_interceptor_example.py`를 참고하세요.
