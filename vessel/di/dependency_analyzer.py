"""
DependencyAnalyzer - 의존성 분석 책임
"""

from typing import Any, Dict, List, Set, Type
from vessel.di.dependency import DependencyGraph, extract_dependencies


class DependencyAnalyzer:
    """컨테이너들 간의 의존성을 분석하는 클래스"""

    @staticmethod
    def analyze_dependencies(
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factories: Dict[Type, List[Any]],
        dependency_graph: DependencyGraph,
    ) -> None:
        """
        컴포넌트, 컨트롤러, 팩토리의 의존성을 분석하여 그래프에 추가

        Args:
            components: 컴포넌트 딕셔너리
            controllers: 컨트롤러 딕셔너리
            factories: 팩토리 딕셔너리
            dependency_graph: 의존성 그래프 (수정됨)
        """
        # 팩토리가 생성할 타입들 수집
        factory_types = DependencyAnalyzer._collect_factory_types(factories)

        # 컴포넌트의 의존성 분석
        DependencyAnalyzer._analyze_component_dependencies(
            components, controllers, factory_types, dependency_graph
        )

        # 컨트롤러의 의존성 분석
        DependencyAnalyzer._analyze_controller_dependencies(
            components, controllers, factory_types, dependency_graph
        )

        # 팩토리의 의존성 분석
        DependencyAnalyzer._analyze_factory_dependencies(
            components, controllers, factories, factory_types, dependency_graph
        )

    @staticmethod
    def _collect_factory_types(factories: Dict[Type, List[Any]]) -> Set[Type]:
        """팩토리가 생성할 타입들을 수집"""
        factory_types = set()
        for parent_class, factory_list in factories.items():
            for factory_container in factory_list:
                if factory_container.return_type:
                    factory_types.add(factory_container.return_type)
        return factory_types

    @staticmethod
    def _analyze_component_dependencies(
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factory_types: Set[Type],
        dependency_graph: DependencyGraph,
    ) -> None:
        """컴포넌트의 의존성 분석"""
        for component_type, container in components.items():
            deps = extract_dependencies(component_type)
            for dep in deps:
                if dep in components or dep in controllers or dep in factory_types:
                    dependency_graph.add_dependency(component_type, dep)

    @staticmethod
    def _analyze_controller_dependencies(
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factory_types: Set[Type],
        dependency_graph: DependencyGraph,
    ) -> None:
        """컨트롤러의 의존성 분석"""
        for controller_type, container in controllers.items():
            deps = extract_dependencies(controller_type)
            for dep in deps:
                if dep in components or dep in controllers or dep in factory_types:
                    dependency_graph.add_dependency(controller_type, dep)

    @staticmethod
    def _analyze_factory_dependencies(
        components: Dict[Type, Any],
        controllers: Dict[Type, Any],
        factories: Dict[Type, List[Any]],
        factory_types: Set[Type],
        dependency_graph: DependencyGraph,
    ) -> None:
        """팩토리의 의존성 분석"""
        for parent_class, factory_list in factories.items():
            for factory_container in factory_list:
                deps = extract_dependencies(factory_container.target)
                for dep in deps:
                    # 팩토리가 생성하는 타입을 의존성 그래프에 추가
                    if factory_container.return_type:
                        if (
                            dep in components
                            or dep in controllers
                            or dep in factory_types
                        ):
                            dependency_graph.add_dependency(
                                factory_container.return_type, dep
                            )
