"""
run_sync_or_async 데코레이터 스타일 사용 예제

두 가지 사용 방법을 비교합니다:
1. 기존 방식: await run_sync_or_async(func, arg1, arg2)
2. 데코레이터 방식: await run_sync_or_async(func)(arg1, arg2)
"""

import asyncio
import time
from vessel.utils.async_support import run_sync_or_async


# 테스트용 함수들
def sync_function(x: int) -> int:
    """동기 함수"""
    time.sleep(0.1)
    return x * 2


async def async_function(x: int) -> int:
    """비동기 함수"""
    await asyncio.sleep(0.1)
    return x * 3


class Calculator:
    """테스트용 클래스"""

    def sync_method(self, x: int, y: int) -> int:
        """동기 메서드"""
        return x + y

    async def async_method(self, x: int, y: int) -> int:
        """비동기 메서드"""
        await asyncio.sleep(0.05)
        return x * y


async def test_decorator_style():
    """데코레이터 스타일 테스트"""
    print("=" * 60)
    print("run_sync_or_async 데코레이터 스타일 테스트")
    print("=" * 60)

    # 1. 일반 함수 - 데코레이터 방식
    print("\n[1] 일반 함수 호출 (데코레이터 방식)")
    result = await run_sync_or_async(sync_function)(5)
    print(f"sync_function(5) = {result}")  # 10

    result = await run_sync_or_async(async_function)(5)
    print(f"async_function(5) = {result}")  # 15

    # 2. 클래스 메서드 - 데코레이터 방식
    print("\n[2] 클래스 메서드 호출 (데코레이터 방식)")
    calc = Calculator()

    result = await run_sync_or_async(calc.sync_method)(10, 20)
    print(f"calc.sync_method(10, 20) = {result}")  # 30

    result = await run_sync_or_async(calc.async_method)(10, 20)
    print(f"calc.async_method(10, 20) = {result}")  # 200

    # 3. 람다 함수 - 데코레이터 방식
    print("\n[3] 람다 함수 (데코레이터 방식)")
    add = lambda x, y: x + y
    result = await run_sync_or_async(add)(100, 50)
    print(f"lambda(100, 50) = {result}")  # 150

    # 4. 실제 사용 예시 - RouteHandler 스타일
    print("\n[4] 실제 사용 예시 (RouteHandler 스타일)")

    class MockRouteHandler:
        def handle_request(self, request):
            return f"Handled: {request}"

    class MockMiddleware:
        async def execute_request(self, request):
            await asyncio.sleep(0.01)
            return None  # None이면 핸들러로 진행

        def execute_response(self, request, response):
            return f"Processed: {response}"

    handler = MockRouteHandler()
    middleware = MockMiddleware()

    request = {"path": "/test", "method": "GET"}

    # 미들웨어 실행 (async)
    early_response = await run_sync_or_async(middleware.execute_request)(request)
    print(f"Middleware early_response: {early_response}")

    if early_response is None:
        # 핸들러 실행 (sync)
        response = await run_sync_or_async(handler.handle_request)(request)
        print(f"Handler response: {response}")

        # 응답 미들웨어 (sync)
        final_response = await run_sync_or_async(middleware.execute_response)(
            request, response
        )
        print(f"Final response: {final_response}")

    # 5. 동시 실행 (concurrent execution)
    print("\n[5] 동시 실행 예시")
    start = time.time()

    results = await asyncio.gather(
        run_sync_or_async(sync_function)(1),
        run_sync_or_async(sync_function)(2),
        run_sync_or_async(async_function)(3),
        run_sync_or_async(async_function)(4),
    )

    elapsed = time.time() - start
    print(f"Results: {results}")  # [2, 4, 9, 12]
    print(f"Elapsed time: {elapsed:.2f}s (should be ~0.1s due to concurrent execution)")

    # 6. 데코레이터로 함수 감싸기
    print("\n[6] 함수를 미리 감싸서 재사용")

    # 미리 래핑한 함수 생성
    wrapped_sync = run_sync_or_async(sync_function)
    wrapped_async = run_sync_or_async(async_function)

    # 여러 번 재사용 가능
    r1 = await wrapped_sync(10)
    r2 = await wrapped_sync(20)
    r3 = await wrapped_async(10)
    r4 = await wrapped_async(20)

    print(f"Reused wrapped functions: {r1}, {r2}, {r3}, {r4}")

    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    # Python 3.7+ 에서 실행
    asyncio.run(test_decorator_style())
