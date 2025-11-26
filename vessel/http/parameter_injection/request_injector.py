"""
HttpRequest parameter injector
"""

from typing import Any, Optional, Tuple
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.request import HttpRequest


class HttpRequestInjector(ParameterInjector):
    """HttpRequest 타입 파라미터 주입"""

    def can_inject(self, context: InjectionContext) -> bool:
        """HttpRequest 타입이거나 'request' 이름인 경우"""
        return context.param_type == HttpRequest or (
            context.param_name == "request"
            and context.param_type is inspect.Parameter.empty
        )

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """HttpRequest 객체를 주입하고, request_data에서 제거"""
        return context.request, True

    @property
    def priority(self) -> int:
        """최고 우선순위"""
        return 0
