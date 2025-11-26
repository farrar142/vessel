"""
Container 기본 클래스 및 관련 유틸리티
"""

from typing import Any, Callable, Optional, Type, Dict, List
from abc import ABC, abstractmethod
from enum import Enum


class ContainerType(Enum):
    """컨테이너 타입"""

    COMPONENT = "component"
    FACTORY = "factory"
    CONTROLLER = "controller"
    HANDLER = "handler"


class Container(ABC):
    """
    모든 컨테이너의 기본 추상 클래스
    중첩 가능한 데코레이터 시스템을 지원
    """

    def __init__(self, target: Any):
        self.target = target
        self.container_type: ContainerType = ContainerType.COMPONENT
        self.metadata: Dict[str, Any] = {}
        self.nested_containers: List["Container"] = []

    def add_nested_container(self, container: "Container"):
        """중첩된 컨테이너 추가"""
        self.nested_containers.append(container)

    def get_nested_containers(self) -> List["Container"]:
        """중첩된 컨테이너 목록 반환"""
        return self.nested_containers

    @abstractmethod
    def initialize(self, *args, **kwargs) -> Any:
        """컨테이너 초기화 메서드"""
        pass

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """메타데이터 조회"""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any):
        """메타데이터 설정"""
        self.metadata[key] = value


class ContainerHolder:
    """
    컨테이너들을 관리하는 홀더 클래스
    클래스나 메서드에 중첩된 컨테이너들을 저장하고 관리
    """

    def __init__(self, target: Any):
        self.target = target
        self.containers: List[Container] = []

    def add_container(self, container: Container):
        """컨테이너 추가"""
        self.containers.append(container)

    def get_containers(self) -> List[Container]:
        """모든 컨테이너 반환"""
        return self.containers

    def get_containers_by_type(self, container_type: ContainerType) -> List[Container]:
        """특정 타입의 컨테이너들만 반환"""
        return [c for c in self.containers if c.container_type == container_type]

    def has_container_type(self, container_type: ContainerType) -> bool:
        """특정 타입의 컨테이너가 있는지 확인"""
        return any(c.container_type == container_type for c in self.containers)


# 컨테이너 홀더를 저장하는 전역 레지스트리
_container_registry: Dict[Any, ContainerHolder] = {}


def get_container_holder(target: Any) -> Optional[ContainerHolder]:
    """대상 객체의 ContainerHolder 조회"""
    return _container_registry.get(target)


def get_or_create_container_holder(target: Any) -> ContainerHolder:
    """대상 객체의 ContainerHolder를 가져오거나 생성"""
    if target not in _container_registry:
        _container_registry[target] = ContainerHolder(target)
    return _container_registry[target]


def register_container(target: Any, container: Container):
    """컨테이너를 대상 객체에 등록"""
    holder = get_or_create_container_holder(target)
    holder.add_container(container)


def get_all_registered_targets() -> List[Any]:
    """등록된 모든 대상 객체 반환"""
    return list(_container_registry.keys())
