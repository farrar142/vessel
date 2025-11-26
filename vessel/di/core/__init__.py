"""
Vessel DI Core - 핵심 DI 컴포넌트

Container, DependencyGraph, ContainerManager 등 DI의 핵심 기능
"""

from vessel.di.core.container import (
    Container,
    ContainerType,
    ContainerHolder,
    get_container_holder,
    get_all_registered_targets,
    register_container,
)
from vessel.di.core.container_manager import ContainerManager
from vessel.di.core.dependency import DependencyGraph, extract_dependencies

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
