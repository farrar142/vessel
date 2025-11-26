"""
RouteHandler - HTTP 요청을 처리하고 핸들러 메서드를 실행
"""

from typing import Any, Dict, List, Callable, Optional, Type
import inspect
from typing import get_type_hints

from vessel.http.request import HttpRequest, HttpResponse
from vessel.di.container_manager import ContainerManager


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
        self._register_routes()

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
                        from vessel.decorators.web.mapping import HttpMethodMappingHandler

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

        except Exception as e:
            # 에러를 Application으로 전파 (Application의 _handle_error에서 처리)
            raise

    def _invoke_handler(self, route: Route, request: HttpRequest) -> Any:
        """
        핸들러 메서드를 실행하면서 파라미터에 값 주입
        """
        handler = route.handler
        sig = inspect.signature(handler)

        # 파라미터 분석 및 값 주입
        kwargs = {}

        try:
            hints = get_type_hints(handler)
        except:
            hints = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = hints.get(param_name, param.annotation)

            # HttpRequest 타입이면 request 객체 주입
            if param_type == HttpRequest or param_type is inspect.Parameter.empty:
                if param_name == "request":
                    kwargs[param_name] = request
                    continue

            # 기본 타입 (str, int, float, bool) 처리
            if param_type in (str, int, float, bool):
                # query params에서 먼저 확인
                if param_name in request.query_params:
                    value = request.query_params[param_name]
                # path params에서 확인
                elif param_name in request.path_params:
                    value = request.path_params[param_name]
                # body에서 확인 (POST, PUT, PATCH)
                elif (
                    request.body
                    and isinstance(request.body, dict)
                    and param_name in request.body
                ):
                    value = request.body[param_name]
                else:
                    continue

                # 타입 변환
                try:
                    if param_type == int:
                        kwargs[param_name] = int(value)
                    elif param_type == float:
                        kwargs[param_name] = float(value)
                    elif param_type == bool:
                        kwargs[param_name] = (
                            value
                            if isinstance(value, bool)
                            else value.lower() in ("true", "1", "yes")
                        )
                    else:
                        kwargs[param_name] = str(value)
                except:
                    pass
                continue

            # Pydantic 모델이나 데이터 클래스인 경우
            if inspect.isclass(param_type):
                # BaseModel 체크 (pydantic)
                if hasattr(param_type, "model_validate"):
                    # Pydantic v2
                    try:
                        if request.body:
                            kwargs[param_name] = param_type.model_validate(request.body)
                        else:
                            kwargs[param_name] = param_type.model_validate({})
                    except:
                        kwargs[param_name] = param_type()
                elif hasattr(param_type, "parse_obj"):
                    # Pydantic v1
                    try:
                        if request.body:
                            kwargs[param_name] = param_type.parse_obj(request.body)
                        else:
                            kwargs[param_name] = param_type.parse_obj({})
                    except:
                        kwargs[param_name] = param_type()
                else:
                    # 일반 클래스는 인스턴스화 시도
                    try:
                        kwargs[param_name] = param_type()
                    except:
                        pass

        # 핸들러 실행
        return handler(**kwargs)

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
