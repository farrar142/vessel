"""
Unit Tests for Container classes
"""

import pytest
from vessel.core.container import Container, ContainerType


class MockContainer(Container):
    """Mock container for testing"""

    def initialize(self, *args, **kwargs):
        return "initialized"


class TestContainer:
    """Container 기본 클래스 테스트"""

    def test_container_creation(self):
        """컨테이너 생성 테스트"""

        def dummy_target():
            pass

        container = MockContainer(dummy_target)
        assert container.target == dummy_target
        assert container.container_type == ContainerType.COMPONENT

    def test_metadata_operations(self):
        """메타데이터 설정 및 조회 테스트"""

        def dummy_target():
            pass

        container = MockContainer(dummy_target)
        container.set_metadata("key1", "value1")
        container.set_metadata("key2", 123)

        assert container.get_metadata("key1") == "value1"
        assert container.get_metadata("key2") == 123
        assert container.get_metadata("key3", "default") == "default"

    def test_nested_containers(self):
        """중첩 컨테이너 테스트"""

        def dummy_target():
            pass

        container1 = MockContainer(dummy_target)
        container2 = MockContainer(dummy_target)
        container3 = MockContainer(dummy_target)

        container1.add_nested_container(container2)
        container1.add_nested_container(container3)

        nested = container1.get_nested_containers()
        assert len(nested) == 2
        assert container2 in nested
        assert container3 in nested

    def test_initialize(self):
        """초기화 메서드 테스트"""

        def dummy_target():
            pass

        container = MockContainer(dummy_target)
        result = container.initialize()
        assert result == "initialized"
