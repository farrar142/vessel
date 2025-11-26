"""
DefaultValueInjector - 기본 파라미터 타입 변환 및 검증을 처리하는 injector
"""

import inspect
from typing import Any, Dict, List, Tuple, get_type_hints, get_origin, get_args

from vessel.web.router.parameter_injection.base import ParameterInjector, InjectionContext


class ValidationError(Exception):
    """검증 실패 예외"""

    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors
        messages = [f"{err['field']}: {err['message']}" for err in errors]
        super().__init__("; ".join(messages))

    def to_dict(self) -> dict:
        """에러를 딕셔너리로 변환"""
        return {"error": "Validation failed", "details": self.errors}


class DefaultValueInjector(ParameterInjector):
    """
    기본 파라미터 값 주입 및 타입 변환을 처리하는 injector

    Priority: 0 (가장 낮은 우선순위 - 다른 모든 injector가 처리하지 않은 파라미터 처리)

    이 injector는:
    1. request_data에서 값을 가져옴
    2. 타입 변환 수행 (int, bool, list 등)
    3. 필수 파라미터 검증
    4. 기본값 처리
    """

    @property
    def priority(self) -> int:
        """가장 낮은 우선순위 (fallback injector) - 가장 마지막에 실행"""
        return 999

    def can_inject(self, context: InjectionContext) -> bool:
        """
        다른 injector가 처리하지 않은 모든 파라미터를 처리 (fallback injector)

        Args:
            context: Injection context

        Returns:
            True if this parameter should be injected by this injector
        """
        param_name = context.param_name
        param = context.param

        # self 파라미터는 처리하지 않음
        if param_name == "self":
            return False

        # 타입 힌트가 없으면 에러
        if (
            param_name not in context.hints
            and param.annotation == inspect.Parameter.empty
        ):
            raise TypeError(
                f"Parameter '{param_name}' must have a type annotation. "
                f"All parameters (except 'self') require type hints."
            )

        # 모든 일반 파라미터를 처리 (다른 injector가 처리하지 않은 경우)
        # 값이 없고 기본값도 없으면 inject()에서 ValidationError 발생
        return True

    def inject(self, context: InjectionContext) -> Tuple[Any, bool]:
        """
        파라미터 값을 주입

        Args:
            context: Injection context

        Returns:
            Tuple[Any, bool]: (주입된 값, request_data에서 제거 여부)

        Raises:
            ValidationError: 검증 실패 시
        """
        param_name = context.param_name
        param = context.param
        param_type = context.hints.get(param_name, str)
        request_data = context.request_data

        # 기본값 확인
        has_default = param.default != inspect.Parameter.empty
        default_value = param.default if has_default else None

        # 요청 데이터에서 값 가져오기
        value = request_data.get(param_name)

        # 필수 파라미터 체크
        if value is None:
            if has_default:
                return (default_value, True)
            else:
                raise ValidationError(
                    [
                        {
                            "field": param_name,
                            "message": f"Missing required parameter '{param_name}'",
                        }
                    ]
                )

        # 타입 변환
        try:
            converted_value = self._convert_type(value, param_type, param_name)
            return (converted_value, True)
        except ValueError as e:
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": str(e),
                    }
                ]
            )

    def _convert_type(self, value: Any, param_type: type, param_name: str) -> Any:
        """타입 변환 수행"""
        # 이미 올바른 타입이면 그대로 반환
        if isinstance(value, param_type):
            return value

        # Generic 타입 처리 (List, Dict 등)
        origin = get_origin(param_type)
        if origin is not None:
            if origin is list:
                return self._convert_to_list(value, param_type, param_name)
            elif origin is dict:
                return self._convert_to_dict(value, param_type, param_name)
            # 다른 Generic 타입은 그대로 반환
            return value

        # 기본 타입 변환
        try:
            if param_type == bool:
                return self._convert_to_bool(value)
            elif param_type == int:
                return int(value)
            elif param_type == float:
                return float(value)
            elif param_type == str:
                return str(value)
            else:
                # 커스텀 타입이거나 변환 불가능한 경우 그대로 반환
                return value
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert parameter '{param_name}' to {param_type.__name__}: {str(e)}"
            )

    def _convert_to_bool(self, value: Any) -> bool:
        """문자열을 boolean으로 변환"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            else:
                raise ValueError(f"Cannot convert '{value}' to boolean")
        return bool(value)

    def _convert_to_list(self, value: Any, param_type: type, param_name: str) -> List:
        """값을 리스트로 변환"""
        if isinstance(value, list):
            # 이미 리스트면 요소 타입 변환
            args = get_args(param_type)
            if args:
                element_type = args[0]
                return [
                    self._convert_type(item, element_type, f"{param_name}[{i}]")
                    for i, item in enumerate(value)
                ]
            return value
        elif isinstance(value, str):
            # 문자열을 쉼표로 분리
            items = [item.strip() for item in value.split(",")]
            args = get_args(param_type)
            if args:
                element_type = args[0]
                return [
                    self._convert_type(item, element_type, f"{param_name}[{i}]")
                    for i, item in enumerate(items)
                ]
            return items
        else:
            # 단일 값을 리스트로 감싸기
            return [value]

    def _convert_to_dict(self, value: Any, param_type: type, param_name: str) -> Dict:
        """값을 딕셔너리로 변환"""
        if isinstance(value, dict):
            return value
        else:
            raise ValueError(
                f"Cannot convert parameter '{param_name}' to dict: expected dict, got {type(value).__name__}"
            )
