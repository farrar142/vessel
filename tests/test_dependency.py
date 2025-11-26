"""
Unit Tests for Dependency Graph and Resolution
"""

import pytest
from vessel.core.dependency import DependencyGraph, extract_dependencies


class TestDependencyGraph:
    """의존성 그래프 테스트"""

    def test_add_dependency(self):
        """의존성 추가 테스트"""
        graph = DependencyGraph()
        graph.add_dependency("A", "B")
        graph.add_dependency("A", "C")

        deps = graph.get_dependencies("A")
        assert "B" in deps
        assert "C" in deps

    def test_topological_sort_simple(self):
        """간단한 위상 정렬 테스트"""
        graph = DependencyGraph()
        graph.add_dependency("A", "B")  # A depends on B
        graph.add_dependency("B", "C")  # B depends on C

        sorted_nodes = graph.topological_sort()

        # C가 먼저, B가 다음, A가 마지막
        c_idx = sorted_nodes.index("C")
        b_idx = sorted_nodes.index("B")
        a_idx = sorted_nodes.index("A")

        assert c_idx < b_idx < a_idx

    def test_topological_sort_complex(self):
        """복잡한 의존성 그래프 테스트"""
        graph = DependencyGraph()
        # D depends on B and C
        graph.add_dependency("D", "B")
        graph.add_dependency("D", "C")
        # B depends on A
        graph.add_dependency("B", "A")
        # C depends on A
        graph.add_dependency("C", "A")

        sorted_nodes = graph.topological_sort()

        # A가 가장 먼저, D가 마지막
        a_idx = sorted_nodes.index("A")
        d_idx = sorted_nodes.index("D")

        assert a_idx < d_idx

    def test_topological_sort_circular_dependency(self):
        """순환 의존성 감지 테스트"""
        graph = DependencyGraph()
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "C")
        graph.add_dependency("C", "A")  # Circular!

        with pytest.raises(ValueError, match="Circular dependency"):
            graph.topological_sort()

    def test_topological_sort_no_dependencies(self):
        """의존성이 없는 경우 테스트"""
        graph = DependencyGraph()
        # 의존성 없이 노드만 추가
        graph.graph["A"] = set()
        graph.graph["B"] = set()

        sorted_nodes = graph.topological_sort()

        assert len(sorted_nodes) == 2
        assert "A" in sorted_nodes
        assert "B" in sorted_nodes


class TestExtractDependencies:
    """의존성 추출 테스트"""

    def test_extract_dependencies_with_type_hints(self):
        """타입 힌트가 있는 클래스의 의존성 추출"""

        class ServiceA:
            pass

        class ServiceB:
            pass

        class ServiceC:
            service_a: ServiceA
            service_b: ServiceB

        deps = extract_dependencies(ServiceC)

        assert ServiceA in deps
        assert ServiceB in deps
        assert len(deps) == 2

    def test_extract_dependencies_no_type_hints(self):
        """타입 힌트가 없는 클래스"""

        class NoHintService:
            pass

        deps = extract_dependencies(NoHintService)
        assert len(deps) == 0

    def test_extract_dependencies_function(self):
        """함수의 의존성 추출"""

        class ServiceA:
            pass

        def my_function(service: ServiceA):
            pass

        deps = extract_dependencies(my_function)
        assert ServiceA in deps

    def test_extract_dependencies_builtin_types(self):
        """내장 타입은 무시"""

        class MyClass:
            name: str
            age: int
            active: bool

        deps = extract_dependencies(MyClass)
        # 내장 타입은 의존성으로 간주하지 않음
        assert len(deps) == 0
