"""
Async Handler Example

이 예제는 sync/async 핸들러를 함께 사용하는 방법을 보여줍니다.
"""

import asyncio
from vessel import Application, Component, Controller, Get


# 동기 서비스
@Component
class DatabaseService:
    def query_user(self, user_id: int):
        """동기적으로 사용자 정보 조회 (예: SQLite)"""
        print(f"[Sync] Querying user {user_id} from database...")
        return {"id": user_id, "name": f"User{user_id}", "type": "sync"}


# 비동기 서비스
@Component
class APIService:
    async def fetch_external_data(self, user_id: int):
        """비동기적으로 외부 API에서 데이터 가져오기"""
        print(f"[Async] Fetching external data for user {user_id}...")
        await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
        return {"userId": user_id, "externalData": "some data", "type": "async"}


# 컨트롤러
@Controller("/api")
class UserController:
    db_service: DatabaseService
    api_service: APIService

    @Get("/user/{user_id}")
    def get_user_sync(self, user_id: int):
        """동기 핸들러 - 빠르게 응답"""
        return self.db_service.query_user(user_id)

    @Get("/user/{user_id}/external")
    async def get_user_with_external(self, user_id: int):
        """비동기 핸들러 - 외부 API 호출"""
        external_data = await self.api_service.fetch_external_data(user_id)
        return external_data

    @Get("/user/{user_id}/full")
    async def get_user_full(self, user_id: int):
        """혼합 핸들러 - sync와 async를 함께 사용"""
        # 동기 서비스 호출 (자동으로 async로 변환됨)
        user = self.db_service.query_user(user_id)

        # 비동기 서비스 호출
        external = await self.api_service.fetch_external_data(user_id)

        return {"user": user, "external": external, "type": "mixed"}

    @Get("/users/batch")
    async def get_users_batch(self):
        """동시에 여러 사용자 데이터 가져오기"""
        # 여러 비동기 작업을 동시에 실행
        tasks = [
            self.api_service.fetch_external_data(1),
            self.api_service.fetch_external_data(2),
            self.api_service.fetch_external_data(3),
        ]

        results = await asyncio.gather(*tasks)
        return {"users": results, "count": len(results)}


if __name__ == "__main__":
    # 애플리케이션 생성 및 초기화
    app = Application(__name__, debug=True)
    app.initialize()  # 초기화 필수!

    print("=" * 60)
    print("Async/Sync Handler Example")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET /api/user/{user_id}          - Sync handler")
    print("  GET /api/user/{user_id}/external - Async handler")
    print("  GET /api/user/{user_id}/full     - Mixed handler")
    print("  GET /api/users/batch             - Concurrent async")
    print("\nTesting endpoints...\n")

    # 테스트 요청
    from vessel.web.http.request import HttpRequest

    # 테스트 1: 동기 방식 호출 (기존 코드 호환)
    print("=" * 60)
    print("방법 1: 동기 방식 호출 (Sync API - 기존 코드 호환)")
    print("=" * 60)
    print("\n1. Testing sync handler (sync call):")
    request = HttpRequest(method="GET", path="/api/user/1")
    response = app.handle_request(request)  # await 없이 호출!
    print(f"   Response: {response.body}\n")

    print("2. Testing async handler (sync call):")
    request = HttpRequest(method="GET", path="/api/user/2/external")
    response = app.handle_request(request)  # await 없이 호출!
    print(f"   Response: {response.body}\n")

    # 테스트 2: 비동기 방식 호출 (새로운 스타일)
    async def test_async_endpoints():
        print("=" * 60)
        print("방법 2: 비동기 방식 호출 (Async API - 새로운 스타일)")
        print("=" * 60)

        # 1. 혼합 핸들러 테스트
        print("\n3. Testing mixed handler (async call):")
        request = HttpRequest(method="GET", path="/api/user/3/full")
        response = await app.handle_request(request)  # await 사용!
        print(f"   Response: {response.body}\n")

        # 2. 동시 요청 테스트
        print("4. Testing concurrent requests (async call):")
        request = HttpRequest(method="GET", path="/api/users/batch")
        response = await app.handle_request(request)  # await 사용!
        print(f"   Response: {response.body}\n")

        # 3. 진짜 동시 요청
        print("5. Testing truly concurrent requests:")
        requests = [
            app.handle_request(HttpRequest(method="GET", path="/api/user/1")),
            app.handle_request(HttpRequest(method="GET", path="/api/user/2/external")),
            app.handle_request(HttpRequest(method="GET", path="/api/user/3/full")),
        ]
        responses = await asyncio.gather(*requests)
        print(f"   Processed {len(responses)} requests concurrently!")
        for i, resp in enumerate(responses, 1):
            print(f"   Response {i}: {resp.body.get('type', 'N/A')}")

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    # 비동기 테스트 실행
    asyncio.run(test_async_endpoints())
