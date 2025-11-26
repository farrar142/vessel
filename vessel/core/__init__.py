"""
Core module exports
"""

from vessel.core.container import (
    Container,
    ContainerType,
    ContainerHolder,
    get_container_holder,
    get_all_registered_targets,
    register_container,
)
from vessel.core.container_manager import ContainerManager
from vessel.core.dependency import DependencyGraph, extract_dependencies

# NOTE: 리팩토링된 모듈들(PackageScanner, ContainerCollector, etc.)은
# 내부 구현이므로 __init__.py에서 export하지 않습니다.
# 필요시 직접 import: from vessel.core.package_scanner import PackageScanner

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
