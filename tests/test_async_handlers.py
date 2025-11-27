"""
Async Handler Support Tests

async 핸들러와 sync 핸들러가 모두 정상적으로 동작하는지 테스트
"""

import pytest
import asyncio
from vessel import Component, Controller, Get, Post
from vessel.di.core.container_manager import ContainerManager
from vessel.web.router import RouteHandler
from vessel.web.request_handler import RequestHandler
from vessel.web.http.request import HttpRequest
from vessel.web.middleware import MiddlewareChain


class TestAsyncHandlers:
    """async 핸들러 지원 테스트"""

    @pytest.fixture
    def services_and_controllers(self):
        """테스트용 서비스와 컨트롤러 생성"""

        # 테스트용 서비스 (sync)
        @Component
        class SyncService:
            def get_message(self):
                return "Hello from sync service"

        # 테스트용 서비스 (async)
        @Component
        class AsyncService:
            async def get_message(self):
                await asyncio.sleep(0.01)  # 비동기 작업 시뮬레이션
                return "Hello from async service"

        # 테스트용 컨트롤러 (sync/async 혼합)
        @Controller("/api")
        class MixedController:
            sync_service: SyncService
            async_service: AsyncService

            @Get("/sync")
            def sync_handler(self):
                """동기 핸들러"""
                return {"message": self.sync_service.get_message(), "type": "sync"}

            @Get("/async")
            async def async_handler(self):
                """비동기 핸들러"""
                message = await self.async_service.get_message()
                return {"message": message, "type": "async"}

            @Get("/mixed")
            async def mixed_handler(self):
                """sync 서비스를 async 핸들러에서 사용"""
                sync_msg = self.sync_service.get_message()
                async_msg = await self.async_service.get_message()
                return {"sync": sync_msg, "async": async_msg, "type": "mixed"}

            @Post("/sync-post")
            def sync_post_handler(self, name: str = "World"):
                """동기 POST 핸들러"""
                return {"greeting": f"Hello, {name}!", "type": "sync-post"}

            @Post("/async-post")
            async def async_post_handler(self, name: str = "World"):
                """비동기 POST 핸들러"""
                await asyncio.sleep(0.01)
                return {"greeting": f"Hello, {name}!", "type": "async-post"}

        return SyncService, AsyncService, MixedController

    @pytest.fixture
    def request_handler(self, services_and_controllers):
        """테스트용 RequestHandler 생성"""
        # ContainerManager 생성 및 초기화
        manager = ContainerManager()
        manager._collect_containers()
        manager.initialize()

        # RouteHandler와 RequestHandler 생성
        route_handler = RouteHandler(manager)
        request_handler = RequestHandler(route_handler, debug=True)

        return request_handler

    @pytest.mark.asyncio
    async def test_sync_handler(self, request_handler):
        """동기 핸들러가 정상적으로 동작하는지 테스트"""
        request = HttpRequest(method="GET", path="/api/sync")
        response = await request_handler.handle_request(request)

        assert response.status_code == 200
        assert response.body["type"] == "sync"
        assert "sync service" in response.body["message"]

    @pytest.mark.asyncio
    async def test_async_handler(self, request_handler):
        """비동기 핸들러가 정상적으로 동작하는지 테스트"""
        request = HttpRequest(method="GET", path="/api/async")
        response = await request_handler.handle_request(request)

        assert response.status_code == 200
        assert response.body["type"] == "async"
        assert "async service" in response.body["message"]

    @pytest.mark.asyncio
    async def test_mixed_handler(self, request_handler):
        """sync/async 혼합 핸들러가 정상적으로 동작하는지 테스트"""
        request = HttpRequest(method="GET", path="/api/mixed")
        response = await request_handler.handle_request(request)

        assert response.status_code == 200
        assert response.body["type"] == "mixed"
        assert "sync service" in response.body["sync"]
        assert "async service" in response.body["async"]

    @pytest.mark.asyncio
    async def test_sync_post_handler(self, request_handler):
        """동기 POST 핸들러가 정상적으로 동작하는지 테스트"""
        request = HttpRequest(
            method="POST", path="/api/sync-post", body={"name": "Alice"}
        )
        response = await request_handler.handle_request(request)

        assert response.status_code == 200
        assert response.body["type"] == "sync-post"
        assert "Alice" in response.body["greeting"]

    @pytest.mark.asyncio
    async def test_async_post_handler(self, request_handler):
        """비동기 POST 핸들러가 정상적으로 동작하는지 테스트"""
        request = HttpRequest(
            method="POST", path="/api/async-post", body={"name": "Bob"}
        )
        response = await request_handler.handle_request(request)

        assert response.status_code == 200
        assert response.body["type"] == "async-post"
        assert "Bob" in response.body["greeting"]

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, request_handler):
        """동시 요청 처리 테스트"""
        requests = [
            HttpRequest(method="GET", path="/api/sync"),
            HttpRequest(method="GET", path="/api/async"),
            HttpRequest(method="GET", path="/api/mixed"),
        ]

        # 동시에 여러 요청 처리
        responses = await asyncio.gather(
            *[request_handler.handle_request(req) for req in requests]
        )

        assert len(responses) == 3
        assert all(r.status_code == 200 for r in responses)
        assert responses[0].body["type"] == "sync"
        assert responses[1].body["type"] == "async"
        assert responses[2].body["type"] == "mixed"

    @pytest.mark.asyncio
    async def test_performance_comparison(self, request_handler):
        """sync vs async 성능 비교 (정보 제공용)"""
        import time

        # Sync 핸들러 10회 실행
        start = time.time()
        for _ in range(10):
            request = HttpRequest(method="GET", path="/api/sync")
            await request_handler.handle_request(request)
        sync_time = time.time() - start

        # Async 핸들러 10회 실행
        start = time.time()
        for _ in range(10):
            request = HttpRequest(method="GET", path="/api/async")
            await request_handler.handle_request(request)
        async_time = time.time() - start

        print(f"\nSync handler: {sync_time:.4f}s")
        print(f"Async handler: {async_time:.4f}s")

        # 둘 다 정상적으로 실행되었는지만 확인
        assert sync_time > 0
        assert async_time > 0
