"""
pytest configuration
"""

import sys
from pathlib import Path
import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def cleanup_registry():
    """각 테스트 전후로 전역 컨테이너 레지스트리를 초기화합니다."""
    import vessel.di.core.container as container_module

    # 테스트 실행 전 초기화
    container_module._container_registry.clear()

    yield

    # 테스트 실행 후 초기화
    container_module._container_registry.clear()


@pytest.fixture
def manager():
    """각 테스트마다 새로운 ContainerManager 인스턴스를 제공합니다."""
    from vessel.di.core.container_manager import ContainerManager

    return ContainerManager()
