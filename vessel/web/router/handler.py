"""
RouteHandler - HTTP 요청을 처리하고 핸들러 메서드를 실행
"""

from typing import Any, Dict, List, Callable, Optional, Type, get_origin, get_args
import inspect
from typing import get_type_hints

from vessel.http.request import HttpRequest, HttpResponse
from vessel.di.core.container_manager import ContainerManager
from vessel.http.parameter_injection import (
    ParameterInjectorRegistry,
    HttpRequestInjector,
    HttpHeaderInjector,
    HttpCookieInjector,
    FileInjector,
    DefaultValueInjector,
    ValidationError,
    AuthenticationInjector,
)
from vessel.web.auth import AuthenticationException


class Route:
    """라우트 정보를 저장하는 클래스"""

    def __init__(
        self,
        path: str,
        method: str,
        handler: Callable,
        controller_instance: Any,
        controller_class: Type,
    ):
        self.path = path
        self.method = method
        self.handler = handler
        self.controller_instance = controller_instance
        self.controller_class = controller_class


class RouteHandler:
    """
    HTTP 요청을 라우팅하고 핸들러 메서드를 실행하는 클래스
    """

    def __init__(self, container_manager: ContainerManager):
        self.container_manager = container_manager
        self.routes: List[Route] = []
        self._setup_injector_registry()
        self._register_routes()

    def _setup_injector_registry(self):
        """파라미터 주입 레지스트리 설정"""
        self.injector_registry = ParameterInjectorRegistry()
        self.injector_registry.register(HttpRequestInjector())
        self.injector_registry.register(AuthenticationInjector())
        self.injector_registry.register(HttpHeaderInjector())
        self.injector_registry.register(HttpCookieInjector())
        self.injector_registry.register(FileInjector())
        self.injector_registry.register(DefaultValueInjector())  # 가장 낮은 우선순위

    def _register_routes(self):
        """컨트롤러들에서 라우트 정보 수집"""
        controllers = self.container_manager.get_controllers()

        for controller_class, controller_instance in controllers.items():
            # 컨트롤러의 base path 가져오기
            base_path = ""
            if hasattr(controller_class, "__pydi_base_path__"):
                base_path = controller_class.__pydi_base_path__
            elif hasattr(controller_class, "__pydi_request_mapping__"):
                base_path = controller_class.__pydi_request_mapping__

            # 컨트롤러의 메서드들 검사
            for attr_name in dir(controller_instance):
                attr = getattr(controller_instance, attr_name)

                # 핸들러 메서드인지 확인
                if callable(attr) and hasattr(attr, "__pydi_handler__"):
                    method = getattr(attr, "__pydi_http_method__", "GET")
                    path = getattr(attr, "__pydi_path__", "")

                    # 전체 경로 구성
                    full_path = self._combine_paths(base_path, path)

                    # 핸들러 컨테이너가 있으면 인터셉터 적용
                    handler_to_use = attr
                    if hasattr(attr, "__pydi_container__"):
                        from vessel.decorators.web.mapping import (
                            HttpMethodMappingHandler,
                        )

                        container = attr.__pydi_container__
                        if (
                            isinstance(container, HttpMethodMappingHandler)
                            and container.interceptors
                        ):
                            # 인터셉터로 감싼 핸들러 사용
                            handler_to_use = container.wrap_handler(attr)

                    # 라우트 등록
                    route = Route(
                        path=full_path,
                        method=method,
                        handler=handler_to_use,
                        controller_instance=controller_instance,
                        controller_class=controller_class,
                    )
                    self.routes.append(route)

    def _combine_paths(self, base: str, path: str) -> str:
        """베이스 경로와 경로를 결합"""
        base = base.rstrip("/")
        path = path.lstrip("/")

        if not path:
            return base or "/"

        if not base:
            return "/" + path

        return base + "/" + path

    def find_route(self, method: str, path: str) -> Optional[Route]:
        """메서드와 경로에 맞는 라우트 찾기 (path parameter 지원)"""
        for route in self.routes:
            if route.method == method:
                # 정확한 매칭 먼저 시도
                if route.path == path:
                    return route

                # path parameter 패턴 매칭
                if self._match_path_pattern(route.path, path):
                    return route
        return None

    def _match_path_pattern(self, pattern: str, path: str) -> bool:
        """path parameter 패턴 매칭 (예: /users/{id} 와 /users/123 매칭)"""
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        for pattern_part, path_part in zip(pattern_parts, path_parts):
            # {} 로 감싸진 부분은 path parameter로 간주
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                continue
            # 일반 부분은 정확히 일치해야 함
            elif pattern_part != path_part:
                return False

        return True

    def _extract_path_params(self, pattern: str, path: str) -> Dict[str, str]:
        """path에서 parameter 값 추출"""
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")
        params = {}

        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                param_name = pattern_part[1:-1]  # {} 제거
                params[param_name] = path_part

        return params

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        HTTP 요청을 처리
        1. 라우트 찾기
        2. 핸들러 메서드의 파라미터 분석
        3. 파라미터에 값 주입
        4. 핸들러 실행
        """
        route = self.find_route(request.method, request.path)

        if route is None:
            return HttpResponse(body={"error": "Route not found"}, status_code=404)

        # path parameter 추출하여 request에 저장
        path_params = self._extract_path_params(route.path, request.path)
        if path_params:
            request.path_params = path_params

        try:
            # 핸들러 메서드 실행
            result = self._invoke_handler(route, request)

            # 결과를 HttpResponse로 변환
            if isinstance(result, HttpResponse):
                return result
            else:
                return HttpResponse(body=result, status_code=200)

        except AuthenticationException as e:
            # 인증 실패 시 401 에러 반환
            return HttpResponse(status_code=e.status_code, body={"message": e.message})

        except Exception as e:
            # 에러를 Application으로 전파 (Application의 _handle_error에서 처리)
            raise

    def _invoke_handler(self, route: Route, request: HttpRequest) -> Any:
        """
        핸들러 메서드를 실행
        - Registry 패턴으로 모든 파라미터 주입 처리 (validation 포함)
        """
        handler = route.handler

        # 요청 데이터 수집 (query, path, body)
        request_data = self._collect_request_data(request)

        # 타입 힌트 가져오기 (Annotated 타입 포함)
        try:
            hints = get_type_hints(handler, include_extras=True)
        except:
            hints = {}

        # 레지스트리를 통한 모든 파라미터 주입 (DefaultValueInjector가 validation 처리)
        kwargs = self.injector_registry.inject_parameters(
            handler, request, request_data, hints
        )

        # 핸들러 실행
        return handler(**kwargs)

    def _collect_request_data(self, request: HttpRequest) -> Dict[str, Any]:
        """요청 데이터 수집 (query, path, body)"""
        request_data = {}
        request_data.update(request.query_params)
        request_data.update(request.path_params)

        # body 데이터 수집 (파일 데이터도 포함)
        if request.body and isinstance(request.body, dict):
            for key, value in request.body.items():
                request_data[key] = value

        return request_data

    def get_all_routes(self) -> List[Dict[str, str]]:
        """등록된 모든 라우트 정보 반환"""
        return [
            {
                "method": route.method,
                "path": route.path,
                "controller": route.controller_class.__name__,
                "handler": route.handler.__name__,
            }
            for route in self.routes
        ]
