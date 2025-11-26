"""
ComponentInitializer - 컴포넌트 초기화 책임
"""

from typing import Any, Dict, List, Type


class ComponentInitializer:
    """컴포넌트들을 초기화하는 클래스"""

    @staticmethod
    def initialize_components(
        sorted_types: List[Type],
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factories: Dict[Type, List[Any]],
        instances: Dict[Type, Any],
    ) -> None:
        """
        정렬된 순서대로 컴포넌트를 초기화

        Args:
            sorted_types: Topological Sort된 타입 리스트
            components: 컴포넌트 딕셔너리
            controllers: 컨트롤러 딕셔너리
            factories: 팩토리 딕셔너리
            instances: 인스턴스 딕셔너리 (수정됨)
        """
        # 1. 팩토리의 부모 컴포넌트들을 먼저 초기화
        ComponentInitializer._initialize_factory_parents(
            factories, components, instances
        )

        # 2. 팩토리 타입 매핑 생성
        factory_types = ComponentInitializer._build_factory_type_mapping(factories)

        # 3. Sorted types에 있는 컴포넌트/컨트롤러 초기화
        ComponentInitializer._initialize_sorted_types(
            sorted_types, components, controllers, factory_types, instances
        )

        # 4. 의존성 없는 컴포넌트/컨트롤러 초기화
        ComponentInitializer._initialize_remaining_components(
            components, controllers, instances
        )

    @staticmethod
    def _initialize_factory_parents(
        factories: Dict[Type, List[Any]],
        components: Dict[Type, Any],
        instances: Dict[Type, Any],
    ) -> None:
        """팩토리의 부모 컴포넌트들을 먼저 초기화"""
        for parent_class in factories.keys():
            if parent_class not in instances and parent_class in components:
                container = components[parent_class]
                instance = container.initialize(instances)
                instances[parent_class] = instance

    @staticmethod
    def _build_factory_type_mapping(
        factories: Dict[Type, List[Any]],
    ) -> Dict[Type, tuple[Type, Any]]:
        """팩토리가 생성하는 타입 매핑 생성"""
        factory_types = {}
        for parent_class, factory_list in factories.items():
            for factory_container in factory_list:
                if factory_container.return_type:
                    factory_types[factory_container.return_type] = (
                        parent_class,
                        factory_container,
                    )
        return factory_types

    @staticmethod
    def _initialize_sorted_types(
        sorted_types: List[Type],
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factory_types: Dict[Type, tuple[Type, Any]],
        instances: Dict[Type, Any],
    ) -> None:
        """Sorted types에 있는 컴포넌트/컨트롤러 초기화"""
        for component_type in sorted_types:
            if component_type in instances:
                continue

            # 팩토리로 생성되는 타입인지 확인
            if component_type in factory_types:
                ComponentInitializer._initialize_factory_type(
                    component_type, factory_types, instances
                )
                continue

            # 컴포넌트 초기화
            if component_type in components:
                container = components[component_type]
                instance = container.initialize(instances)
                instances[component_type] = instance

            # 컨트롤러 초기화
            elif component_type in controllers:
                container = controllers[component_type]
                instance = container.initialize(instances)
                instances[component_type] = instance

    @staticmethod
    def _initialize_factory_type(
        component_type: Type,
        factory_types: Dict[Type, tuple[Type, Any]],
        instances: Dict[Type, Any],
    ) -> None:
        """팩토리를 통해 생성되는 타입 초기화"""
        parent_class, factory_container = factory_types[component_type]
        parent_instance = instances.get(parent_class)

        if parent_instance is not None:
            instance = factory_container.initialize(instances, parent_instance)
            instances[component_type] = instance

    @staticmethod
    def _initialize_remaining_components(
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        instances: Dict[Type, Any],
    ) -> None:
        """의존성이 없어 sorted_types에 포함되지 않은 컴포넌트/컨트롤러 초기화"""
        # 남은 컴포넌트 초기화
        for component_type, container in components.items():
            if component_type not in instances:
                instance = container.initialize(instances)
                instances[component_type] = instance

        # 남은 컨트롤러 초기화
        for controller_type, container in controllers.items():
            if controller_type not in instances:
                instance = container.initialize(instances)
                instances[controller_type] = instance
