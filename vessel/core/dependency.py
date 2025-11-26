"""
의존성 분석 및 Topological Sort 유틸리티
"""

from typing import Any, Dict, List, Set, Type, get_type_hints
from collections import defaultdict, deque
import inspect


class DependencyGraph:
    """의존성 그래프를 관리하는 클래스"""

    def __init__(self):
        self.graph: Dict[Any, Set[Any]] = defaultdict(set)
        self.reverse_graph: Dict[Any, Set[Any]] = defaultdict(set)

    def add_dependency(self, target: Any, dependency: Any):
        """
        의존성 추가
        target이 dependency에 의존함
        """
        self.graph[target].add(dependency)
        self.reverse_graph[dependency].add(target)

    def get_dependencies(self, target: Any) -> Set[Any]:
        """대상의 모든 의존성 반환"""
        return self.graph.get(target, set())

    def get_dependents(self, target: Any) -> Set[Any]:
        """대상에 의존하는 모든 대상 반환"""
        return self.reverse_graph.get(target, set())

    def topological_sort(self) -> List[Any]:
        """
        Topological Sort를 수행하여 초기화 순서 결정
        Kahn's Algorithm 사용
        """
        # 진입 차수(in-degree) 계산
        in_degree: Dict[Any, int] = defaultdict(int)
        all_nodes = set(self.graph.keys()) | set(self.reverse_graph.keys())

        for node in all_nodes:
            in_degree[node] = len(self.graph.get(node, set()))

        # 진입 차수가 0인 노드들로 시작
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # 이 노드에 의존하는 노드들의 진입 차수 감소
            for dependent in self.reverse_graph.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # 순환 의존성 검사
        if len(result) != len(all_nodes):
            remaining = all_nodes - set(result)
            raise ValueError(f"Circular dependency detected among: {remaining}")

        return result


def extract_dependencies(target: Any) -> Set[Type]:
    """
    클래스나 함수에서 의존성 추출
    타입 힌트를 분석하여 의존하는 타입들을 반환
    """
    dependencies = set()

    try:
        if inspect.isclass(target):
            # 클래스의 __init__ 메서드와 클래스 속성 분석
            hints = get_type_hints(target)
            dependencies.update(hints.values())

            # __init__ 메서드가 있다면 파라미터도 분석
            if hasattr(target, "__init__"):
                init_hints = get_type_hints(target.__init__)
                # 'return' 타입 힌트 제외
                dependencies.update(v for k, v in init_hints.items() if k != "return")

        elif inspect.isfunction(target) or inspect.ismethod(target):
            # 함수나 메서드의 파라미터 분석
            hints = get_type_hints(target)
            # 'return' 타입 힌트 제외
            dependencies.update(v for k, v in hints.items() if k != "return")

    except Exception as e:
        # 타입 힌트를 가져올 수 없는 경우 무시
        pass

    # 기본 타입들 제외 (str, int, float, bool 등)
    filtered_dependencies = set()
    for dep in dependencies:
        if inspect.isclass(dep) and not _is_builtin_type(dep):
            filtered_dependencies.add(dep)

    return filtered_dependencies


def _is_builtin_type(typ: Type) -> bool:
    """내장 타입인지 확인"""
    builtin_types = (str, int, float, bool, list, dict, set, tuple, bytes, bytearray)
    return typ in builtin_types or typ.__module__ == "builtins"
