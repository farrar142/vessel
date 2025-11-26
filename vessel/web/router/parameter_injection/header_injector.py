"""
HTTP Header parameter injector
"""

from typing import Any, Optional

from vessel.web.router.parameter_injection.annotated_value_injector import (
    AnnotatedValueInjector,
)
from vessel.web.router.parameter_injection.base import InjectionContext
from vessel.web.http.injection_types import HttpHeader


class HttpHeaderInjector(AnnotatedValueInjector):
    """HTTP 헤더 파라미터 주입"""

    def get_marker_type(self) -> type:
        """HttpHeader 타입 반환"""
        return HttpHeader

    def extract_value_from_request(
        self, context: InjectionContext, name: str
    ) -> Optional[str]:
        """요청에서 헤더 값 추출"""
        return context.request.headers.get(name)

    def get_default_name(self, param_name: str) -> str:
        """파라미터 이름을 헤더 이름으로 변환 (snake_case -> Title-Case)"""
        return self._convert_to_header_name(param_name)

    def create_value_object(self, name: str, value: str) -> HttpHeader:
        """HttpHeader 값 객체 생성"""
        return HttpHeader(name=name, value=value)

    def get_error_message(self, name: str, param_name: str) -> str:
        """필수 헤더 누락 에러 메시지"""
        return f"Required header '{name}' is missing"

    def _convert_to_header_name(self, param_name: str) -> str:
        """파라미터 이름을 헤더 이름으로 변환 (snake_case -> Title-Case)"""
        words = param_name.split("_")
        return "-".join(word.capitalize() for word in words)

    @property
    def priority(self) -> int:
        """HTTP 관련 우선순위"""
        return 100
