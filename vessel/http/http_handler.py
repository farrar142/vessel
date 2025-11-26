"""
HTTP 메서드 매핑 핸들러 (@Get, @Post, @Put, @Delete)
HandlerContainer를 상속받아 HTTP 특화 기능 제공
"""

from typing import Callable, TypeVar, overload, Union
from vessel.decorators.handler import HandlerContainer
from vessel.core.container import register_container

T = TypeVar("T")


class HttpMethodMappingHandler(HandlerContainer):
    """HTTP 메서드 매핑 핸들러 컨테이너"""

    def __init__(self, target: Callable, method: str, path: str = ""):
        super().__init__(target)
        self.http_method = method
        self.path = path
        self.set_metadata("http_method", method)
        self.set_metadata("path", path)


def _create_http_handler_decorator(http_method: str):
    """HTTP 메서드 데코레이터 생성 팩토리"""

    @overload
    def decorator(func: Callable[..., T], /) -> Callable[..., T]:
        """데코레이터를 인자 없이 사용: @Get"""
        ...

    @overload
    def decorator(path: str = "", /) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """데코레이터를 경로와 함께 사용: @Get("/path")"""
        ...

    def decorator(
        path_or_func: Union[Callable[..., T], str, None] = None, /
    ) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
        """
        경로를 받는 데코레이터 또는 직접 함수를 받는 데코레이터

        사용법:
        - @Get          # 인자 없이 사용
        - @Get()        # 빈 괄호로 사용
        - @Get("/path") # 경로와 함께 사용
        """

        def wrapper(func: Callable[..., T]) -> Callable[..., T]:
            """
            실제 함수를 감싸는 래퍼
            """
            # path 결정
            actual_path = "" if callable(path_or_func) else (path_or_func or "")

            # 기존 HandlerContainer가 있으면 HTTP 핸들러로 업그레이드
            if hasattr(func, "__pydi_container__") and isinstance(
                func.__pydi_container__, HandlerContainer
            ):
                # 기존 컨테이너의 인터셉터를 유지하면서 HTTP 컨테이너로 변환
                old_container = func.__pydi_container__
                container = HttpMethodMappingHandler(func, http_method, actual_path)
                container.interceptors = old_container.interceptors
            else:
                container = HttpMethodMappingHandler(func, http_method, actual_path)
                register_container(func, container)

            # 함수에 핸들러 정보 저장
            func.__pydi_handler__ = True
            func.__pydi_http_method__ = http_method
            func.__pydi_path__ = actual_path
            func.__pydi_container__ = container

            return func

        # path_or_func이 함수인 경우 (데코레이터를 인자 없이 사용: @Get)
        if callable(path_or_func):
            return wrapper(path_or_func)

        # path_or_func이 문자열이거나 None인 경우 (데코레이터를 인자와 함께 사용: @Get("/path"))
        return wrapper

    return decorator


# HTTP 메서드 데코레이터 생성
Get = _create_http_handler_decorator("GET")
Post = _create_http_handler_decorator("POST")
Put = _create_http_handler_decorator("PUT")
Delete = _create_http_handler_decorator("DELETE")
Patch = _create_http_handler_decorator("PATCH")
