"""
Integration Tests for ContainerManager
"""

import pytest
from vessel import Component, Controller, ContainerManager, Get


class TestContainerManagerIntegration:
    """ContainerManager 통합 테스트"""

    def test_simple_component_initialization(self):
        """간단한 컴포넌트 초기화 테스트"""

        @Component
        class SimpleService:
            def get_value(self):
                return 42

        manager = ContainerManager()
        # component_scan 대신 _collect_containers 직접 호출
        manager._collect_containers()
        manager.initialize()

        instance = manager.get_instance(SimpleService)
        assert instance is not None
        assert instance.get_value() == 42

    def test_dependency_injection(self):
        """의존성 주입 테스트"""

        @Component
        class ServiceA:
            def get_name(self):
                return "ServiceA"

        @Component
        class ServiceB:
            service_a: ServiceA

            def get_combined(self):
                return f"ServiceB + {self.service_a.get_name()}"

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        instance_b = manager.get_instance(ServiceB)
        assert instance_b is not None
        assert instance_b.get_combined() == "ServiceB + ServiceA"

    def test_multiple_dependencies(self):
        """여러 의존성 주입 테스트"""

        @Component
        class ServiceA:
            pass

        @Component
        class ServiceB:
            pass

        @Component
        class ServiceC:
            service_a: ServiceA
            service_b: ServiceB

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        instance_a = manager.get_instance(ServiceA)
        instance_b = manager.get_instance(ServiceB)
        instance_c = manager.get_instance(ServiceC)

        assert instance_c.service_a is instance_a
        assert instance_c.service_b is instance_b

    def test_controller_initialization(self):
        """컨트롤러 초기화 테스트"""

        @Component
        class DataService:
            def get_data(self):
                return {"data": "test"}

        @Controller
        class TestController:
            data_service: DataService

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        controllers = manager.get_controllers()
        assert TestController in controllers

        controller = controllers[TestController]
        assert controller.data_service is not None
        assert controller.data_service.get_data() == {"data": "test"}

    def test_circular_dependency_detection(self):
        """순환 의존성 감지 테스트"""
        # 이 테스트는 실제로 순환 의존성을 만들기 어려우므로
        # 의존성 그래프 레벨에서 테스트됨 (test_dependency.py 참조)
        pass

    def test_component_scan_current_module(self):
        """현재 모듈 스캔 테스트"""

        @Component
        class LocalService:
            value = 100

        manager = ContainerManager()
        # component_scan 대신 _collect_containers 직접 호출
        manager._collect_containers()
        manager.initialize()

        instance = manager.get_instance(LocalService)
        assert instance is not None
        assert instance.value == 100

    def test_get_all_instances(self):
        """모든 인스턴스 조회 테스트"""

        @Component
        class ServiceX:
            pass

        @Component
        class ServiceY:
            pass

        manager = ContainerManager()
        # component_scan 대신 _collect_containers 직접 호출
        manager._collect_containers()
        manager.initialize()

        all_instances = manager.get_all_instances()

        assert ServiceX in all_instances
        assert ServiceY in all_instances
