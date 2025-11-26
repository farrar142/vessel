"""
Registry for parameter injectors
"""

from typing import List, Dict, Any, Set
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.request import HttpRequest


class ParameterInjectorRegistry:
    """
    파라미터 주입기들을 관리하는 Registry
    """

    def __init__(self):
        self._injectors: List[ParameterInjector] = []

    def register(self, injector: ParameterInjector) -> None:
        """
        Injector 등록

        Args:
            injector: 등록할 injector
        """
        self._injectors.append(injector)
        # 우선순위 순으로 정렬
        self._injectors.sort(key=lambda x: x.priority)

    def inject_parameters(
        self,
        handler: Any,
        request: HttpRequest,
        request_data: Dict[str, Any],
        hints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        모든 등록된 injector를 사용하여 파라미터 주입

        Args:
            handler: 핸들러 함수
            request: HTTP 요청
            request_data: 요청 데이터
            hints: 타입 힌트

        Returns:
            Dict[str, Any]: 주입된 파라미터들
        """
        sig = inspect.signature(handler)
        kwargs = {}
        params_to_remove_from_request_data: Set[str] = set()

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = hints.get(param_name, param.annotation)

            # 주입 컨텍스트 생성
            context = InjectionContext(
                request=request,
                param_name=param_name,
                param=param,
                param_type=param_type,
                hints=hints,
                request_data=request_data,
            )

            # 우선순위 순으로 injector 실행
            for injector in self._injectors:
                if injector.can_inject(context):
                    value, should_remove = injector.inject(context)
                    kwargs[param_name] = value

                    if should_remove and param_name in request_data:
                        params_to_remove_from_request_data.add(param_name)

                    break  # 첫 번째 매칭된 injector만 실행

        # request_data에서 처리된 파라미터 제거
        for param_name in params_to_remove_from_request_data:
            if param_name in request_data:
                del request_data[param_name]

        return kwargs
