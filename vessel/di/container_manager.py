"""
ContainerManager - 컨테이너들을 관리하고 초기화하는 핵심 클래스 (리팩토링됨)
"""

from typing import Any, Dict, List, Type, Optional, TYPE_CHECKING

from vessel.di.container import Container
from vessel.di.dependency import DependencyGraph

# 순환 import 방지를 위한 TYPE_CHECKING
if TYPE_CHECKING:
    from vessel.decorators.di.component import ComponentContainer
    from vessel.decorators.di.factory import FactoryContainer
    from vessel.decorators.web.controller import ControllerContainer

# 리팩토링된 책임 분리 클래스들
from vessel.di.package_scanner import PackageScanner
from vessel.di.container_collector import ContainerCollector
from vessel.di.dependency_analyzer import DependencyAnalyzer
from vessel.di.component_initializer import ComponentInitializer
from vessel.di.interceptor_resolver import InterceptorResolver


class ContainerManager:
    """
    컨테이너 관리자 (Orchestrator)

    책임:
    - 전체 초기화 프로세스 조율
    - 컨테이너 및 인스턴스 저장소 역할
    - 외부 API 제공

    실제 작업은 각 책임별 클래스에 위임:
    - PackageScanner: 패키지 스캐닝
    - ContainerCollector: 컨테이너 수집
    - DependencyAnalyzer: 의존성 분석
    - ComponentInitializer: 컴포넌트 초기화
    - InterceptorResolver: 인터셉터 의존성 해결
    """

    def __init__(self):
        self.components: Dict[Type, Any] = {}  # ComponentContainer
        self.controllers: Dict[Type, Any] = {}  # ControllerContainer
        self.factories: Dict[Type, List[Any]] = {}  # FactoryContainer
        self.instances: Dict[Type, Any] = {}
        self.dependency_graph = DependencyGraph()

    def component_scan(self, *packages: str) -> None:
        """
        지정된 패키지들을 스캔하여 컴포넌트 수집

        Args:
            *packages: 스캔할 패키지 이름들 또는 모듈 경로
        """
        # 1. 패키지 스캔 (PackageScanner에 위임)
        PackageScanner.scan_packages(*packages)

        # 2. 컨테이너 수집 (ContainerCollector에 위임)
        self._collect_containers()

    def _collect_containers(self) -> None:
        """등록된 컨테이너들을 수집 (ContainerCollector에 위임)"""
        self.components, self.controllers, self.factories = (
            ContainerCollector.collect_containers()
        )

    def initialize(self) -> None:
        """
        모든 컨테이너 초기화

        프로세스:
        1. 의존성 분석 (DependencyAnalyzer에 위임)
        2. Topological sort
        3. 순서대로 초기화 (ComponentInitializer에 위임)
        4. 인터셉터 의존성 해결 (InterceptorResolver에 위임)
        """
        # 1. 의존성 분석
        DependencyAnalyzer.analyze_dependencies(
            self.components,
            self.controllers,
            self.factories,
            self.dependency_graph,
        )

        # 2. Topological sort
        try:
            sorted_types = self.dependency_graph.topological_sort()
        except ValueError as e:
            raise ValueError(f"Failed to initialize containers: {e}")

        # 3. 컴포넌트 초기화
        ComponentInitializer.initialize_components(
            sorted_types,
            self.components,
            self.controllers,
            self.factories,
            self.instances,
        )

        # 4. 인터셉터 의존성 수집 및 초기화
        InterceptorResolver.collect_and_initialize_interceptor_dependencies(
            self.components,
            self.instances,
        )

        # 5. 핸들러 인터셉터 의존성 해결
        InterceptorResolver.resolve_handler_interceptors(self)

    # ========== 조회 API ==========

    def get_container(self, type_: Type) -> Optional[Container]:
        """
        특정 타입의 컨테이너 조회

        Args:
            type_: 조회할 타입

        Returns:
            Container 또는 None
        """
        if type_ in self.components:
            return self.components[type_]
        elif type_ in self.controllers:
            return self.controllers[type_]
        return None

    def get_instance[T](self, type_: Type[T]) -> Optional[T]:
        """
        특정 타입의 인스턴스 조회

        Args:
            type_: 조회할 타입

        Returns:
            인스턴스 또는 None
        """
        return self.instances.get(type_)

    def get_all_instances(self) -> Dict[Type, Any]:
        """
        모든 인스턴스 반환

        Returns:
            타입: 인스턴스 딕셔너리
        """
        return self.instances.copy()

    def get_controllers(self) -> Dict[Type, Any]:
        """
        모든 컨트롤러 인스턴스 반환

        Returns:
            컨트롤러 타입: 인스턴스 딕셔너리
        """
        return {
            type_: instance
            for type_, instance in self.instances.items()
            if type_ in self.controllers
        }
