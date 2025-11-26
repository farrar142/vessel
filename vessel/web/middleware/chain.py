"""
Middleware 추상 클래스 및 MiddlewareChain 구현
"""

from typing import Optional, Any, List
from abc import ABC, abstractmethod
from vessel.web.http.request import HttpRequest, HttpResponse


class Middleware(ABC):
    """
    미들웨어 추상 클래스

    모든 미들웨어는 이 클래스를 상속받아야 함
    Component로 등록하여 의존성 주입 가능
    """

    @abstractmethod
    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """
        요청 처리 전 실행

        Args:
            request: HTTP 요청

        Returns:
            None: 다음 미들웨어/핸들러로 진행
            Any: 반환값이 있으면 early return (라우트 핸들러 스킵)
        """
        pass

    @abstractmethod
    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        응답 처리 후 실행

        Args:
            request: HTTP 요청
            response: HTTP 응답

        Returns:
            HttpResponse: 수정된 응답 (또는 원본 응답)
        """
        pass


class MiddlewareGroup:
    """미들웨어 그룹 - 순서가 있는 미들웨어 컬렉션"""

    def __init__(self, name: str = "default"):
        self.name = name
        self.middlewares: List[Middleware] = []
        self.enabled = True

    def add(self, *middlewares: Middleware) -> "MiddlewareGroup":
        """
        미들웨어 추가

        Args:
            *middlewares: 추가할 미들웨어들

        Returns:
            self (메서드 체이닝용)
        """
        for middleware in middlewares:
            if not isinstance(middleware, Middleware):
                raise TypeError(f"{middleware} is not a Middleware instance")
            self.middlewares.append(middleware)
        return self

    def disable(self) -> "MiddlewareGroup":
        """이 그룹 비활성화"""
        self.enabled = False
        return self

    def enable(self) -> "MiddlewareGroup":
        """이 그룹 활성화"""
        self.enabled = True
        return self

    def get_active_middlewares(self) -> List[Middleware]:
        """활성화된 미들웨어 목록 반환"""
        return self.middlewares if self.enabled else []


class MiddlewareChain:
    """
    미들웨어 체인 관리

    여러 미들웨어 그룹을 관리하고 실행 순서 제어
    """

    def __init__(self):
        self.groups: List[MiddlewareGroup] = []
        self.default_group = MiddlewareGroup("default")
        self.groups.append(self.default_group)
        self.disabled_middlewares: set = set()

    def get_default_group(self) -> MiddlewareGroup:
        """기본 그룹 반환"""
        return self.default_group

    def add_group(self, name: str) -> MiddlewareGroup:
        """
        새 그룹 추가 (마지막에)

        Args:
            name: 그룹 이름

        Returns:
            생성된 그룹
        """
        group = MiddlewareGroup(name)
        self.groups.append(group)
        return group

    def add_group_before(
        self, *middlewares: Middleware, target_group: Optional[MiddlewareGroup] = None
    ) -> MiddlewareGroup:
        """
        특정 그룹 앞에 새 그룹 추가

        Args:
            *middlewares: 추가할 미들웨어들
            target_group: 대상 그룹 (None이면 default 그룹 앞)

        Returns:
            생성된 그룹
        """
        target = target_group or self.default_group
        index = self.groups.index(target)

        new_group = MiddlewareGroup(f"before_{target.name}")
        new_group.add(*middlewares)
        self.groups.insert(index, new_group)

        return new_group

    def add_group_after(
        self, *middlewares: Middleware, target_group: Optional[MiddlewareGroup] = None
    ) -> MiddlewareGroup:
        """
        특정 그룹 뒤에 새 그룹 추가

        Args:
            *middlewares: 추가할 미들웨어들
            target_group: 대상 그룹 (None이면 default 그룹 뒤)

        Returns:
            생성된 그룹
        """
        target = target_group or self.default_group
        index = self.groups.index(target) + 1

        new_group = MiddlewareGroup(f"after_{target.name}")
        new_group.add(*middlewares)
        self.groups.insert(index, new_group)

        return new_group

    def disable(self, *middlewares: Middleware) -> "MiddlewareChain":
        """
        특정 미들웨어 비활성화

        Args:
            *middlewares: 비활성화할 미들웨어들

        Returns:
            self (메서드 체이닝용)
        """
        for middleware in middlewares:
            self.disabled_middlewares.add(type(middleware))
        return self

    def enable(self, *middlewares: Middleware) -> "MiddlewareChain":
        """
        특정 미들웨어 활성화

        Args:
            *middlewares: 활성화할 미들웨어들

        Returns:
            self (메서드 체이닝용)
        """
        for middleware in middlewares:
            self.disabled_middlewares.discard(type(middleware))
        return self

    def get_all_middlewares(self) -> List[Middleware]:
        """
        모든 활성화된 미들웨어를 순서대로 반환

        Returns:
            미들웨어 리스트
        """
        all_middlewares = []

        for group in self.groups:
            if not group.enabled:
                continue

            for middleware in group.middlewares:
                # 개별적으로 비활성화된 미들웨어는 제외
                if type(middleware) not in self.disabled_middlewares:
                    all_middlewares.append(middleware)

        return all_middlewares

    def execute_request(self, request: HttpRequest) -> Optional[Any]:
        """
        요청 처리 단계 실행

        Args:
            request: HTTP 요청

        Returns:
            None: 정상 진행
            Any: early return 값
        """
        for middleware in self.get_all_middlewares():
            result = middleware.process_request(request)
            if result is not None:
                # Early return
                return result
        return None

    def execute_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        응답 처리 단계 실행 (역순)

        Args:
            request: HTTP 요청
            response: HTTP 응답

        Returns:
            처리된 응답
        """
        # 역순으로 실행
        for middleware in reversed(self.get_all_middlewares()):
            response = middleware.process_response(request, response)

        return response

    def __repr__(self) -> str:
        active_count = len(self.get_all_middlewares())
        return f"MiddlewareChain(groups={len(self.groups)}, active_middlewares={active_count})"


__all__ = ["Middleware", "MiddlewareChain", "MiddlewareGroup"]
