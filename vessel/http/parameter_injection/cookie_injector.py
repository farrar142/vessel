"""
HTTP Cookie parameter injector
"""

from typing import Any, Optional

from vessel.http.parameter_injection.annotated_value_injector import (
    AnnotatedValueInjector,
)
from vessel.http.parameter_injection.base import InjectionContext
from vessel.http.injection_types import HttpCookie


class HttpCookieInjector(AnnotatedValueInjector):
    """HTTP 쿠키 파라미터 주입"""

    def get_marker_type(self) -> type:
        """HttpCookie 타입 반환"""
        return HttpCookie

    def extract_value_from_request(
        self, context: InjectionContext, name: str
    ) -> Optional[str]:
        """요청에서 쿠키 값 추출"""
        return context.request.cookies.get(name)

    def get_default_name(self, param_name: str) -> str:
        """파라미터 이름을 쿠키 이름으로 변환 (변환 없이 그대로 사용)"""
        return param_name

    def create_value_object(self, name: str, value: str) -> HttpCookie:
        """HttpCookie 값 객체 생성"""
        return HttpCookie(name=name, value=value)

    def get_error_message(self, name: str, param_name: str) -> str:
        """필수 쿠키 누락 에러 메시지"""
        return f"Required cookie '{name}' is missing"

    @property
    def priority(self) -> int:
        """HTTP 관련 우선순위"""
        return 101
