"""
Integration Tests for Decorator Factory with Dependency Injection
"""

import pytest
from vessel import (
    Component,
    Controller,
    ContainerManager,
    HandlerInterceptor,
    create_handler_decorator,
    Get,
)


class TestDecoratorFactoryIntegration:
    """데코레이터 팩토리 통합 테스트"""

    def test_interceptor_with_dependency_injection(self):
        """인터셉터 의존성 주입 테스트 - 실제 사용 검증"""

        @Component
        class LoggerService:
            def __init__(self):
                self.logs = []

            def log(self, message):
                self.logs.append(message)

        class LoggingInterceptor(HandlerInterceptor):
            logger: LoggerService

            def before(self, *args, **kwargs):
                self.logger.log("before")
                return args, kwargs

            def after(self, result, *args, **kwargs):
                self.logger.log("after")
                return result

        Logging = create_handler_decorator(LoggingInterceptor, inject_dependencies=True)

        @Controller
        class TestController:
            @Get("/test")
            @Logging
            def test_handler(self):
                return {"result": "ok"}

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        # LoggerService 인스턴스 확인
        logger = manager.get_instance(LoggerService)
        assert logger is not None
        assert isinstance(logger.logs, list)
        assert len(logger.logs) == 0  # 아직 핸들러 실행 전

        # RouteHandler를 통해 핸들러 실행 - 인터셉터가 실제로 동작
        from vessel.http.route_handler import RouteHandler
        from vessel.http.request import HttpRequest

        route_handler = RouteHandler(manager)
        request = HttpRequest(method="GET", path="/test")
        response = route_handler.handle_request(request)

        # 결과 확인
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

        # 인터셉터가 주입받은 LoggerService를 실제로 사용했는지 검증
        assert len(logger.logs) == 2
        assert logger.logs[0] == "before"
        assert logger.logs[1] == "after"

    def test_multiple_interceptors_with_dependencies(self):
        """여러 인터셉터가 각각 의존성 주입 받는 테스트 - 실제 사용 검증"""

        @Component
        class ServiceA:
            def __init__(self):
                self.called = False

            def mark_called(self):
                self.called = True

        @Component
        class ServiceB:
            def __init__(self):
                self.count = 0

            def increment(self):
                self.count += 1

        class InterceptorA(HandlerInterceptor):
            service_a: ServiceA

            def before(self, *args, **kwargs):
                self.service_a.mark_called()
                return args, kwargs

        class InterceptorB(HandlerInterceptor):
            service_b: ServiceB

            def before(self, *args, **kwargs):
                self.service_b.increment()
                return args, kwargs

        Combined = create_handler_decorator(
            InterceptorA, InterceptorB, inject_dependencies=True
        )

        @Controller
        class TestController:
            @Get("/test")
            @Combined
            def test_handler(self):
                return {"result": "ok"}

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        service_a = manager.get_instance(ServiceA)
        service_b = manager.get_instance(ServiceB)

        assert service_a is not None
        assert service_b is not None

        # 초기 상태 확인
        assert service_a.called is False
        assert service_b.count == 0

        # RouteHandler를 통해 핸들러 실행 - 인터셉터들이 실제로 동작
        from vessel.http.route_handler import RouteHandler
        from vessel.http.request import HttpRequest

        route_handler = RouteHandler(manager)
        request = HttpRequest(method="GET", path="/test")
        response = route_handler.handle_request(request)

        # 결과 확인
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

        # 각 인터셉터가 주입받은 서비스를 실제로 사용했는지 검증
        assert service_a.called is True  # InterceptorA가 ServiceA를 사용함
        assert service_b.count == 1  # InterceptorB가 ServiceB를 사용함

    def test_interceptor_without_dependencies(self):
        """의존성이 없는 인터셉터 테스트 - 상태 변경 검증"""

        # 인터셉터 인스턴스를 추적하기 위한 전역 변수
        interceptor_instance = None

        class SimpleInterceptor(HandlerInterceptor):
            def __init__(self):
                self.called = False
                self.call_count = 0
                nonlocal interceptor_instance
                interceptor_instance = self

            def before(self, *args, **kwargs):
                self.called = True
                self.call_count += 1
                return args, kwargs

        Simple = create_handler_decorator(SimpleInterceptor, inject_dependencies=False)

        @Controller
        class TestControllerNoDeps:
            @Get("/test")
            @Simple
            def test_handler(self):
                return {"result": "ok"}

        manager = ContainerManager()
        # component_scan 대신 _collect_containers 직접 호출
        manager._collect_containers()
        manager.initialize()

        # 컨트롤러가 초기화되어야 함
        controllers = manager.get_controllers()
        assert TestControllerNoDeps in controllers

        # 초기 상태 확인
        assert interceptor_instance is not None
        assert interceptor_instance.called is False
        assert interceptor_instance.call_count == 0

        # RouteHandler를 통해 핸들러 실행 - 인터셉터가 실제로 동작
        from vessel.http.route_handler import RouteHandler
        from vessel.http.request import HttpRequest

        route_handler = RouteHandler(manager)
        request = HttpRequest(method="GET", path="/test")
        response = route_handler.handle_request(request)

        # 결과 확인
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

        # 인터셉터가 실제로 실행되었는지 검증
        assert interceptor_instance.called is True
        assert interceptor_instance.call_count == 1

        # 한 번 더 호출
        response2 = route_handler.handle_request(request)
        assert response2.status_code == 200
        assert interceptor_instance.call_count == 2

    def test_mixed_dependencies_and_no_dependencies(self):
        """의존성 있는/없는 인터셉터 혼합 테스트 - 실제 동작 검증"""

        @Component
        class Logger:
            def __init__(self):
                self.messages = []

            def log(self, msg):
                self.messages.append(msg)

        simple_call_count = 0

        class LoggingInterceptor(HandlerInterceptor):
            logger: Logger

            def before(self, *args, **kwargs):
                self.logger.log("logging")
                return args, kwargs

        class SimpleInterceptor(HandlerInterceptor):
            def before(self, *args, **kwargs):
                nonlocal simple_call_count
                simple_call_count += 1
                return args, kwargs

        Mixed = create_handler_decorator(
            LoggingInterceptor,  # 의존성 있음
            SimpleInterceptor,  # 의존성 없음
            inject_dependencies=True,
        )

        @Controller
        class TestController:
            @Get("/test")
            @Mixed
            def test_handler(self):
                return {"result": "ok"}

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        logger = manager.get_instance(Logger)
        assert logger is not None
        assert len(logger.messages) == 0  # 초기 상태
        assert simple_call_count == 0

        # RouteHandler를 통해 핸들러 실행 - 두 인터셉터가 모두 동작
        from vessel.http.route_handler import RouteHandler
        from vessel.http.request import HttpRequest

        route_handler = RouteHandler(manager)
        request = HttpRequest(method="GET", path="/test")
        response = route_handler.handle_request(request)

        # 결과 확인
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

        # LoggingInterceptor가 주입받은 Logger를 사용했는지 검증
        assert len(logger.messages) == 1
        assert logger.messages[0] == "logging"

        # SimpleInterceptor가 실행되었는지 검증
        assert simple_call_count == 1


class TestHTTPIntegration:
    """HTTP 라우팅 통합 테스트"""

    def test_route_registration(self):
        """라우트 등록 테스트"""

        @Component
        class DataService:
            def get_data(self):
                return {"data": "test"}

        @Controller
        class ApiController:
            service: DataService

            @Get("/api/data")
            def get_data_endpoint(self):
                return self.service.get_data()

        manager = ContainerManager()
        manager.component_scan("__main__")
        manager.initialize()

        from vessel.http.route_handler import RouteHandler

        route_handler = RouteHandler(manager)

        # 라우트가 등록되어야 함
        assert len(route_handler.routes) > 0

        # 특정 라우트 찾기
        found = False
        for route in route_handler.routes:
            if route.path == "/api/data" and route.method == "GET":
                found = True
                break

        assert found, "Route /api/data not found"
