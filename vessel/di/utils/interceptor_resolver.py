"""
InterceptorResolver - 인터셉터 의존성 해결 책임
"""

from typing import Any, Dict, Set, Type
from typing import get_type_hints
from vessel.di.core.container import get_all_registered_targets, get_container_holder


class InterceptorResolver:
    """인터셉터의 의존성을 해결하는 클래스"""

    @staticmethod
    def collect_and_initialize_interceptor_dependencies(
        components: Dict[Type, Any],
        instances: Dict[Type, Any],
    ) -> None:
        """
        인터셉터의 의존성을 수집하고 초기화

        Args:
            components: 컴포넌트 딕셔너리
            instances: 인스턴스 딕셔너리 (수정됨)
        """
        # 인터셉터가 필요로 하는 의존성 타입 수집
        interceptor_dep_types = (
            InterceptorResolver._collect_interceptor_dependency_types(components)
        )

        # 인터셉터 의존성 초기화
        InterceptorResolver._initialize_interceptor_dependencies(
            interceptor_dep_types, components, instances
        )

    @staticmethod
    def _collect_interceptor_dependency_types(components: Dict[Type, Any]) -> Set[Type]:
        """인터셉터가 필요로 하는 의존성 타입들을 수집"""
        # 런타임에 import하여 순환 import 방지
        from vessel.decorators.handler.handler import HandlerContainer

        interceptor_dep_types = set()
        targets = get_all_registered_targets()

        for target in targets:
            holder = get_container_holder(target)
            if holder is None:
                continue

            for container in holder.get_containers():
                if isinstance(container, HandlerContainer):
                    # 인터셉터 클래스의 타입 힌트 확인
                    for interceptor_class in container.interceptor_classes:
                        try:
                            hints = get_type_hints(interceptor_class)
                            for attr_type in hints.values():
                                if attr_type in components:
                                    interceptor_dep_types.add(attr_type)
                        except:
                            pass

        return interceptor_dep_types

    @staticmethod
    def _initialize_interceptor_dependencies(
        interceptor_dep_types: Set[Type],
        components: Dict[Type, Any],
        instances: Dict[Type, Any],
    ) -> None:
        """인터셉터 의존성 초기화"""
        for dep_type in interceptor_dep_types:
            if dep_type not in instances and dep_type in components:
                container = components[dep_type]
                instance = container.initialize(instances)
                instances[dep_type] = instance

    @staticmethod
    def resolve_handler_interceptors(container_manager) -> None:
        """
        핸들러 컨테이너의 인터셉터 의존성 해결

        Args:
            container_manager: ContainerManager 인스턴스
        """
        # 런타임에 import하여 순환 import 방지
        from vessel.decorators.handler.handler import HandlerContainer

        targets = get_all_registered_targets()

        for target in targets:
            holder = get_container_holder(target)
            if holder is None:
                continue

            for container in holder.get_containers():
                if isinstance(container, HandlerContainer):
                    # 인터셉터 클래스를 인스턴스로 해결
                    if container.interceptor_classes:
                        container.resolve_interceptors(container_manager)
