"""
Unit Tests for Component decorator
"""

import pytest
from vessel.decorators.component import Component, ComponentContainer


class TestComponent:
    """Component 데코레이터 테스트"""

    def test_component_decorator(self):
        """@Component 데코레이터가 제대로 적용되는지 테스트"""

        @Component
        class TestService:
            pass

        assert hasattr(TestService, "__pydi_container__")
        assert isinstance(TestService.__pydi_container__, ComponentContainer)

    def test_component_initialization(self):
        """컴포넌트 초기화 테스트"""

        @Component
        class SimpleService:
            pass

        container = SimpleService.__pydi_container__
        instance = container.initialize()

        assert instance is not None
        assert isinstance(instance, SimpleService)
        assert container.instance == instance

    def test_component_with_dependencies(self):
        """의존성이 있는 컴포넌트 테스트"""

        @Component
        class ServiceA:
            pass

        @Component
        class ServiceB:
            service_a: ServiceA

        # ServiceA 먼저 초기화
        container_a = ServiceA.__pydi_container__
        instance_a = container_a.initialize()

        # ServiceB 초기화 (의존성 주입)
        container_b = ServiceB.__pydi_container__
        dependencies = {ServiceA: instance_a}
        instance_b = container_b.initialize(dependencies)

        assert instance_b.service_a == instance_a

    def test_component_singleton(self):
        """컴포넌트가 싱글톤으로 동작하는지 테스트"""

        @Component
        class SingletonService:
            pass

        container = SingletonService.__pydi_container__
        instance1 = container.initialize()
        instance2 = container.initialize()

        assert instance1 is instance2

    def test_component_without_type_hints(self):
        """타입 힌트가 없는 컴포넌트 테스트"""

        @Component
        class NoHintService:
            def __init__(self):
                self.value = 42

        container = NoHintService.__pydi_container__
        instance = container.initialize()

        assert instance.value == 42
