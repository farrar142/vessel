"""
HTTP Cookie parameter injector
"""

from typing import Any, Optional, Tuple, get_origin, get_args, Union, Annotated
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.injection_types import HttpCookie
from vessel.validation import ValidationError


class HttpCookieInjector(ParameterInjector):
    """HTTP 쿠키 파라미터 주입"""

    def can_inject(self, context: InjectionContext) -> bool:
        """HttpCookie 타입 또는 Optional[HttpCookie] 타입인 경우"""
        param_type = context.param_type

        # Annotated[HttpCookie, "name"] 체크
        origin = get_origin(param_type)
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpCookie:
                return True

        # HttpCookie 직접 체크
        if param_type == HttpCookie:
            return True

        # Optional[HttpCookie] 체크
        if origin is Union:
            args = get_args(param_type)
            if HttpCookie in args and type(None) in args:
                return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """HTTP 쿠키 값을 주입"""
        param_type = context.param_type
        param = context.param
        request = context.request
        param_name = context.param_name

        # 명시적 이름 추출
        explicit_name = self._extract_explicit_name(param_type, param)

        # Optional 여부 확인
        is_optional = self._is_optional(param_type)

        # 쿠키 이름 결정 (헤더와 다르게 자동 변환 없음)
        cookie_name = explicit_name if explicit_name else param_name

        # 쿠키 값 가져오기
        cookie_value = request.cookies.get(cookie_name)

        if cookie_value is None:
            if is_optional:
                return None, False
            else:
                raise ValidationError(
                    [
                        {
                            "field": param_name,
                            "message": f"Required cookie '{cookie_name}' is missing",
                        }
                    ]
                )

        return cookie_value, False

    def _extract_explicit_name(
        self, param_type: Any, param: inspect.Parameter
    ) -> Optional[str]:
        """명시적으로 지정된 쿠키 이름 추출"""
        # Annotated에서 추출
        origin = get_origin(param_type)
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpCookie and len(args) > 1:
                return args[1]

        # 기본값에서 추출
        if param.default != inspect.Parameter.empty:
            # HttpCookie 인스턴스인 경우
            if isinstance(param.default, HttpCookie) and param.default.name:
                return param.default.name

            # Annotated 타입인 경우
            default_origin = get_origin(param.default)
            if default_origin is Annotated:
                default_args = get_args(param.default)
                if (
                    default_args
                    and default_args[0] == HttpCookie
                    and len(default_args) > 1
                ):
                    return default_args[1]

        return None

    def _is_optional(self, param_type: Any) -> bool:
        """Optional 타입인지 확인"""
        origin = get_origin(param_type)
        if origin is Union:
            args = get_args(param_type)
            return HttpCookie in args and type(None) in args
        return False

    @property
    def priority(self) -> int:
        """HTTP 관련 우선순위"""
        return 101
