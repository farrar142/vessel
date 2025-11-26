"""
Configuration 데코레이터
Factory 메서드를 그룹핑하기 위한 데코레이터
"""

from typing import Type, TypeVar
from vessel.di.core.container import Container, ContainerType, register_container

T = TypeVar("T")


class ConfigurationContainer(Container):
    """Configuration 클래스를 위한 컨테이너"""

    def __init__(self, target: Type):
        super().__init__(target)
        self.container_type = ContainerType.COMPONENT
        self.is_configuration = True
        self.instance = None  # 인스턴스 저장

    def initialize(self, dependencies: dict = None) -> any:
        """Configuration 인스턴스 생성"""
        if self.instance is not None:
            return self.instance

        if dependencies is None:
            dependencies = {}

        # 타입 힌트 기반 의존성 주입 (ComponentContainer와 동일)
        from typing import get_type_hints

        try:
            hints = get_type_hints(self.target)
        except:
            hints = {}

        # 인스턴스 생성
        self.instance = self.target()

        # 속성에 의존성 주입
        for attr_name, attr_type in hints.items():
            if attr_type in dependencies:
                setattr(self.instance, attr_name, dependencies[attr_type])

        return self.instance

    def get_instance(self):
        """인스턴스 반환"""
        return self.instance


def Configuration(cls: Type[T]) -> Type[T]:
    """
    Configuration 클래스 데코레이터

    Factory 메서드를 그룹핑하기 위한 클래스 마커
    Component와 유사하지만 주로 @Factory 메서드를 포함하는 설정 클래스용

    사용 예:
    @Configuration
    class AppConfig:
        @Factory
        def my_bean(self) -> MyBean:
            return MyBean()
    """
    container = ConfigurationContainer(cls)
    register_container(cls, container)

    cls.__pydi_container__ = container
    cls.__pydi_configuration__ = True

    return cls


__all__ = ["Configuration", "ConfigurationContainer"]
