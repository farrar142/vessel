"""
Base interface for parameter injection system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
import inspect

from vessel.http.request import HttpRequest


@dataclass
class InjectionContext:
    """파라미터 주입에 필요한 컨텍스트 정보"""

    request: HttpRequest
    param_name: str
    param: inspect.Parameter
    param_type: Any
    hints: Dict[str, Any]
    request_data: Dict[str, Any]


class ParameterInjector(ABC):
    """
    파라미터 주입을 담당하는 추상 클래스
    각 타입별로 구현하여 Registry에 등록
    """

    @abstractmethod
    def can_inject(self, context: InjectionContext) -> bool:
        """
        이 injector가 해당 파라미터를 처리할 수 있는지 확인

        Args:
            context: 주입 컨텍스트

        Returns:
            bool: 처리 가능 여부
        """
        pass

    @abstractmethod
    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """
        파라미터 값을 주입

        Args:
            context: 주입 컨텍스트

        Returns:
            Tuple[Optional[Any], bool]: (주입된 값, request_data에서 제거 여부)
        """
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        주입 우선순위 (낮을수록 먼저 실행)
        0-99: 특수 타입 (HttpRequest 등)
        100-199: HTTP 관련 (HttpHeader, HttpCookie)
        200-299: 파일
        300+: 일반 파라미터
        """
        pass
