"""
HTTP Header parameter injector
"""

from typing import Any, Optional, Tuple, get_origin, get_args, Union, Annotated
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.injection_types import HttpHeader
from vessel.validation import ValidationError


class HttpHeaderInjector(ParameterInjector):
    """HTTP 헤더 파라미터 주입"""

    def can_inject(self, context: InjectionContext) -> bool:
        """HttpHeader 타입 또는 Optional[HttpHeader] 타입인 경우"""
        param_type = context.param_type

        # Annotated[HttpHeader, "name"] 체크
        origin = get_origin(param_type)
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpHeader:
                return True

        # HttpHeader 직접 체크
        if param_type == HttpHeader:
            return True

        # Optional[HttpHeader] 체크
        if origin is Union:
            args = get_args(param_type)
            if HttpHeader in args and type(None) in args:
                return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """HTTP 헤더 값을 주입"""
        param_type = context.param_type
        param = context.param
        request = context.request
        param_name = context.param_name

        # 명시적 이름 추출
        explicit_name = self._extract_explicit_name(param_type, param)

        # Optional 여부 확인
        is_optional = self._is_optional(param_type)

        # 헤더 이름 결정
        header_name = (
            explicit_name if explicit_name else self._convert_to_header_name(param_name)
        )

        # 헤더 값 가져오기
        header_value = request.headers.get(header_name)

        if header_value is None:
            if is_optional:
                return None, False
            else:
                raise ValidationError(
                    [
                        {
                            "field": param_name,
                            "message": f"Required header '{header_name}' is missing",
                        }
                    ]
                )

        return header_value, False

    def _extract_explicit_name(
        self, param_type: Any, param: inspect.Parameter
    ) -> Optional[str]:
        """명시적으로 지정된 헤더 이름 추출"""
        # Annotated에서 추출
        origin = get_origin(param_type)
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpHeader and len(args) > 1:
                return args[1]

        # 기본값에서 추출
        if param.default != inspect.Parameter.empty:
            # HttpHeader 인스턴스인 경우
            if isinstance(param.default, HttpHeader) and param.default.name:
                return param.default.name

            # Annotated 타입인 경우
            default_origin = get_origin(param.default)
            if default_origin is Annotated:
                default_args = get_args(param.default)
                if (
                    default_args
                    and default_args[0] == HttpHeader
                    and len(default_args) > 1
                ):
                    return default_args[1]

        return None

    def _is_optional(self, param_type: Any) -> bool:
        """Optional 타입인지 확인"""
        origin = get_origin(param_type)
        if origin is Union:
            args = get_args(param_type)
            return HttpHeader in args and type(None) in args
        return False

    def _convert_to_header_name(self, param_name: str) -> str:
        """파라미터 이름을 헤더 이름으로 변환 (snake_case -> Title-Case)"""
        words = param_name.split("_")
        return "-".join(word.capitalize() for word in words)

    @property
    def priority(self) -> int:
        """HTTP 관련 우선순위"""
        return 100
