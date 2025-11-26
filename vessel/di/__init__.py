"""
Vessel DI Module - Dependency Injection Core

이 모듈은 프레임워크의 DI 기능을 담당합니다.
"""

from vessel.di.container import (
    Container,
    ContainerType,
    ContainerHolder,
    get_container_holder,
    get_all_registered_targets,
    register_container,
)
from vessel.di.container_manager import ContainerManager
from vessel.di.dependency import DependencyGraph, extract_dependencies

# NOTE: 내부 구현 모듈들(PackageScanner, ContainerCollector, etc.)은
# 명시적으로 import 해서 사용: from vessel.di.package_scanner import PackageScanner

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
