"""
Vessel Validation Module

파라미터 타입 검증 및 변환

Note: ValidationError와 파라미터 주입 로직은 vessel.http.parameter_injection으로 이동되었습니다.
이 모듈은 하위 호환성을 위해 유지됩니다.
"""

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    get_type_hints,
    get_origin,
    get_args,
)

# ValidationError를 parameter_injection에서 import하여 re-export
from vessel.http.parameter_injection import ValidationError

# 하위 호환성을 위해 re-export
__all__ = ["ValidationError", "ParameterValidator"]


class ParameterValidator:
    """
    [DEPRECATED] 파라미터 검증 및 변환

    Note: 이 클래스는 deprecated 되었습니다.
    파라미터 주입 및 검증은 이제 vessel.http.parameter_injection.DefaultValueInjector를 통해
    자동으로 처리됩니다. RouteHandler가 자동으로 모든 injector를 설정합니다.
    """

    @staticmethod
    def validate_and_convert(
        handler_func: Callable,
        request_data: Dict[str, Any],
        skip_params: set | None = None,
    ) -> Dict[str, Any]:
        """
        [DEPRECATED] 핸들러 함수의 파라미터를 검증하고 변환

        이 메서드는 하위 호환성을 위해 유지됩니다.
        새 코드에서는 DefaultValueInjector를 사용하세요.

        Args:
            handler_func: 핸들러 함수
            request_data: 요청 데이터 (query_params, path_params, body 합친 것)
            skip_params: 검증을 건너뛸 파라미터 이름 세트 (이미 처리된 파라미터)

        Returns:
            검증되고 변환된 파라미터 딕셔너리

        Raises:
            ValidationError: 검증 실패 시
        """
        if skip_params is None:
            skip_params = set()

        sig = inspect.signature(handler_func)
        type_hints = get_type_hints(handler_func)

        validated_params = {}
        errors = []

        for param_name, param in sig.parameters.items():
            # self 파라미터 스킵
            if param_name == "self":
                continue

            # 이미 처리된 파라미터 스킵
            if param_name in skip_params:
                continue

            # 파라미터 타입 힌트 확인
            if (
                param_name not in type_hints
                and param.annotation == inspect.Parameter.empty
            ):
                # 타입 힌트가 없으면 에러
                raise TypeError(
                    f"Parameter '{param_name}' in handler '{handler_func.__name__}' "
                    f"must have a type annotation. All parameters (except 'self') require type hints."
                )

            param_type = type_hints.get(param_name, str)

            # 기본값 확인
            has_default = param.default != inspect.Parameter.empty
            default_value = param.default if has_default else None

            # 요청 데이터에서 값 가져오기
            value = request_data.get(param_name)

            # 필수 파라미터 체크
            if value is None:
                if has_default:
                    validated_params[param_name] = default_value
                    continue
                else:
                    errors.append(
                        {
                            "field": param_name,
                            "message": f"Required field '{param_name}' is missing",
                        }
                    )
                    continue

            # 타입 변환 및 검증
            try:
                converted_value = ParameterValidator._convert_type(
                    value, param_type, param_name
                )
                validated_params[param_name] = converted_value
            except (ValueError, TypeError) as e:
                errors.append(
                    {
                        "field": param_name,
                        "message": f"Invalid type for '{param_name}': {str(e)}",
                    }
                )

        if errors:
            raise ValidationError(errors)

        return validated_params

    @staticmethod
    def _convert_type(value: Any, target_type: type, field_name: str) -> Any:
        """
        값을 목표 타입으로 변환

        Args:
            value: 변환할 값
            target_type: 목표 타입
            field_name: 필드 이름 (에러 메시지용)

        Returns:
            변환된 값

        Raises:
            ValueError: 변환 실패 시
        """
        # 이미 올바른 타입이면 그대로 반환
        if isinstance(value, target_type):
            return value

        # 기본 타입 변환
        if target_type == int:
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert '{value}' to int")

        elif target_type == float:
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert '{value}' to float")

        elif target_type == bool:
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    return True
                elif value.lower() in ("false", "0", "no"):
                    return False
            raise ValueError(f"Cannot convert '{value}' to bool")

        elif target_type == str:
            return str(value)

        # List, Dict 등은 그대로 반환
        elif target_type in (list, dict):
            if not isinstance(value, target_type):
                raise ValueError(
                    f"Expected {target_type.__name__}, got {type(value).__name__}"
                )
            return value

        # 기타 타입은 그대로 반환
        return value
