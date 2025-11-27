"""
Vessel Application 사용 예제
"""

from vessel import Application, Component, Controller, Get, Post


# 서비스 계층
@Component
class UserService:
    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
        }

    def get_all_users(self):
        return list(self.users.values())

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def create_user(self, name: str, email: str):
        user_id = max(self.users.keys()) + 1 if self.users else 1
        user = {"id": user_id, "name": name, "email": email}
        self.users[user_id] = user
        return user


@Component
class LogService:
    def __init__(self):
        self.logs = []

    def log(self, message: str):
        self.logs.append(message)
        print(f"[LOG] {message}")


# 컨트롤러 계층
@Controller("/api/users")
class UserController:
    user_service: UserService
    log_service: LogService

    @Get
    def get_users(self):
        """모든 사용자 조회"""
        self.log_service.log("Fetching all users")
        users = self.user_service.get_all_users()
        return {"users": users, "count": len(users)}

    @Get("/{user_id}")
    def get_user(self, user_id: int):
        """특정 사용자 조회"""
        self.log_service.log(f"Fetching user {user_id}")
        user = self.user_service.get_user(user_id)

        if user:
            return user
        else:
            return {"error": "User not found"}, 404

    @Post
    def create_user(self, name: str, email: str):
        """새 사용자 생성"""
        self.log_service.log(f"Creating user: {name}")
        user = self.user_service.create_user(name, email)
        return {"message": "User created", "user": user}


@Controller("/api/health")
class HealthController:
    @Get
    def health_check(self):
        """헬스 체크"""
        return {"status": "ok", "service": "Vessel App"}


def main():
    # Application 생성 및 초기화
    app = Application(
        "__main__",  # 현재 모듈 스캔
        debug=True,
        host="127.0.0.1",
        port=8080,
    )

    # 초기화
    app.initialize()

    # 미들웨어 추가 (선택사항)
    def logging_middleware(request, next_handler):
        print(f"[MIDDLEWARE] {request.method} {request.path}")
        response = next_handler(request)
        print(f"[MIDDLEWARE] Response: {response.status_code}")
        return response

    app.add_middleware(logging_middleware)

    # 에러 핸들러 추가 (선택사항)
    def handle_value_error(error):
        from vessel.http.request import HttpResponse

        return HttpResponse(
            status_code=400, body={"error": "Bad Request", "message": str(error)}
        )

    app.add_error_handler(ValueError, handle_value_error)

    # 수동 요청 테스트
    print("\n=== Manual Request Test ===")
    from vessel.http.request import HttpRequest

    # GET /api/health
    request1 = HttpRequest(method="GET", path="/api/health")
    response1 = app.handle_request(request1)
    print(f"GET /api/health -> {response1.status_code}: {response1.body}")

    # GET /api/users
    request2 = HttpRequest(method="GET", path="/api/users")
    response2 = app.handle_request(request2)
    print(f"GET /api/users -> {response2.status_code}: {response2.body}")

    # GET /api/users/1
    request3 = HttpRequest(method="GET", path="/api/users/1")
    response3 = app.handle_request(request3)
    print(f"GET /api/users/1 -> {response3.status_code}: {response3.body}")

    print("\n=== Starting Server ===")
    print("Try these URLs:")
    print("  - http://127.0.0.1:8080/api/health")
    print("  - http://127.0.0.1:8080/api/users")
    print("  - http://127.0.0.1:8080/api/users/1")
    print()

    # 서버 시작
    app.run()


if __name__ == "__main__":
    main()
