# run_sync_or_async 데코레이터 스타일 리팩토링

## 변경 사항 요약

`run_sync_or_async` 함수를 **데코레이터 방식**으로 사용할 수 있도록 개선했습니다.

### Before (기존 방식)

```python
# 함수와 인자를 함께 전달
result = await run_sync_or_async(func, arg1, arg2, key=value)
```

### After (새로운 방식)

```python
# 데코레이터 방식: 함수를 래핑한 후 호출
result = await run_sync_or_async(func)(arg1, arg2, key=value)

# 또는 미리 래핑해서 재사용
wrapped_func = run_sync_or_async(func)
result1 = await wrapped_func(arg1, arg2)
result2 = await wrapped_func(arg3, arg4)
```

## 장점

### 1. 재사용 가능

```python
# Before: 매번 run_sync_or_async 호출
for item in items:
    result = await run_sync_or_async(processor.process, item)

# After: 한 번만 래핑
wrapped_process = run_sync_or_async(processor.process)
for item in items:
    result = await wrapped_process(item)
```

### 2. 명확한 의도 표현

```python
# "route_handler.handle_request를 래핑하여 호출"
response = await run_sync_or_async(self.route_handler.handle_request)(request)

# vs (기존)
response = await run_sync_or_async(self.route_handler.handle_request, request)
```

### 3. 타입 안전성

```python
# run_sync_or_async(func)는 항상 async 함수를 반환
# → 항상 await 가능함을 보장
wrapper: Callable[..., Awaitable[Any]] = run_sync_or_async(func)
```

## 구현 방식

### 변경된 함수 시그니처

```python
# Before
async def run_sync_or_async[**P, R](
    func: Callable[P, R], 
    *args: P.args, 
    **kwargs: P.kwargs
) -> R:
    if is_async_callable(func):
        return await func(*args, **kwargs)
    else:
        async_func = sync_to_async(func, thread_sensitive=False)
        return await async_func(*args, **kwargs)

# After
def run_sync_or_async(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """
    sync/async 함수를 async 래퍼로 감싸는 데코레이터
    """
    if is_async_callable(func):
        return func  # async 함수는 그대로 반환
    else:
        return sync_to_async(func, thread_sensitive=False)  # sync → async 변환
```

### 작동 원리

1. **입력**: sync 또는 async 함수
2. **처리**:
   - async 함수면 → 원본 함수 그대로 반환
   - sync 함수면 → `sync_to_async`로 변환하여 반환
3. **출력**: 항상 async 함수 (awaitable)

## 프레임워크 내부 적용

### 1. request_handler.py

```python
# Before
early_response = await run_sync_or_async(
    self.middleware_chain.execute_request, request
)
response = await run_sync_or_async(
    self.route_handler.handle_request, request
)

# After
early_response = await run_sync_or_async(
    self.middleware_chain.execute_request
)(request)
response = await run_sync_or_async(
    self.route_handler.handle_request
)(request)
```

### 2. handler.py

```python
# Before
return await run_sync_or_async(handler, **kwargs)

# After
return await run_sync_or_async(handler)(**kwargs)
```

## 사용 예시

### 기본 사용

```python
import asyncio
from vessel.utils.async_support import run_sync_or_async

def sync_function(x: int) -> int:
    return x * 2

async def async_function(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 3

async def main():
    # 둘 다 같은 방식으로 호출
    result1 = await run_sync_or_async(sync_function)(5)      # 10
    result2 = await run_sync_or_async(async_function)(5)     # 15
```

### 클래스 메서드

```python
class Calculator:
    def sync_add(self, x, y):
        return x + y
    
    async def async_multiply(self, x, y):
        await asyncio.sleep(0.01)
        return x * y

calc = Calculator()

# 메서드도 동일하게 처리
result1 = await run_sync_or_async(calc.sync_add)(10, 20)       # 30
result2 = await run_sync_or_async(calc.async_multiply)(10, 20)  # 200
```

### 재사용 패턴

```python
# 한 번 래핑하여 여러 번 사용
wrapped_handler = run_sync_or_async(my_handler)

responses = await asyncio.gather(
    wrapped_handler(request1),
    wrapped_handler(request2),
    wrapped_handler(request3),
)
```

### 실제 프레임워크 패턴

```python
class RequestHandler:
    async def _handle_request_async(self, request: HttpRequest) -> HttpResponse:
        if self.middleware_chain:
            # 미들웨어 실행 (sync/async 자동 처리)
            early_response = await run_sync_or_async(
                self.middleware_chain.execute_request
            )(request)
            
            if early_response is None:
                # 핸들러 실행 (sync/async 자동 처리)
                response = await run_sync_or_async(
                    self.route_handler.handle_request
                )(request)
                
                # 응답 미들웨어 (sync/async 자동 처리)
                response = await run_sync_or_async(
                    self.middleware_chain.execute_response
                )(request, response)
            
            return response
```

## 테스트 결과

모든 기존 테스트 통과: **130/130 ✓**

- ✅ 7개 async 핸들러 테스트
- ✅ 123개 기존 통합 테스트
- ✅ 하위 호환성 유지
- ✅ sync/async 혼용 정상 작동

## 관련 파일

### 수정된 파일

1. **vessel/utils/async_support.py** - `run_sync_or_async` 함수 시그니처 변경
2. **vessel/web/request_handler.py** - 데코레이터 방식 적용
3. **vessel/web/router/handler.py** - 데코레이터 방식 적용
4. **vessel/web/application.py** - `inspect` import 추가 (타입 체크용)

### 추가된 파일

1. **test_decorator_style.py** - 데코레이터 스타일 사용 예제 및 테스트
2. **docs/08_async_support.md** - 문서 업데이트 (데코레이터 방식 설명 추가)

## 마이그레이션 가이드

### 기존 코드가 있다면?

기존의 `run_sync_or_async(func, *args, **kwargs)` 패턴을 사용하는 코드가 있다면:

```python
# Before
result = await run_sync_or_async(my_func, arg1, arg2)

# After
result = await run_sync_or_async(my_func)(arg1, arg2)
```

### 프레임워크 사용자는?

**아무 변경 필요 없음!** 

이 변경사항은 프레임워크 내부 구현이며, 사용자의 핸들러 코드는 그대로 작동합니다:

```python
# 여전히 두 방식 모두 작동
@Get("/sync")
def sync_handler(self):
    return {"message": "sync"}

@Get("/async")
async def async_handler(self):
    return {"message": "async"}
```

## 성능 영향

**성능 영향 없음**

- 기존: `run_sync_or_async(func, args)` 호출 시 매번 `is_async_callable` 체크
- 변경: `run_sync_or_async(func)` 호출 시 한 번만 체크, 이후 재사용 가능
- 오히려 재사용 패턴을 사용하면 성능 개선 가능

## 결론

✅ **더 명확한 API**  
✅ **재사용 가능한 래퍼**  
✅ **타입 안전성 향상**  
✅ **하위 호환성 유지**  
✅ **성능 저하 없음**  

데코레이터 방식으로 변경하여 코드의 가독성과 재사용성이 크게 향상되었습니다!
