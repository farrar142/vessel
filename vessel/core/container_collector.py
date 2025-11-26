"""
ContainerCollector - 컨테이너 수집 책임
"""

from typing import Any, Dict, List, Type
from vessel.core.container import (
    get_all_registered_targets,
    get_container_holder,
    register_container,
)


class ContainerCollector:
    """등록된 컨테이너들을 수집하는 클래스"""

    @staticmethod
    def collect_containers() -> (
        tuple[Dict[Type, Any], Dict[Type, Any], Dict[Type, List[Any]]]
    ):
        """
        전역 레지스트리에서 모든 컨테이너를 수집

        Returns:
            (components, controllers, factories) 튜플
        """
        # 런타임에 import하여 순환 import 방지
        from vessel.decorators.component import ComponentContainer
        from vessel.decorators.factory import FactoryContainer
        from vessel.decorators.controller import ControllerContainer
        from vessel.decorators.configuration import ConfigurationContainer

        components: Dict[Type, Any] = {}
        controllers: Dict[Type, Any] = {}
        factories: Dict[Type, List[Any]] = {}

        targets = get_all_registered_targets()

        for target in targets:
            holder = get_container_holder(target)
            if holder is None:
                continue

            for container in holder.get_containers():
                if isinstance(container, ComponentContainer):
                    components[target] = container
                elif isinstance(container, ControllerContainer):
                    controllers[target] = container
                elif isinstance(container, ConfigurationContainer):
                    # Configuration도 Component처럼 취급
                    components[target] = container
                elif isinstance(container, FactoryContainer):
                    if container.parent_class not in factories:
                        factories[container.parent_class] = []
                    factories[container.parent_class].append(container)

        # 팩토리 메서드도 수집
        ContainerCollector._collect_factory_methods(components, factories)

        return components, controllers, factories

    @staticmethod
    def _collect_factory_methods(
        components: Dict[Type, Any],
        factories: Dict[Type, List[Any]],
    ) -> None:
        """
        컴포넌트 클래스들에서 @Factory 메서드 찾기

        Args:
            components: 컴포넌트 딕셔너리
            factories: 팩토리 딕셔너리 (수정됨)
        """
        # 런타임에 import하여 순환 import 방지
        from vessel.decorators.factory import FactoryContainer

        for component_class in components.keys():
            for attr_name in dir(component_class):
                try:
                    attr = getattr(component_class, attr_name)
                    if callable(attr) and hasattr(attr, "__pydi_factory__"):
                        # Factory 컨테이너 생성 및 등록
                        factory_container = FactoryContainer(attr, component_class)

                        if component_class not in factories:
                            factories[component_class] = []
                        factories[component_class].append(factory_container)

                        # 레지스트리에도 등록
                        register_container(attr, factory_container)
                except:
                    pass
