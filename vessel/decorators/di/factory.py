"""
@Factory 데코레이터
"""

from typing import Callable, TypeVar
from vessel.di.core.container import Container, ContainerType, register_container
import inspect
from typing import get_type_hints

T = TypeVar("T")


class FactoryContainer(Container):
    """Factory 컨테이너"""

    def __init__(self, target: Callable, parent_class: type):
        super().__init__(target)
        self.container_type = ContainerType.FACTORY
        self.parent_class = parent_class
        self.instance = None
        self.return_type = None

        # 팩토리 메서드의 반환 타입 추출
        try:
            hints = get_type_hints(target)
            self.return_type = hints.get("return")
        except:
            pass

    def initialize(self, dependencies: dict = None, parent_instance=None) -> any:
        """
        팩토리 메서드 실행하여 인스턴스 생성
        """
        if self.instance is not None:
            return self.instance

        if dependencies is None:
            dependencies = {}

        # 팩토리 메서드의 파라미터 분석
        sig = inspect.signature(self.target)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # 파라미터 타입에 맞는 의존성 주입
            param_type = param.annotation
            if param_type != inspect.Parameter.empty and param_type in dependencies:
                kwargs[param_name] = dependencies[param_type]

        # 팩토리 메서드 호출 (바운드 메서드로 호출)
        if parent_instance is not None:
            # parent_instance에서 메서드를 가져와서 호출 (바운드 메서드)
            method = getattr(parent_instance, self.target.__name__)
            self.instance = method(**kwargs)
        else:
            self.instance = self.target(**kwargs)

        return self.instance


def Factory(method: Callable[..., T]) -> Callable[..., T]:
    """
    팩토리 메서드를 표시하는 데코레이터

    사용 예:
    @Component
    class Config:
        @Factory
        def create_service(dependency: SomeDependency) -> MyService:
            return MyService(dependency)
    """
    # 메서드에 팩토리 마커 추가
    method.__pydi_factory__ = True

    return method
