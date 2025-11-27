"""
Async Support Utilities

asgiref를 사용하여 sync/async 함수를 유연하게 처리하는 유틸리티
"""

import asyncio
import inspect
from typing import Any, Awaitable, Callable, Coroutine, TypeVar, Union, cast
from asgiref.sync import sync_to_async, async_to_sync

T = TypeVar("T")


def is_async_callable(func: Callable[..., Any]) -> bool:
    """
    함수가 async 함수인지 확인

    Args:
        func: 확인할 함수

    Returns:
        bool: async 함수면 True, 아니면 False
    """
    # 코루틴 함수인지 확인
    if asyncio.iscoroutinefunction(func):
        return True

    # 클래스 메서드의 경우 __func__ 속성을 확인
    if hasattr(func, "__func__"):
        return asyncio.iscoroutinefunction(func.__func__)

    # __call__ 메서드가 async인지 확인 (callable 객체)
    if hasattr(func, "__call__") and asyncio.iscoroutinefunction(func.__call__):
        return True

    return False


def run_sync_or_async[**P, R](
    func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
    """
    sync 또는 async 함수를 async 래퍼로 감싸는 데코레이터

    사용 방법:
    1. 데코레이터로 사용: @run_sync_or_async
    2. 함수 호출 시 사용: await run_sync_or_async(func)(args)

    sync 함수인 경우 sync_to_async로 변환
    async 함수인 경우 그대로 반환

    Args:
        func: 래핑할 함수 (sync 또는 async)

    Returns:
        async 함수 래퍼

    Examples:
        >>> # 방법 1: 데코레이터로 사용
        >>> @run_sync_or_async
        ... def sync_handler(x):
        ...     return x * 2
        >>>
        >>> result = await sync_handler(5)  # 10
        >>>
        >>> # 방법 2: 직접 호출
        >>> def my_func(x):
        ...     return x + 1
        >>>
        >>> result = await run_sync_or_async(my_func)(5)  # 6
        >>>
        >>> # 방법 3: 메서드 호출
        >>> result = await run_sync_or_async(obj.method)(arg1, arg2)
    """
    if is_async_callable(func):
        # async 함수는 그대로 반환
        return func  # type:ignore
    else:
        # sync 함수는 async로 변환
        # thread_sensitive=False로 설정하여 별도 스레드에서 실행
        return sync_to_async(func, thread_sensitive=False)  # type:ignore


def force_sync(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    sync 또는 async 함수를 강제로 동기 방식으로 실행

    async 함수인 경우 async_to_sync로 변환하여 실행
    sync 함수인 경우 직접 실행

    Args:
        func: 실행할 함수 (sync 또는 async)
        *args: 함수 인자
        **kwargs: 함수 키워드 인자

    Returns:
        함수 실행 결과

    Examples:
        >>> async def async_handler():
        ...     return "async result"
        >>>
        >>> # async 함수를 sync 방식으로 실행
        >>> result = force_sync(async_handler)
    """
    if is_async_callable(func):
        # async 함수는 sync로 변환하여 실행
        sync_func = async_to_sync(func, force_new_loop=False)
        return sync_func(*args, **kwargs)
    else:
        # sync 함수는 직접 실행
        return func(*args, **kwargs)
