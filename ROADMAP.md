# Vessel Framework - Roadmap

## 🎯 현재 구현 완료된 기능

### Core Features ✅
- [x] Field Injection 기반 DI 시스템
- [x] Topological Sort를 통한 의존성 해결
- [x] 순환 의존성 감지
- [x] @Component, @Factory, @Configuration 데코레이터
- [x] HTTP 라우팅 (@Controller, @Get, @Post, @Put, @Delete, @Patch)
- [x] Handler Interceptor 시스템
- [x] Middleware Chain (CORS, Logging, Authentication)
- [x] RequestBody 자동 변환 (dataclass, Pydantic)
- [x] Path Parameters 자동 변환
- [x] Header/Cookie 주입
- [x] 개발 서버

---

## 🚀 Phase 1: 핵심 기능 강화 (우선순위: 높음)

### 1.1 비동기(Async) 지원 ⭐⭐⭐
**필요성**: 현대적인 웹 프레임워크는 비동기 처리가 필수

```python
@Controller("/api")
class AsyncController:
    service: AsyncService
    
    @Get("/users")
    async def get_users(self):
        return await self.service.fetch_users()

# Middleware도 비동기 지원
class AsyncMiddleware(Middleware):
    async def process_request(self, request: HttpRequest):
        await some_async_operation()
        return None
```

**구현 사항**:
- [ ] async/await 지원 핸들러
- [ ] AsyncMiddleware 베이스 클래스
- [ ] 비동기 DI 초기화 옵션
- [ ] ASGI 서버 통합 (uvicorn)

---

### 1.2 의존성 스코프 (Scope) 시스템 ⭐⭐⭐
**필요성**: 싱글톤만으로는 부족, 요청별/세션별 인스턴스 필요

```python
@Component(scope=Scope.SINGLETON)  # 기본값
class DatabaseConnection:
    pass

@Component(scope=Scope.REQUEST)  # 요청당 새 인스턴스
class RequestContext:
    user_id: str

@Component(scope=Scope.PROTOTYPE)  # 매번 새 인스턴스
class TempService:
    pass
```

**구현 사항**:
- [ ] Scope enum (SINGLETON, REQUEST, PROTOTYPE, SESSION)
- [ ] ScopeManager 클래스
- [ ] Request 스코프 컨텍스트 관리
- [ ] @RequestScope, @Prototype 데코레이터

---

### 1.3 의존성 주입 확장 ⭐⭐
**필요성**: 더 유연한 DI 패턴 지원

```python
# 1. 생성자 주입 옵션 (선택적)
@Component(injection_mode="constructor")
class ServiceWithConstructor:
    def __init__(self, repo: UserRepository):
        self.repo = repo

# 2. Qualifier (같은 타입의 여러 구현체)
@Component
@Qualifier("mysql")
class MySQLRepository(Repository):
    pass

@Component
@Qualifier("postgres")
class PostgresRepository(Repository):
    pass

@Component
class Service:
    repo: Repository = Inject(qualifier="mysql")

# 3. Optional 의존성
@Component
class OptionalService:
    cache: Optional[CacheService] = None  # 없어도 됨
```

**구현 사항**:
- [ ] @Qualifier 데코레이터
- [ ] Inject() 헬퍼 함수
- [ ] Optional 의존성 처리
- [ ] 생성자 주입 옵션

---

### 1.4 Query Parameter & Form Data 지원 ⭐⭐
**필요성**: RESTful API에서 필수적인 기능

```python
@Controller("/api")
class UserController:
    @Get("/search")
    def search_users(
        self,
        query: Query[str],  # ?query=...
        page: Query[int] = 1,  # 기본값
        size: Query[int] = 10
    ):
        return self.service.search(query, page, size)
    
    @Post("/register")
    def register(self, form: Form[UserRegistrationForm]):
        # Form data 처리
        return self.service.register(form)
```

**구현 사항**:
- [ ] Query[T] 타입
- [ ] Form[T] 타입
- [ ] 쿼리 파라미터 검증
- [ ] Form data 파싱

---

## 🔧 Phase 2: 개발 경험 개선 (우선순위: 중간)

### 2.1 Validation 시스템 강화 ⭐⭐
**필요성**: 데이터 검증은 모든 애플리케이션의 필수 요소

```python
from vessel import Validated, Validator

@dataclass
class CreateUserRequest(Validated):
    username: str = Field(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    email: str = Field(email=True)
    age: int = Field(ge=0, le=150)
    
    @Validator
    def validate_age(self):
        if self.age < 18:
            raise ValidationError("Must be 18 or older")

@Post("/users")
def create_user(self, body: RequestBody[CreateUserRequest]):
    # 자동 검증 완료 후 도달
    pass
```

**구현 사항**:
- [ ] Validated 베이스 클래스
- [ ] Field() 헬퍼 (min_length, max, pattern 등)
- [ ] @Validator 데코레이터
- [ ] 커스텀 ValidationError
- [ ] 검증 실패 시 자동 400 응답

---

### 2.2 예외 처리 시스템 ⭐⭐
**필요성**: 일관된 에러 응답 제공

```python
@Component
class GlobalExceptionHandler:
    @ExceptionHandler(ValidationError)
    def handle_validation_error(self, error: ValidationError):
        return HttpResponse(
            status_code=400,
            body={"errors": error.errors}
        )
    
    @ExceptionHandler(NotFoundException)
    def handle_not_found(self, error: NotFoundException):
        return HttpResponse(
            status_code=404,
            body={"message": str(error)}
        )
    
    @ExceptionHandler(Exception)  # 모든 예외의 폴백
    def handle_generic_error(self, error: Exception):
        logger.error(f"Unhandled error: {error}")
        return HttpResponse(
            status_code=500,
            body={"message": "Internal server error"}
        )
```

**구현 사항**:
- [ ] @ExceptionHandler 데코레이터
- [ ] ExceptionHandlerRegistry
- [ ] 예외 우선순위 처리 (구체적 → 일반적)
- [ ] 기본 예외 핸들러들

---

### 2.3 개발 도구 개선 ⭐⭐
**필요성**: 생산성 향상

```python
# 1. CLI 도구
$ vessel new my-project  # 새 프로젝트 생성
$ vessel run --reload    # Hot reload
$ vessel routes          # 등록된 라우트 출력
$ vessel deps            # 의존성 그래프 시각화

# 2. 개발 서버 개선
app = Application(
    "my_app",
    debug=True,
    auto_reload=True,  # 파일 변경 시 자동 재시작
    hot_reload=True    # 코드 변경 시 즉시 반영
)

# 3. 디버깅 엔드포인트
@Get("/debug/routes")  # 디버그 모드에서만
def show_routes():
    return app.get_routes()

@Get("/debug/components")
def show_components():
    return app.get_all_components()
```

**구현 사항**:
- [ ] vessel CLI (Click 사용)
- [ ] 프로젝트 스캐폴딩
- [ ] Auto-reload (watchfiles)
- [ ] 디버그 엔드포인트
- [ ] 의존성 그래프 시각화

---

### 2.4 OpenAPI (Swagger) 자동 생성 ⭐⭐
**필요성**: API 문서화 자동화

```python
@Controller("/api/users")
class UserController:
    @Get("/{user_id}")
    @OpenAPI(
        summary="Get user by ID",
        description="Retrieve a user's information",
        responses={
            200: {"model": UserResponse},
            404: {"description": "User not found"}
        }
    )
    def get_user(self, user_id: int) -> UserResponse:
        pass

# 자동으로 /docs 에서 Swagger UI 제공
app = Application("my_app", enable_swagger=True)
```

**구현 사항**:
- [ ] OpenAPI 스펙 생성기
- [ ] @OpenAPI 데코레이터
- [ ] Swagger UI 통합
- [ ] 타입 힌트에서 스키마 자동 추출

---

## 🌐 Phase 3: 프로덕션 기능 (우선순위: 중간)

### 3.1 데이터베이스 통합 ⭐⭐⭐
**필요성**: 대부분의 애플리케이션에서 필요

```python
# SQLAlchemy 통합
@Component
class DatabaseConfig:
    @Factory
    def database_engine(self) -> Engine:
        return create_engine("postgresql://...")
    
    @Factory
    def session_factory(self, engine: Engine) -> sessionmaker:
        return sessionmaker(bind=engine)

# Repository 패턴
@Component
class UserRepository:
    session_factory: sessionmaker
    
    @Transactional  # 자동 트랜잭션 관리
    def create_user(self, user: User) -> User:
        session = self.session_factory()
        session.add(user)
        return user

# ORM 모델 자동 주입
@Get("/users/{user_id}")
def get_user(self, user: User):  # Path parameter로 자동 조회
    return user
```

**구현 사항**:
- [ ] SQLAlchemy 통합
- [ ] @Transactional 데코레이터
- [ ] Repository 패턴 지원
- [ ] 모델 자동 조회 (by ID)
- [ ] Migration 도구 통합

---

### 3.2 캐싱 시스템 ⭐⭐
**필요성**: 성능 최적화의 핵심

```python
@Component
class UserService:
    @Cacheable(key="user:{user_id}", ttl=300)
    def get_user(self, user_id: int) -> User:
        # 캐시 히트 시 실행 안됨
        return self.repository.find_by_id(user_id)
    
    @CacheEvict(key="user:{user_id}")
    def update_user(self, user_id: int, data: dict):
        # 업데이트 후 캐시 무효화
        pass

# Redis 통합
@Configuration
class CacheConfig:
    @Factory
    def cache_manager(self) -> CacheManager:
        return RedisCacheManager(host="localhost", port=6379)
```

**구현 사항**:
- [ ] @Cacheable 데코레이터
- [ ] @CacheEvict, @CachePut
- [ ] In-memory cache (기본)
- [ ] Redis 통합
- [ ] 캐시 키 생성 전략

---

### 3.3 백그라운드 작업 & 스케줄링 ⭐⭐
**필요성**: 비동기 작업 처리

```python
@Component
class EmailService:
    @Background  # 백그라운드에서 실행
    def send_email(self, to: str, subject: str, body: str):
        # 이메일 전송...
        pass

@Component
class ScheduledTasks:
    @Scheduled(cron="0 0 * * *")  # 매일 자정
    def cleanup_old_data(self):
        # 오래된 데이터 정리
        pass
    
    @Scheduled(interval=timedelta(hours=1))  # 1시간마다
    def refresh_cache(self):
        pass

# Celery 통합
@Component
class HeavyTask:
    @CeleryTask
    def process_large_file(self, file_path: str):
        # Celery worker에서 실행
        pass
```

**구현 사항**:
- [ ] @Background 데코레이터 (ThreadPoolExecutor)
- [ ] @Scheduled 데코레이터
- [ ] Cron 표현식 지원
- [ ] Celery 통합 옵션

---

### 3.4 웹소켓 지원 ⭐⭐
**필요성**: 실시간 통신

```python
@WebSocket("/ws/chat")
class ChatWebSocket:
    room_service: ChatRoomService
    
    async def on_connect(self, websocket: WebSocketConnection):
        await websocket.accept()
    
    async def on_message(self, websocket: WebSocketConnection, message: str):
        # 메시지 브로드캐스트
        await self.room_service.broadcast(message)
    
    async def on_disconnect(self, websocket: WebSocketConnection):
        await self.room_service.leave(websocket.user_id)
```

**구현 사항**:
- [ ] @WebSocket 데코레이터
- [ ] WebSocketConnection 클래스
- [ ] on_connect, on_message, on_disconnect 훅
- [ ] 브로드캐스팅 지원

---

## 🧪 Phase 4: 테스팅 & 품질 (우선순위: 중간)

### 4.1 테스팅 유틸리티 ⭐⭐
**필요성**: 애플리케이션 테스트를 쉽게

```python
from vessel.testing import TestClient, TestCase

class UserControllerTest(TestCase):
    def setUp(self):
        self.client = TestClient(Application("test_app"))
        
        # Mock 의존성
        self.mock_service = Mock(spec=UserService)
        self.client.override(UserService, self.mock_service)
    
    def test_get_user(self):
        self.mock_service.get_user.return_value = User(id=1, name="Test")
        
        response = self.client.get("/api/users/1")
        
        assert response.status_code == 200
        assert response.json()["name"] == "Test"
```

**구현 사항**:
- [ ] TestClient (requests-like API)
- [ ] TestCase 베이스 클래스
- [ ] Mock/Stub 의존성 주입
- [ ] Fixture 지원

---

### 4.2 모니터링 & 로깅 ⭐⭐
**필요성**: 프로덕션 환경에서 필수

```python
# 구조화된 로깅
@Component
class UserService:
    logger: Logger
    
    def create_user(self, data: dict):
        self.logger.info(
            "Creating user",
            extra={"username": data["username"], "action": "create_user"}
        )

# 메트릭 수집
@Component
class MetricsService:
    @Metrics(name="api.request.duration")
    def some_method(self):
        pass

# Health check
@Get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": db.is_connected(),
        "redis": redis.ping()
    }
```

**구현 사항**:
- [ ] 구조화된 로깅 (structlog 통합)
- [ ] @Metrics 데코레이터
- [ ] Health check 엔드포인트
- [ ] Prometheus 메트릭 export

---

## 🔌 Phase 5: 확장성 (우선순위: 낮음)

### 5.1 플러그인 시스템 ⭐
```python
# 플러그인 정의
class MyPlugin(VesselPlugin):
    def on_application_start(self, app: Application):
        # 초기화 로직
        pass
    
    def register_routes(self, app: Application):
        # 라우트 등록
        pass

# 플러그인 사용
app = Application("my_app", plugins=[
    MyPlugin(),
    DatabasePlugin(),
    CachePlugin()
])
```

---

### 5.2 GraphQL 지원 ⭐
```python
@GraphQLSchema
class UserSchema:
    @Query
    def user(self, id: int) -> User:
        return self.user_service.get_user(id)
    
    @Mutation
    def create_user(self, input: CreateUserInput) -> User:
        return self.user_service.create(input)
```

---

### 5.3 gRPC 지원 ⭐
```python
@GrpcService
class UserService:
    @GrpcMethod
    def GetUser(self, request: GetUserRequest) -> UserResponse:
        pass
```

---

## 📊 우선순위 요약

### 🔴 High Priority (즉시 구현 권장)
1. **비동기(Async) 지원** - 현대 웹 프레임워크의 필수
2. **의존성 스코프** - REQUEST, PROTOTYPE 등
3. **Query Parameter & Form** - RESTful API 완성도
4. **Validation 강화** - 데이터 검증 자동화

### 🟡 Medium Priority (다음 단계)
1. **예외 처리 시스템** - 일관된 에러 응답
2. **OpenAPI/Swagger** - 문서화 자동화
3. **데이터베이스 통합** - ORM 지원
4. **개발 도구 개선** - CLI, Hot reload

### 🟢 Low Priority (추후 고려)
1. **캐싱 시스템**
2. **웹소켓 지원**
3. **플러그인 시스템**
4. **GraphQL/gRPC**

---

## 🎓 참고할 프레임워크

- **FastAPI**: 비동기, Validation, OpenAPI
- **Spring Boot**: DI 스코프, 예외 처리, 트랜잭션
- **NestJS**: 모듈 시스템, 데코레이터 패턴
- **Django**: ORM, Admin 패널, 폼 처리

---

## 💡 다음 스프린트 제안

### Sprint 1 (2주): Async 지원
- [ ] 비동기 핸들러 지원
- [ ] AsyncMiddleware
- [ ] ASGI 서버 통합

### Sprint 2 (2주): 의존성 스코프
- [ ] REQUEST 스코프 구현
- [ ] PROTOTYPE 스코프 구현
- [ ] ScopeManager 구현

### Sprint 3 (1주): Query & Form
- [ ] Query[T] 구현
- [ ] Form[T] 구현
- [ ] 파라미터 검증

### Sprint 4 (2주): Validation
- [ ] Validated 베이스 클래스
- [ ] Field() 헬퍼
- [ ] 커스텀 Validator

---

**총평**: Vessel은 이미 견고한 DI와 웹 라우팅 기반을 갖추고 있습니다. 위의 기능들을 단계적으로 추가하면 프로덕션 레벨의 엔터프라이즈 프레임워크로 성장할 수 있습니다! 🚀
