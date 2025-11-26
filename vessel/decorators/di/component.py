"""
@Component 데코레이터
"""

from typing import Type, TypeVar, Any
from vessel.di.container import Container, ContainerType, register_container

T = TypeVar("T")


class ComponentContainer(Container):
    """Component 컨테이너"""

    def __init__(self, target: Type):
        super().__init__(target)
        self.container_type = ContainerType.COMPONENT
        self.instance = None

    def initialize(self, dependencies: dict = None) -> any:
        """
        컴포넌트 초기화
        타입 기반 속성 의존성 주입
        """
        if self.instance is not None:
            return self.instance

        if dependencies is None:
            dependencies = {}

        # 클래스 속성의 타입 힌트를 기반으로 의존성 주입
        import inspect
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


def Component(cls: Type[T]) -> Type[T]:
    """
    클래스를 컴포넌트로 등록하는 데코레이터

    사용 예:
    @Component
    class MyService:
        dependency: SomeDependency
    """
    container = ComponentContainer(cls)
    register_container(cls, container)

    # 원본 클래스에 컨테이너 정보 저장
    cls.__pydi_container__ = container

    return cls
