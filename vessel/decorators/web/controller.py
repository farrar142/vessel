"""
@Controller 및 @RequestMapping 데코레이터
"""

from typing import Type, TypeVar, Optional, Any, Callable
from vessel.di.container import Container, ContainerType, register_container

T = TypeVar("T")


class ControllerContainer(Container):
    """Controller 컨테이너"""

    def __init__(self, target: Type):
        super().__init__(target)
        self.container_type = ContainerType.CONTROLLER
        self.instance = None
        self.base_path = ""

    def initialize(self, dependencies: dict = None) -> any:
        """
        컨트롤러 초기화
        타입 기반 속성 의존성 주입
        """
        if self.instance is not None:
            return self.instance

        if dependencies is None:
            dependencies = {}

        # 타입 힌트 기반 의존성 주입
        from typing import get_type_hints

        try:
            hints = get_type_hints(self.target)
        except:
            hints = {}

        # 인스턴스 생성 (기본 생성자)
        self.instance = self.target()

        # 속성에 의존성 주입
        for attr_name, attr_type in hints.items():
            if attr_type in dependencies:
                setattr(self.instance, attr_name, dependencies[attr_type])

        return self.instance

    def get_instance(self) -> Any:
        """인스턴스 반환"""
        return self.instance


class RequestMappingContainer(Container):
    """RequestMapping 컨테이너"""

    def __init__(self, target: Type, path: str):
        super().__init__(target)
        self.container_type = ContainerType.HANDLER
        self.path = path
        self.set_metadata("path", path)

    def initialize(self, *args, **kwargs):
        """RequestMapping은 메타데이터만 제공"""
        return self.target


def Controller(path: str = "") -> Callable[[Type[T]], Type[T]]:
    """
    클래스를 컨트롤러로 등록하는 데코레이터
    선택적으로 base path를 지정할 수 있음

    사용 예:
    @Controller
    class MyController:
        service: MyService

    @Controller("/api")
    class ApiController:
        pass
    """

    def decorator(cls: Type[T]) -> Type[T]:
        container = ControllerContainer(cls)
        register_container(cls, container)

        cls.__pydi_container__ = container
        cls.__pydi_controller__ = True

        # base path 저장
        if path:
            cls.__pydi_base_path__ = path
            container.set_metadata("base_path", path)

        return cls

    # @Controller 형태로 사용된 경우 (path가 클래스인 경우)
    if isinstance(path, type):
        cls = path
        path_str = ""
        container = ControllerContainer(cls)
        register_container(cls, container)
        cls.__pydi_container__ = container
        cls.__pydi_controller__ = True
        return cls

    # @Controller() 또는 @Controller("/path") 형태
    return decorator


def RequestMapping(path: str):
    """
    컨트롤러의 기본 경로를 설정하는 데코레이터

    사용 예:
    @Controller
    @RequestMapping("/api/users")
    class UserController:
        pass
    """

    def decorator(cls: Type[T]) -> Type[T]:
        container = RequestMappingContainer(cls, path)
        register_container(cls, container)

        # 기존 컨트롤러 컨테이너가 있다면 base_path 설정
        if hasattr(cls, "__pydi_container__") and isinstance(
            cls.__pydi_container__, ControllerContainer
        ):
            cls.__pydi_container__.base_path = path

        cls.__pydi_request_mapping__ = path

        return cls

    return decorator
