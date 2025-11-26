"""
범용 핸들러 데코레이터 및 인터셉터
HTTP, WebSocket 등 다양한 프로토콜에서 사용 가능
"""

from typing import Callable, TypeVar, Any, List, Optional
from vessel.di.core.container import Container, ContainerType, register_container
import functools

T = TypeVar("T")


class HandlerInterceptor:
    """핸들러 인터셉터 인터페이스"""

    def before(self, *args, **kwargs) -> tuple:
        """
        핸들러 실행 전 호출
        args, kwargs를 수정하여 반환 가능
        """
        return args, kwargs

    def after(self, result: Any, *args, **kwargs) -> Any:
        """
        핸들러 실행 후 호출
        결과를 수정하여 반환 가능
        """
        return result

    def on_error(self, error: Exception, *args, **kwargs):
        """
        에러 발생 시 호출
        에러를 처리하거나 재발생시킬 수 있음
        """
        raise error


class HandlerContainer(Container):
    """범용 핸들러 컨테이너 - 인터셉터 지원"""

    def __init__(self, target: Callable):
        super().__init__(target)
        self.container_type = ContainerType.HANDLER
        self.interceptors: List[HandlerInterceptor] = []
        self.interceptor_classes: List[type[HandlerInterceptor]] = []

    def add_interceptor(self, interceptor: HandlerInterceptor):
        """인터셉터 인스턴스 추가"""
        self.interceptors.append(interceptor)

    def add_interceptor_class(self, interceptor_class: type[HandlerInterceptor]):
        """인터셉터 클래스 추가 (지연 생성용)"""
        self.interceptor_classes.append(interceptor_class)

    def resolve_interceptors(self, container_manager):
        """인터셉터 클래스를 인스턴스로 해결 (타입 기반 의존성 주입)"""
        from typing import get_type_hints

        for interceptor_class in self.interceptor_classes:
            # 인터셉터 인스턴스 생성 (기본 생성자)
            interceptor_instance = interceptor_class()

            # 타입 힌트를 통한 의존성 주입
            try:
                hints = get_type_hints(interceptor_class)
            except:
                hints = {}

            # 속성에 의존성 주입
            for attr_name, attr_type in hints.items():
                dep_container = container_manager.get_container(attr_type)
                if dep_container:
                    dep_instance = dep_container.get_instance()
                    setattr(interceptor_instance, attr_name, dep_instance)

            self.interceptors.append(interceptor_instance)

        # 해결된 클래스 제거
        self.interceptor_classes.clear()

    def wrap_handler(self, handler: Callable) -> Callable:
        """
        핸들러를 인터셉터로 감싸기
        """

        @functools.wraps(handler)
        def wrapped(*args, **kwargs):
            # Before 인터셉터 실행
            for interceptor in self.interceptors:
                args, kwargs = interceptor.before(*args, **kwargs)

            try:
                # 실제 핸들러 실행
                result = handler(*args, **kwargs)

                # After 인터셉터 실행
                for interceptor in reversed(self.interceptors):
                    result = interceptor.after(result, *args, **kwargs)

                return result

            except Exception as e:
                # 에러 인터셉터 실행
                for interceptor in reversed(self.interceptors):
                    interceptor.on_error(e, *args, **kwargs)
                raise

        return wrapped

    def initialize(self, *args, **kwargs):
        """핸들러는 메타데이터만 제공"""
        return self.target


# 범용 인터셉터 예시


class TransactionInterceptor(HandlerInterceptor):
    """트랜잭션 인터셉터 예시"""

    def before(self, *args, **kwargs) -> tuple:
        print("  [Transaction] BEGIN - 트랜잭션 시작")
        return args, kwargs

    def after(self, result: Any, *args, **kwargs) -> Any:
        print("  [Transaction] COMMIT - 트랜잭션 커밋")
        return result

    def on_error(self, error: Exception, *args, **kwargs):
        print(f"  [Transaction] ROLLBACK - 에러 발생: {error}")
        raise error


class LoggingInterceptor(HandlerInterceptor):
    """로깅 인터셉터 예시"""

    def before(self, *args, **kwargs) -> tuple:
        print(f"  [Logging] 요청 시작 - args: {args}, kwargs: {kwargs}")
        return args, kwargs

    def after(self, result: Any, *args, **kwargs) -> Any:
        print(f"  [Logging] 요청 완료 - result: {result}")
        return result

    def on_error(self, error: Exception, *args, **kwargs):
        print(f"  [Logging] 에러 발생 - {type(error).__name__}: {error}")
        raise error


# 데코레이터 팩토리


def create_handler_decorator(
    *interceptor_classes: type[HandlerInterceptor],
    container_class: type[HandlerContainer] = HandlerContainer,
    metadata_key: Optional[str] = None,
    inject_dependencies: bool = True,
):
    """
    핸들러 데코레이터 팩토리 (개선 버전)

    Args:
        *interceptor_classes: 적용할 인터셉터 클래스들 (여러 개 가능)
        container_class: 사용할 컨테이너 클래스 (기본: HandlerContainer)
        metadata_key: 메타데이터 키 (예: __pydi_transaction__)
        inject_dependencies: 인터셉터에 의존성 주입 사용 여부 (기본: True)

    Returns:
        데코레이터 함수

    Examples:
        # 단일 인터셉터
        Timer = create_handler_decorator(TimerInterceptor)

        # 여러 인터셉터를 하나의 데코레이터로
        Monitored = create_handler_decorator(
            LoggingInterceptor,
            TimerInterceptor,
            metadata_key="__pydi_monitored__"
        )

        # 의존성 주입 받는 인터셉터
        class DbInterceptor(HandlerInterceptor):
            def __init__(self, db_service: DatabaseService):
                self.db = db_service

        DbTransaction = create_handler_decorator(
            DbInterceptor,
            inject_dependencies=True
        )
    """
    from vessel.di.core.container_manager import ContainerManager

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # 핸들러 컨테이너가 없으면 생성
        if not hasattr(func, "__pydi_container__"):
            container = container_class(func)
            func.__pydi_container__ = container
            register_container(func, container)
        # 다른 컨테이너가 있으면 업그레이드
        elif not isinstance(func.__pydi_container__, container_class):
            old_container = func.__pydi_container__
            # 기존 인터셉터 복사
            if isinstance(old_container, HandlerContainer):
                container = container_class(func)
                container.interceptors = old_container.interceptors.copy()
                func.__pydi_container__ = container
                register_container(func, container)

        # 여러 인터셉터 추가
        if isinstance(func.__pydi_container__, HandlerContainer):
            for interceptor_class in interceptor_classes:
                if inject_dependencies:
                    # 인터셉터를 지연 생성 (초기화 시점에 의존성 해결)
                    func.__pydi_container__.add_interceptor_class(interceptor_class)
                else:
                    # 의존성 주입 없이 직접 생성
                    func.__pydi_container__.add_interceptor(interceptor_class())

        # 메타데이터 추가
        if metadata_key:
            setattr(func, metadata_key, True)

        return func

    return decorator


# 범용 데코레이터 (팩토리로 생성)

Transaction = create_handler_decorator(
    TransactionInterceptor, metadata_key="__pydi_transaction__"
)

Logging = create_handler_decorator(LoggingInterceptor, metadata_key="__pydi_logging__")
