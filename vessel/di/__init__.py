"""
Vessel DI Module - Dependency Injection Core

이 모듈은 프레임워크의 DI 기능을 담당합니다.

구조:
- core/: 핵심 DI 컴포넌트 (Container, ContainerManager, DependencyGraph)
- utils/: DI 유틸리티 (Scanner, Collector, Initializer, Analyzer, Resolver)
"""

# Core components (공개 API)
from vessel.di.core import (
    Container,
    ContainerType,
    ContainerHolder,
    get_container_holder,
    get_all_registered_targets,
    register_container,
    ContainerManager,
    DependencyGraph,
    extract_dependencies,
)

# Utils (필요시 명시적 import)
# from vessel.di.utils import PackageScanner, ContainerCollector, ...

__all__ = [
    # Container
    "Container",
    "ContainerType",
    "ContainerHolder",
    "get_container_holder",
    "get_all_registered_targets",
    "register_container",
    # Main
    "ContainerManager",
    # Dependency
    "DependencyGraph",
    "extract_dependencies",
]
