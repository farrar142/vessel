# Vessel Web Application

## 🚢 Application 클래스

Vessel의 `Application` 클래스는 웹 애플리케이션의 전체 라이프사이클을 관리하는 핵심 클래스입니다. Spring Boot의 `SpringApplication`과 유사한 역할을 수행합니다.

## ✨ 주요 기능

- ✅ **컴포넌트 스캔 및 의존성 주입 자동 초기화**
- ✅ **HTTP 라우팅 자동 설정**
- ✅ **미들웨어 체인 지원**
- ✅ **CORS 설정**
- ✅ **에러 핸들링**
- ✅ **개발용 내장 서버**
- ✅ **메서드 체이닝 API**

## 🚀 빠른 시작

### 1. 기본 사용법

```python
from vessel import Application, Component, Controller, Get

@Component
class HelloService:
    def greet(self, name: str):
        return f"Hello, {name}!"

@Controller("/api")
class HelloController:
    service: HelloService
    
    @Get("/hello")
    def hello(self):
        return {"message": self.service.greet("World")}

# Application 생성 및 실행
app = Application("__main__", debug=True)
app.initialize()
app.run()
```

### 2. Application 초기화 옵션

```python
app = Application(
    "my_package",           # 스캔할 패키지
    "another_package",      # 여러 패키지 지정 가능
    debug=True,             # 디버그 모드
    enable_cors=True,       # CORS 활성화
    host="0.0.0.0",         # 서버 호스트
    port=8080               # 서버 포트
)
```

### 3. 메서드 체이닝

```python
app = (Application("__main__", debug=True)
    .add_middleware(logging_middleware)
    .add_error_handler(ValueError, handle_value_error)
    .initialize())
```

## 📚 상세 가이드

### 미들웨어 추가

미들웨어를 사용하여 요청/응답 처리를 커스터마이징할 수 있습니다:

```python
def logging_middleware(request, next_handler):
    """로깅 미들웨어"""
    print(f"[IN] {request.method} {request.path}")
    
    response = next_handler(request)
    
    print(f"[OUT] {response.status_code}")
    return response

def auth_middleware(request, next_handler):
    """인증 미들웨어"""
    token = request.headers.get("Authorization")
    
    if not token:
        return HttpResponse(
            status_code=401,
            body={"error": "Unauthorized"}
        )
    
    return next_handler(request)

app = Application("__main__")
app.add_middleware(logging_middleware)
app.add_middleware(auth_middleware)
app.initialize()
```

**미들웨어 실행 순서:**
```
Request → logging_middleware (before)
       → auth_middleware (before)
       → handler
       → auth_middleware (after)
       → logging_middleware (after)
       → Response
```

### 에러 핸들러

특정 예외 타입에 대한 커스텀 에러 핸들러를 등록할 수 있습니다:

```python
from vessel.http.request import HttpResponse

def handle_value_error(error: ValueError):
    return HttpResponse(
        status_code=400,
        body={
            "error": "Bad Request",
            "message": str(error),
            "type": "ValueError"
        }
    )

def handle_permission_error(error: PermissionError):
    return HttpResponse(
        status_code=403,
        body={"error": "Forbidden", "message": "Access denied"}
    )

app = Application("__main__")
app.add_error_handler(ValueError, handle_value_error)
app.add_error_handler(PermissionError, handle_permission_error)
```

### CORS 설정

CORS를 활성화하면 자동으로 다음 헤더가 추가됩니다:

```python
app = Application("__main__", enable_cors=True)
```

추가되는 헤더:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

### 수동 요청 테스트

서버를 시작하지 않고도 요청을 테스트할 수 있습니다:

```python
from vessel.http.request import HttpRequest

app = Application("__main__")
app.initialize()

# GET 요청
request = HttpRequest(method="GET", path="/api/users")
response = app.handle_request(request)
print(response.body)

# POST 요청
request = HttpRequest(
    method="POST",
    path="/api/users",
    body={"name": "Alice", "email": "alice@example.com"}
)
response = app.handle_request(request)
print(response.body)
```

### 인스턴스 가져오기

컨테이너에서 직접 인스턴스를 가져올 수 있습니다:

```python
@Component
class UserService:
    pass

app = Application("__main__")
app.initialize()

# 서비스 인스턴스 가져오기
user_service = app.get_instance(UserService)
```

## 📦 완전한 예제

```python
from vessel import Application, Component, Controller, Get, Post

# === 서비스 계층 ===
@Component
class UserRepository:
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def save(self, user):
        user["id"] = self.next_id
        self.users[self.next_id] = user
        self.next_id += 1
        return user
    
    def find_all(self):
        return list(self.users.values())

@Component
class UserService:
    repo: UserRepository
    
    def create_user(self, name: str, email: str):
        user = {"name": name, "email": email}
        return self.repo.save(user)
    
    def get_all_users(self):
        return self.repo.find_all()

# === 컨트롤러 계층 ===
@Controller("/api/users")
class UserController:
    service: UserService
    
    @Get
    def list_users(self):
        users = self.service.get_all_users()
        return {"users": users, "count": len(users)}
    
    @Post
    def create_user(self, name: str, email: str):
        user = self.service.create_user(name, email)
        return {"message": "User created", "user": user}

# === 미들웨어 ===
def request_logger(request, next_handler):
    print(f"→ {request.method} {request.path}")
    response = next_handler(request)
    print(f"← {response.status_code}")
    return response

# === 애플리케이션 설정 ===
app = Application(
    "__main__",
    debug=True,
    enable_cors=True,
    port=8080
)

app.add_middleware(request_logger)
app.initialize()

# 테스트
from vessel.http.request import HttpRequest

print("=== Testing API ===")

# GET /api/users
response = app.handle_request(HttpRequest("GET", "/api/users"))
print(f"GET /api/users: {response.body}")

# POST /api/users
response = app.handle_request(HttpRequest(
    "POST", "/api/users",
    body={"name": "Alice", "email": "alice@test.com"}
))
print(f"POST /api/users: {response.body}")

# 서버 시작
print("\n=== Starting Server ===")
app.run()
```

## 🔧 개발 vs 프로덕션

### 개발 환경

```python
# 내장 개발 서버 사용
app = Application("__main__", debug=True, port=8080)
app.run()
```

### 프로덕션 환경

프로덕션에서는 Uvicorn, Gunicorn 등의 ASGI/WSGI 서버를 사용하세요:

```python
# 추후 지원 예정
import uvicorn

app = Application("__main__", debug=False)
app.run(server=uvicorn)
```

## 📊 테스트

Application 클래스는 테스트하기 쉽게 설계되었습니다:

```python
def test_user_api():
    @Component
    class TestService:
        def get_data(self):
            return {"test": "data"}
    
    @Controller("/api")
    class TestController:
        service: TestService
        
        @Get("/test")
        def test(self):
            return self.service.get_data()
    
    app = Application("__main__")
    app.initialize()
    
    request = HttpRequest("GET", "/api/test")
    response = app.handle_request(request)
    
    assert response.status_code == 200
    assert response.body == {"test": "data"}
```

## 🎯 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `initialize()` | 컴포넌트 스캔 및 DI 초기화 |
| `add_middleware(fn)` | 미들웨어 추가 |
| `add_error_handler(exc, fn)` | 에러 핸들러 등록 |
| `handle_request(req)` | HTTP 요청 처리 |
| `get_instance(type)` | 인스턴스 가져오기 |
| `run()` | 서버 시작 |
| `stop()` | 서버 중지 |

## 💡 베스트 프랙티스

1. **항상 초기화 먼저**: `app.initialize()` 호출 후 사용
2. **미들웨어 순서**: 로깅 → 인증 → 비즈니스 로직
3. **에러 핸들링**: 구체적인 예외부터 처리
4. **패키지 구조**: 계층별로 명확히 분리 (service, controller, etc.)
5. **테스트**: `handle_request()`로 통합 테스트 작성

## 🔗 관련 문서

- [Container Manager](../core/container_manager.md)
- [Decorators](../decorators/README.md)
- [HTTP Handler](../http/README.md)

---

**Vessel**: 컨테이너처럼 모든 것을 담아 실어 나르는 프레임워크 🚢
