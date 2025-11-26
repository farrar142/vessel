"""
MiddlewareChain 통합 테스트
"""

import pytest
from vessel import (
    Component,
    Configuration,
    Factory,
    Application,
    Middleware,
    MiddlewareChain,
    HttpRequest,
    HttpResponse,
)


def test_middleware_chain_auto_detection():
    """MiddlewareChain 자동 감지 테스트"""

    @Component
    class SimpleMiddleware(Middleware):
        def process_request(self, request: HttpRequest):
            request.context["test"] = "value"
            return None

        def process_response(self, request: HttpRequest, response: HttpResponse):
            return response

    @Configuration
    class TestConfig:
        @Factory
        def middleware_chain(self, simple: SimpleMiddleware) -> MiddlewareChain:
            chain = MiddlewareChain()
            chain.get_default_group().add(simple)
            return chain

    app = Application("__main__", debug=False)
    app.initialize()

    # MiddlewareChain이 감지되었는지 확인
    assert app.middleware_chain is not None
    assert len(app.middleware_chain.get_all_middlewares()) == 1


def test_middleware_di_injection():
    """미들웨어에 의존성 주입 테스트"""

    @Component
    class MessageService:
        def get_message(self) -> str:
            return "Test Message"

    @Component
    class TestMiddleware(Middleware):
        service: MessageService

        def process_request(self, request: HttpRequest):
            msg = self.service.get_message()
            request.context["message"] = msg
            return None

        def process_response(self, request: HttpRequest, response: HttpResponse):
            if "message" in request.context:
                response.headers["X-Test-Message"] = request.context["message"]
            return response

    @Configuration
    class TestConfig:
        @Factory
        def middleware_chain(self, test: TestMiddleware) -> MiddlewareChain:
            chain = MiddlewareChain()
            chain.get_default_group().add(test)
            return chain

    app = Application("__main__", debug=False)
    app.initialize()

    request = HttpRequest(method="GET", path="/test", headers={})
    response = app.handle_request(request)

    # 미들웨어가 서비스를 사용했는지 확인
    assert "X-Test-Message" in response.headers
    assert response.headers["X-Test-Message"] == "Test Message"


def test_middleware_early_return():
    """미들웨어 early return 테스트"""

    @Component
    class BlockingMiddleware(Middleware):
        def process_request(self, request: HttpRequest):
            # early return - 라우트 핸들러 실행 안 됨
            return HttpResponse(status_code=403, body={"blocked": True})

        def process_response(self, request: HttpRequest, response: HttpResponse):
            return response

    @Configuration
    class TestConfig:
        @Factory
        def middleware_chain(self, blocking: BlockingMiddleware) -> MiddlewareChain:
            chain = MiddlewareChain()
            chain.get_default_group().add(blocking)
            return chain

    app = Application("__main__", debug=False)
    app.initialize()

    request = HttpRequest(method="GET", path="/test", headers={})
    response = app.handle_request(request)

    # early return이 작동했는지 확인
    assert response.status_code == 403
    assert response.body == {"blocked": True}


def test_middleware_execution_order():
    """미들웨어 실행 순서 테스트"""
    execution_order = []

    @Component
    class FirstMiddleware(Middleware):
        def process_request(self, request: HttpRequest):
            execution_order.append("first_request")
            return None

        def process_response(self, request: HttpRequest, response: HttpResponse):
            execution_order.append("first_response")
            return response

    @Component
    class SecondMiddleware(Middleware):
        def process_request(self, request: HttpRequest):
            execution_order.append("second_request")
            return None

        def process_response(self, request: HttpRequest, response: HttpResponse):
            execution_order.append("second_response")
            return response

    @Configuration
    class TestConfig:
        @Factory
        def middleware_chain(
            self, first: FirstMiddleware, second: SecondMiddleware
        ) -> MiddlewareChain:
            chain = MiddlewareChain()
            group = chain.get_default_group()
            group.add(first)
            group.add(second)
            return chain

    app = Application("__main__", debug=False)
    app.initialize()

    request = HttpRequest(method="GET", path="/test", headers={})
    app.handle_request(request)

    # 요청은 순방향, 응답은 역방향
    assert execution_order == [
        "first_request",
        "second_request",
        "second_response",
        "first_response",
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
