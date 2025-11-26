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
        origin = get_origin(param_type)

        # Annotated[HttpHeader, "name"] 체크
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpHeader:
                return True

        # HttpHeader 직접 체크
        if param_type == HttpHeader:
            return True

        # Optional[HttpHeader] 또는 Optional[Annotated[HttpHeader, "name"]] 체크
        if origin is Union:
            args = get_args(param_type)
            # Union 안에 HttpHeader가 있거나, Annotated[HttpHeader, ...]가 있는지 확인
            for arg in args:
                if arg == HttpHeader:
                    return True
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == HttpHeader:
                        return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """HTTP 헤더 값을 주입"""
        param_type = context.param_type
        request = context.request
        param_name = context.param_name

        # 명시적 이름 추출 (Annotated에서만)
        explicit_name = self._extract_explicit_name(param_type)

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

        # HttpHeader 객체 생성
        http_header = HttpHeader(name=header_name, value=header_value)
        return http_header, False

    def _extract_explicit_name(self, param_type: Any) -> Optional[str]:
        """Annotated 타입에서 명시적으로 지정된 헤더 이름 추출"""
        origin = get_origin(param_type)
        
        # Annotated[HttpHeader, "name"]에서 추출
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == HttpHeader and len(args) > 1:
                return args[1]
        
        # Optional[Annotated[HttpHeader, "name"]]에서 추출
        if origin is Union:
            for arg in get_args(param_type):
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == HttpHeader and len(arg_args) > 1:
                        return arg_args[1]

        return None

    def _is_optional(self, param_type: Any) -> bool:
        """Optional 타입인지 확인"""
        origin = get_origin(param_type)
        if origin is Union:
            args = get_args(param_type)
            # Union 안에 HttpHeader나 Annotated[HttpHeader, ...]와 None이 있는지 확인
            has_none = type(None) in args
            has_http_header = False
            for arg in args:
                if arg == HttpHeader:
                    has_http_header = True
                    break
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == HttpHeader:
                        has_http_header = True
                        break
            return has_none and has_http_header
        return False

    def _convert_to_header_name(self, param_name: str) -> str:
        """파라미터 이름을 헤더 이름으로 변환 (snake_case -> Title-Case)"""
        words = param_name.split("_")
        return "-".join(word.capitalize() for word in words)

    @property
    def priority(self) -> int:
        """HTTP 관련 우선순위"""
        return 100
