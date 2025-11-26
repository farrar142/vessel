# Vessel Framework - Development Progress# Vessel Framework - Development Progress



> Last Updated: 2025-11-26> Last Updated: 2025-11-26



## 📋 목차## 📋 목차

1. [완료된 작업](#완료된-작업)1. [완료된 작업](#완료된-작업)

2. [프로젝트 구조](#프로젝트-구조)2. [프로젝트 구조](#프로젝트-구조)

3. [향후 개발 계획](#향후-개발-계획)3. [향후 개발 계획](#향후-개발-계획)

4. [테스트 현황](#테스트-현황)

---

---

# 완료된 작업

# 완료된 작업

## ✅ 완료: Path Parameter 지원 추가

## ✅ Phase 1: 핵심 DI 프레임워크 구축

### 구현 내용

### 1.1 Dependency Injection 시스템

- ✅ **Container 시스템** - 컴포넌트 등록 및 관리1. **Path Parameter 패턴 매칭** (`vessel/http/route_handler.py`)

- ✅ **DependencyGraph** - 의존성 그래프 및 순환 의존성 감지   - `_match_path_pattern()`: `/users/{id}` 패턴이 `/users/123` 경로와 매칭

- ✅ **ContainerManager** - DI 컨테이너 전체 관리   - `_extract_path_params()`: 경로에서 파라미터 값 추출 (`{id: "123"}`)

- ✅ **타입 기반 자동 주입** - Type hints를 통한 자동 의존성 주입   - `find_route()`: 정확한 매칭 우선, path parameter 패턴 매칭 지원

- ✅ **싱글톤 패턴** - 컴포넌트의 싱글톤 라이프사이클

2. **파라미터 주입 개선** (`vessel/http/route_handler.py`)

### 1.2 데코레이터 시스템   - 기본 타입(str, int, float, bool) 자동 변환

- ✅ **@Component** - 일반 컴포넌트 등록   - 우선순위: query_params → path_params → body

- ✅ **@Configuration** - 설정 클래스 마킹   - Type hint 기반 자동 변환

- ✅ **@Factory** - Factory 메서드 정의

- ✅ **@Controller** - 웹 컨트롤러 정의## ✅ 완료: MiddlewareChain 시스템 구현

- ✅ **HTTP 메서드 데코레이터** - @Get, @Post, @Put, @Delete, @Patch

- ✅ **@overload 타입 힌트** - IDE 자동완성 개선### 구현된 기능



### 1.3 Interceptor 시스템1. **Middleware ABC** (`vessel/web/middleware.py`)

- ✅ **HandlerContainer** - 인터셉터 체인 관리   - `process_request(request)`: 요청 전처리, early return 가능

- ✅ **HandlerInterceptor 인터페이스** - before/after/on_error 훅   - `process_response(request, response)`: 응답 후처리

- ✅ **Built-in 인터셉터** - @Transaction, @Logging

- ✅ **DI 지원** - 인터셉터도 의존성 주입 가능2. **MiddlewareChain** (`vessel/web/middleware.py`)

   - 여러 미들웨어를 그룹으로 관리

---   - 그룹 추가: `add_group_before()` / `add_group_after()`

   - 미들웨어 제어: `disable()` / `enable()`

## ✅ Phase 2: Web Framework 기능   - 실행: `execute_request()` (early return 지원), `execute_response()` (역순)



### 2.1 HTTP 처리3. **Built-in Middlewares** (`vessel/web/builtins.py`)

- ✅ **HttpRequest/HttpResponse** - HTTP 프로토콜 추상화   - `CorsMiddleware`: CORS 정책 설정

- ✅ **RouteHandler** - 라우트 매칭 및 디스패칭   - `LoggingMiddleware`: 요청/응답 로깅

- ✅ **Path Parameters** - `/users/{id}` 패턴 지원   - `AuthenticationMiddleware`: 인증 처리 예제

- ✅ **자동 타입 변환** - str, int, float, bool 자동 변환   - **@Component 제거**: Factory 패턴으로만 생성

- ✅ **Query Parameters** - URL 쿼리 파라미터 파싱

- ✅ **Request Body** - JSON 요청 본문 파싱4. **@Configuration 데코레이터** (`vessel/decorators/configuration.py`)

   - Spring의 @Configuration과 유사한 패턴

### 2.2 Middleware 시스템   - @Factory 메서드를 그룹핑하는 클래스 마커

- ✅ **Middleware ABC** - 표준 미들웨어 인터페이스

- ✅ **MiddlewareChain** - 미들웨어 체인 관리5. **Application 통합** (`vessel/web/application.py`)        cors.setAllowedMethods

- ✅ **그룹 기능** - 미들웨어를 그룹으로 관리

- ✅ **Early Return** - 요청 처리 조기 종료 지원   - `_detect_middleware_chain()`: 자동으로 MiddlewareChain 감지        cors.setAllowedOrigins

- ✅ **DI 지원** - 미들웨어도 의존성 주입 가능

- ✅ **Built-in 미들웨어**:   - `handle_request()`: MiddlewareChain을 통한 요청/응답 처리        cors.setAllowedHosts

  - CorsMiddleware - CORS 정책 설정

  - LoggingMiddleware - 요청/응답 로깅   - MiddlewareChain이 없으면 미들웨어 시스템 비활성화        return cors



### 2.3 Application 클래스

- ✅ **Application (Facade 패턴)** - 사용자 친화적 API

- ✅ **자동 초기화** - 패키지 스캐닝 및 컴포넌트 등록### 사용 예제

- ✅ **에러 핸들러** - 사용자 정의 에러 처리

- ✅ **DevServer** - 개발용 WSGI 서버 내장```python

from vessel import (

---    Component,

    Configuration,

## ✅ Phase 3: 코드 품질 개선    Factory,

    Middleware,

### 3.1 리팩토링: Application 클래스 분리 (SRP)    MiddlewareChain,

**단일 책임 원칙(Single Responsibility Principle) 적용**    CorsMiddleware,

)

기존 문제점: Application 클래스가 너무 많은 책임 보유

# 1. 커스텀 서비스

**해결: 4개 클래스로 분리**@Component

1. **Application** (Facade) - 사용자 인터페이스class AuthService:

2. **ApplicationInitializer** - DI 초기화 전담    def validate_token(self, token: str) -> bool:

3. **RequestHandler** - HTTP 요청 처리        return token in {"token123"}

4. **DevServer** - 개발 서버 실행

# 2. DI를 사용하는 미들웨어

**효과:**@Component

- 각 클래스가 명확한 단일 책임class CustomAuthMiddleware(Middleware):

- 테스트 가능성 향상    auth_service: AuthService  # DI로 주입됨

- 유지보수성 개선    

    def process_request(self, request):

### 3.2 리팩토링: vessel/ 전체 디렉토리 구조 개편        token = request.headers.get("Authorization", "")[7:]

        

**기존 구조 (혼재):**        if not self.auth_service.validate_token(token):

```            # early return - 인증 실패

vessel/            return HttpResponse(status_code=403, body={"error": "Invalid"})

├── core/           # DI + 기타 혼재        

├── decorators/     # 모든 데코레이터가 한 곳에        return None  # 다음으로 진행

├── http/           # HTTP + Mapping 혼재    

└── web/            # Application + Middleware 평면    def process_response(self, request, response):

```        return response



**개선된 구조 (기능별 분리):**# 3. @Configuration으로 MiddlewareChain 구성

```@Configuration

vessel/class MiddlewareConfig:

├── di/    @Factory

│   ├── core/       # 핵심 DI 컴포넌트    def cors_middleware(self) -> CorsMiddleware:

│   └── utils/      # DI 유틸리티        cors = CorsMiddleware()

├── decorators/        cors.set_allowed_origins("http://localhost:3000")

│   ├── di/         # DI 데코레이터        cors.set_allowed_methods("GET", "POST")

│   ├── web/        # Web 데코레이터        return cors

│   └── handler/    # Interceptor 데코레이터    

├── http/           # HTTP 프로토콜 레이어    @Factory

└── web/            # Application 레이어    def middleware_chain(

    └── middleware/ # 미들웨어 시스템        self,

```        auth: CustomAuthMiddleware,

        cors: CorsMiddleware,

**주요 변경:**    ) -> MiddlewareChain:

- 11개 파일 이동/이름 변경        chain = MiddlewareChain()

- 8개 `__init__.py` 생성        default_group = chain.get_default_group()

- 100+ import 경로 업데이트        default_group.add(cors)

- 하위 호환성 유지 (re-export)        default_group.add(auth)

        return chain

**문서화:**

- `RESTRUCTURE_PLAN.md` - 구조 개편 계획# 4. Application 실행

- `STRUCTURE.md` - 새로운 구조 가이드app = Application("__main__", debug=True)

app.initialize()  # 자동으로 MiddlewareChain 감지

### 3.3 리팩토링: vessel/di 내부 구조화```



**vessel/di를 core와 utils로 분리**### 주요 특징



- **vessel/di/core/** - 핵심 DI 컴포넌트✅ **DI 지원**: Middleware가 다른 컴포넌트를 의존성으로 주입받을 수 있음

  - Container, ContainerManager, DependencyGraph✅ **Early Return**: `process_request()`에서 응답을 반환하면 라우트 핸들러 스킵

  ✅ **그룹 관리**: 여러 미들웨어를 그룹으로 묶고 순서 제어 가능

- **vessel/di/utils/** - DI 유틸리티✅ **자동 감지**: Application이 MiddlewareChain을 DI 컨테이너에서 자동 탐지

  - PackageScanner, ContainerCollector, ComponentInitializer✅ **Factory 패턴**: Built-in middleware는 @Factory로 생성 (메서드가 정해져 있으므로)

  - DependencyAnalyzer, InterceptorResolver✅ **Path Parameter**: `@Get("/{id}")`와 같은 경로 파라미터 지원 및 자동 타입 변환



**효과:**## ✅ 완료: 레거시 코드 제거

- 핵심 기능과 지원 기능 명확히 구분

- 모듈 간 책임 분리### 제거된 항목

- 하위 호환성 유지

1. **Application 클래스**

---   - `self.middlewares` 리스트 제거

   - `add_middleware()` 메서드 제거

# 프로젝트 구조   - `_execute_middlewares()` 메서드 제거

   - MiddlewareChain만 사용

## 📁 최종 디렉토리 구조

2. **테스트 파일**

```   - 레거시 middleware 테스트 제거

vessel/   - 모든 테스트 통과 (60/60)

├── __init__.py                      # 메인 export

│3. **예제 파일**

├── di/                              # ✨ DI (Dependency Injection)   - examples/ 폴더 완전 삭제

│   ├── __init__.py

│   ├── core/                        # 핵심 DI 컴포넌트## 테스트 현황

│   │   ├── __init__.py

│   │   ├── container.py             # Container, ContainerHolder**전체 테스트: 60개**

│   │   ├── container_manager.py     # ContainerManager- ✅ test_application.py: 12/12 통과

│   │   └── dependency.py            # DependencyGraph- ✅ test_component.py: 5/5 통과

│   └── utils/                       # DI 유틸리티- ✅ test_container.py: 4/4 통과

│       ├── __init__.py- ✅ test_dependency.py: 9/9 통과

│       ├── package_scanner.py       # 패키지 스캐닝- ✅ test_handler.py: 14/14 통과

│       ├── container_collector.py   # 컨테이너 수집- ✅ test_integration.py: 7/7 통과

│       ├── component_initializer.py # 컴포넌트 초기화- ✅ test_integration_advanced.py: 5/5 통과

│       ├── dependency_analyzer.py   # 의존성 분석- ✅ test_middleware_integration.py: 4/4 통과

│       └── interceptor_resolver.py  # 인터셉터 해결

│**결과: 100% 통과 (60/60)** ✨

├── decorators/                      # 🎨 데코레이터

│   ├── __init__.py---

│   ├── di/                          # DI 데코레이터

│   │   ├── __init__.py## ✅ 완료: Type Overloading 추가

│   │   ├── component.py             # @Component

│   │   ├── configuration.py         # @Configuration### 구현 내용

│   │   └── factory.py               # @Factory

│   ├── web/                         # Web 데코레이터**HTTP 메서드 데코레이터에 @overload 추가** (`vessel/decorators/web/mapping.py`)

│   │   ├── __init__.py- IDE 자동완성 개선: 함수/메서드 구분

│   │   ├── controller.py            # @Controller, @RequestMapping- 2가지 시그니처:

│   │   └── mapping.py               # @Get, @Post, @Put, @Delete, @Patch  1. `@Get` - 인자 없이 함수에 직접 사용

│   └── handler/                     # Handler/Interceptor  2. `@Get(path)` - 경로 지정 후 함수에 사용

│       ├── __init__.py- 적용 데코레이터: `@Get`, `@Post`, `@Put`, `@Delete`, `@Patch`

│       └── handler.py               # HandlerContainer, Interceptors

│---

├── http/                            # 🌐 HTTP 프로토콜 레이어

│   ├── __init__.py## ✅ 완료: Application 클래스 리팩토링 (SRP)

│   ├── request.py                   # HttpRequest, HttpResponse

│   └── router.py                    # RouteHandler, Route 매칭### 단일 책임 원칙(SRP) 적용

│

└── web/                             # 🚀 Web Application 레이어**기존 문제점:**

    ├── __init__.py- Application 클래스가 너무 많은 책임을 가짐

    ├── application.py               # Application (Facade)- 초기화, 요청 처리, 서버 실행이 하나의 클래스에 혼재

    ├── initializer.py               # ApplicationInitializer

    ├── request_handler.py           # RequestHandler**해결책: 4개 클래스로 분리** (`vessel/web/`)

    ├── server.py                    # DevServer

    └── middleware/                  # 🔗 미들웨어1. **Application (Facade)** - `application.py`

        ├── __init__.py   - 사용자 인터페이스 제공

        ├── chain.py                 # MiddlewareChain, Middleware   - 다른 클래스들을 조합하여 간단한 API 제공

        └── builtins.py              # CorsMiddleware, LoggingMiddleware   - `initialize()`, `handle_request()`, `run()` 등

```

2. **ApplicationInitializer** - `initializer.py`

## 🎯 모듈별 책임   - DI 컨테이너 초기화 전담

   - 패키지 스캐닝 및 컴포넌트 등록

### vessel/di (Dependency Injection)   - 미들웨어 체인 자동 감지

**핵심 책임:** 의존성 주입 시스템 제공

3. **RequestHandler** - `request_handler.py`

- **core/**: Container, ContainerManager, DependencyGraph   - HTTP 요청 처리 로직

- **utils/**: 스캐닝, 수집, 초기화, 분석, 해결   - 라우팅 및 핸들러 실행

   - 에러 처리

### vessel/decorators (Decorators)

**핵심 책임:** 선언적 프로그래밍 지원4. **DevServer** - `server.py`

   - 개발 서버 실행

- **di/**: @Component, @Configuration, @Factory   - wsgiref 기반 WSGI 서버

- **web/**: @Controller, @RequestMapping, HTTP 메서드 매핑

- **handler/**: HandlerContainer, Interceptor system---



### vessel/http (HTTP Protocol)## ✅ 완료: vessel/ 디렉토리 전체 구조 개편

**핵심 책임:** HTTP 프로토콜 추상화

### 1단계: 기능별 디렉토리 구조화

- HttpRequest, HttpResponse

- RouteHandler, Route 매칭 로직**기존 구조 (혼재):**

```

### vessel/web (Application Layer)vessel/

**핵심 책임:** 웹 애플리케이션 구성 및 실행├── core/           # DI + 기타 혼재

├── decorators/     # 모든 데코레이터가 한 곳에

- Application (Facade 패턴)├── http/           # HTTP + Mapping 혼재

- ApplicationInitializer, RequestHandler, DevServer└── web/            # Application + Middleware 평면

- Middleware 시스템 (chain, builtins)```



---**개선된 구조 (기능별 분리):**

```

# 향후 개발 계획vessel/

├── di/                              # DI (Dependency Injection)

## 🚀 Phase 4: 핵심 기능 강화 (우선순위: 높음)│   ├── core/                        # 핵심 DI 컴포넌트

│   │   ├── container.py

### 4.1 DI 기능 개선│   │   ├── container_manager.py

│   │   └── dependency.py

#### Constructor Injection 지원│   └── utils/                       # DI 유틸리티

**현재 문제:**│       ├── package_scanner.py

- 필드 주입만 지원 (클래스 변수에 타입 힌트)│       ├── container_collector.py

- 생성자 주입이 더 명시적이고 테스트하기 좋음│       ├── component_initializer.py

│       ├── dependency_analyzer.py

**목표:**│       └── interceptor_resolver.py

```python│

@Component├── decorators/                      # 데코레이터

class UserService:│   ├── di/                          # DI 데코레이터

    def __init__(self, user_repo: UserRepository):│   │   ├── component.py            # @Component

        self.user_repo = user_repo  # 자동 주입│   │   ├── configuration.py        # @Configuration

```│   │   └── factory.py              # @Factory

│   ├── web/                         # Web 데코레이터

**구현 계획:**│   │   ├── controller.py           # @Controller, @RequestMapping

- `ComponentInitializer`에서 `__init__` 파라미터 분석│   │   └── mapping.py              # @Get, @Post, @Put, @Delete, @Patch

- Type hints 기반 자동 주입│   └── handler/                     # Handler/Interceptor

- 필드 주입과 병행 지원│       └── handler.py              # HandlerContainer, Interceptors

│

---├── http/                            # HTTP 프로토콜 레이어

│   ├── request.py                  # HttpRequest, HttpResponse

#### Lazy Initialization│   └── router.py                   # RouteHandler, Route 매칭

**현재 문제:**│

- 모든 컴포넌트가 즉시 초기화됨└── web/                             # Web Application 레이어

- 사용하지 않는 컴포넌트도 메모리 차지    ├── application.py              # Application (Facade)

    ├── initializer.py              # ApplicationInitializer

**목표:**    ├── request_handler.py          # RequestHandler

```python    ├── server.py                   # DevServer

@Component(lazy=True)    └── middleware/                 # 미들웨어

class HeavyService:        ├── chain.py                # MiddlewareChain, Middleware

    pass  # 첫 사용 시점에 초기화        └── builtins.py             # CorsMiddleware, LoggingMiddleware

``````



**구현 계획:**### 주요 변경사항

- Proxy 패턴 적용

- 첫 접근 시 실제 인스턴스 생성**파일 이동 및 이름 변경:**

- 순환 의존성 방지에도 유용- `vessel/core/` → `vessel/di/` (의미 명확화)

- `vessel/http/http_handler.py` → `vessel/decorators/web/mapping.py`

---- `vessel/http/route_handler.py` → `vessel/http/router.py`

- `vessel/web/app_initializer.py` → `vessel/web/initializer.py`

#### Scope 확장- `vessel/web/dev_server.py` → `vessel/web/server.py`

**현재 상태:**- `vessel/web/middleware.py` → `vessel/web/middleware/chain.py`

- Singleton scope만 지원- `vessel/web/builtins.py` → `vessel/web/middleware/builtins.py`



**목표:****Import 경로 업데이트:**

```python- 모든 내부 import 경로 자동 업데이트 (sed 활용)

@Component(scope="prototype")  # 매번 새 인스턴스- 공개 API는 각 모듈의 `__init__.py`에서 re-export

class RequestContext:- 하위 호환성 유지

    pass

**문서화:**

@Component(scope="request")  # HTTP 요청당 하나- `RESTRUCTURE_PLAN.md`: 구조 개편 계획 문서

class UserSession:- `STRUCTURE.md`: 새로운 구조 가이드 (한글)

    pass

```---



**구현 계획:**## ✅ 완료: vessel/di 내부 구조화 (core/utils 분리)

- `ContainerType` enum에 PROTOTYPE, REQUEST 추가

- REQUEST scope는 thread-local 사용### vessel/di를 core와 utils로 분리

- 스코프별 생성 전략 분리

**vessel/di/core/** - 핵심 DI 컴포넌트

---- `container.py`: Container, ContainerType, ContainerHolder

- `container_manager.py`: ContainerManager (메인 Facade)

#### Qualifier 지원- `dependency.py`: DependencyGraph, extract_dependencies

**현재 문제:**

- 같은 타입의 여러 빈이 있으면 충돌**vessel/di/utils/** - DI 유틸리티

- `package_scanner.py`: 패키지 스캐닝

**목표:**- `container_collector.py`: 컨테이너 수집

```python- `component_initializer.py`: 컴포넌트 초기화

@Component(name="mysql_db")- `dependency_analyzer.py`: 의존성 분석

class MySQLDatabase(Database):- `interceptor_resolver.py`: 인터셉터 해결

    pass

### 하위 호환성

@Component(name="postgres_db")

class PostgresDatabase(Database):```python

    pass# 여전히 작동하는 import (vessel/di/__init__.py에서 re-export)

from vessel.di import Container, ContainerManager, DependencyGraph

@Component

class UserService:# 내부 유틸리티는 명시적 import 필요

    db: Database = Inject(name="mysql_db")  # 특정 빈 선택from vessel.di.utils import PackageScanner, ContainerCollector

``````



**구현 계획:**---

- `@Inject` 데코레이터 추가

- Container에 name 기반 조회 추가# 프로젝트 구조

- 충돌 시 명확한 에러 메시지

## 📁 최종 디렉토리 구조

---

```

### 4.2 Web 기능 확장vessel/

├── __init__.py                      # 메인 export

#### 요청 바디 검증 (Validation)│

**목표:**├── di/                              # ✨ DI (Dependency Injection)

```python│   ├── __init__.py

from pydantic import BaseModel│   ├── core/                        # 핵심 DI 컴포넌트

│   │   ├── __init__.py

class CreateUserRequest(BaseModel):│   │   ├── container.py

    username: str│   │   ├── container_manager.py

    email: str│   │   └── dependency.py

    age: int│   └── utils/                       # DI 유틸리티

│       ├── __init__.py

@Post("/users")│       ├── package_scanner.py

def create_user(req: CreateUserRequest) -> HttpResponse:│       ├── container_collector.py

    # req는 이미 검증됨│       ├── component_initializer.py

    pass│       ├── dependency_analyzer.py

```│       └── interceptor_resolver.py

│

**구현 계획:**├── decorators/                      # 🎨 데코레이터

- Pydantic 통합│   ├── __init__.py

- 타입 힌트 분석하여 자동 검증│   ├── di/                          # DI 데코레이터

- 검증 실패 시 400 에러 자동 반환│   │   ├── __init__.py

│   │   ├── component.py

---│   │   ├── configuration.py

│   │   └── factory.py

#### 파일 업로드 지원│   ├── web/                         # Web 데코레이터

**목표:**│   │   ├── __init__.py

```python│   │   ├── controller.py

@Post("/upload")│   │   └── mapping.py

def upload_file(request: HttpRequest) -> HttpResponse:│   └── handler/                     # Handler/Interceptor

    file = request.files['file']│       ├── __init__.py

    file.save('/uploads/' + file.filename)│       └── handler.py

    return HttpResponse(body={"success": True})│

```├── http/                            # 🌐 HTTP 프로토콜 레이어

│   ├── __init__.py

**구현 계획:**│   ├── request.py

- Multipart form data 파싱│   └── router.py

- `HttpRequest.files` 속성 추가│

- 스트리밍 업로드 (대용량 파일)└── web/                             # 🚀 Web Application 레이어

- 파일 크기 제한 설정    ├── __init__.py

    ├── application.py

---    ├── initializer.py

    ├── request_handler.py

#### 정적 파일 서빙    ├── server.py

**목표:**    └── middleware/                  # 🔗 미들웨어

```python        ├── __init__.py

app = Application("__main__")        ├── chain.py

app.serve_static("/static", "./public")  # /static/css/style.css        └── builtins.py

``````



**구현 계획:**## 🎯 모듈별 책임

- Static file middleware 구현

- 개발 모드에서만 활성화### vessel/di (DI Core)

- MIME type 자동 감지- **core**: Container, ContainerManager, DependencyGraph

- 캐싱 헤더 지원- **utils**: 스캐닝, 수집, 초기화, 분석, 해결



---### vessel/decorators (Decorators)

- **di**: @Component, @Configuration, @Factory

#### 템플릿 엔진 통합- **web**: @Controller, @RequestMapping, @Get, @Post, etc.

**목표:**- **handler**: HandlerContainer, Interceptor system

```python

@Get("/users")### vessel/http (HTTP Protocol)

def list_users(user_service: UserService) -> str:- HttpRequest, HttpResponse

    users = user_service.get_all()- RouteHandler, Route 매칭

    return render_template("users.html", users=users)

```### vessel/web (Application Layer)

- Application (Facade)

**구현 계획:**- ApplicationInitializer, RequestHandler, DevServer

- Jinja2 통합- Middleware 시스템

- `render_template()` 함수 제공

- 템플릿 디렉토리 설정---

- 자동 HTML Content-Type

# 향후 개발 계획

---

## 🚀 Phase 1: 핵심 기능 강화

### 4.3 미들웨어 확장

### 1.1 DI 기능 개선

#### Built-in 미들웨어 추가- [ ] **Constructor Injection 개선**

  - 현재는 필드 주입만 지원

**CompressionMiddleware**  - 생성자 주입 지원 추가

```python  - `@Component` 클래스의 `__init__` 파라미터 자동 주입

@Factory

def compression(self) -> CompressionMiddleware:- [ ] **Lazy Initialization**

    return CompressionMiddleware(min_size=500)  # 500바이트 이상만 압축  - 현재는 모든 컴포넌트가 즉시 초기화

```  - `@Component(lazy=True)` 옵션 추가

  - 첫 사용 시점에 초기화

**RateLimitMiddleware**

```python- [ ] **Scope 확장**

@Factory  - 현재는 Singleton만 지원

def rate_limiter(self) -> RateLimitMiddleware:  - Prototype scope 추가 (매번 새 인스턴스)

    return RateLimitMiddleware(max_requests=100, window=60)  # 1분당 100회  - Request scope 추가 (요청당 하나의 인스턴스)

```

- [ ] **Qualifier 지원**

**SessionMiddleware**  - 같은 타입의 여러 빈이 있을 때 구분

```python  - `@Component(name="primary")` 지정

@Factory  - 주입 시 `@Inject(name="primary")` 사용

def session(self) -> SessionMiddleware:

    return SessionMiddleware(secret_key="secret", max_age=3600)### 1.2 Web 기능 확장

```

- [ ] **요청 바디 검증 (Validation)**

**SecurityHeadersMiddleware**  - Pydantic 통합

```python  - `@Post` 핸들러에 자동 검증

@Factory  - 검증 실패 시 400 에러 자동 반환

def security_headers(self) -> SecurityHeadersMiddleware:

    return SecurityHeadersMiddleware(- [ ] **파일 업로드 지원**

        x_frame_options="DENY",  - Multipart form data 파싱

        x_content_type_options="nosniff",  - `HttpRequest.files` 속성 추가

    )  - 스트리밍 업로드 지원

```

- [ ] **정적 파일 서빙**

---  - `app.serve_static("/static", "./public")` API

  - 개발 모드에서 정적 파일 제공

#### 미들웨어 우선순위  - 프로덕션에서는 Nginx/CDN 권장 메시지

**목표:**

```python- [ ] **템플릿 엔진 통합**

@Component(priority=10)  - Jinja2 통합

class AuthMiddleware(Middleware):  - `@Get` 핸들러에서 템플릿 렌더링

    pass  # 낮은 숫자 = 높은 우선순위  - HTML 응답 자동 생성



@Component(priority=20)### 1.3 미들웨어 확장

class LoggingMiddleware(Middleware):

    pass- [ ] **Built-in 미들웨어 추가**

```  - `CompressionMiddleware`: gzip 압축

  - `RateLimitMiddleware`: Rate limiting

**구현 계획:**  - `SessionMiddleware`: 세션 관리

- `@Component(priority=N)` 지원  - `SecurityHeadersMiddleware`: 보안 헤더

- MiddlewareChain에서 자동 정렬

- 명시적 순서 지정 가능- [ ] **미들웨어 우선순위**

  - 숫자 기반 우선순위 지정

---  - `@Middleware(priority=10)`

  - 자동 정렬 기능

## 🔧 Phase 5: 개발 편의성 (우선순위: 중간)

## 🔧 Phase 2: 개발 편의성

### 5.1 CLI 도구

### 2.1 CLI 도구

**프로젝트 생성**

```bash- [ ] **프로젝트 생성**

vessel create my-project          # 새 프로젝트 생성  ```bash

vessel new controller UserController  # 컨트롤러 생성  vessel create my-project

vessel new component UserService      # 컴포넌트 생성  vessel new controller UserController

vessel new middleware AuthMiddleware  # 미들웨어 생성  vessel new component UserService

```  ```



**구현 계획:**- [ ] **개발 서버 개선**

- Click 또는 Typer 사용  - Hot reload (파일 변경 감지 후 자동 재시작)

- 템플릿 기반 코드 생성  - 더 나은 에러 페이지 (stacktrace 표시)

- 프로젝트 스캐폴딩  - 요청/응답 로깅 개선



---### 2.2 디버깅 도구



### 5.2 개발 서버 개선- [ ] **DI 컨테이너 Inspector**

  - 등록된 모든 컴포넌트 조회

**Hot Reload**  - 의존성 그래프 시각화

- 파일 변경 감지 (watchdog)  - 순환 의존성 경고

- 자동 재시작

- 빠른 피드백 루프- [ ] **Health Check Endpoint**

  - `/health` 엔드포인트 자동 생성

**에러 페이지 개선**  - 각 컴포넌트 상태 체크

- 풀 stacktrace 표시  - Kubernetes readiness/liveness probe 지원

- 코드 스니펫 하이라이팅

- 변수 값 표시### 2.3 테스트 지원



**로깅 개선**- [ ] **테스트 유틸리티**

- 컬러풀한 콘솔 출력  - `@WebTest` - 통합 테스트용 데코레이터

- 요청/응답 상세 정보  - Mock 컴포넌트 주입

- 성능 메트릭 표시  - Test client (`app.test_client()`)



---## 📦 Phase 3: 프로덕션 준비



### 5.3 디버깅 도구### 3.1 성능 최적화



**DI 컨테이너 Inspector**- [ ] **비동기 지원 (asyncio)**

```python  - `async def` 핸들러 지원

from vessel.debug import ContainerInspector  - 비동기 미들웨어

  - 비동기 DI 주입

inspector = ContainerInspector(app)

inspector.list_components()  # 모든 컴포넌트 조회- [ ] **캐싱**

inspector.show_dependencies(UserService)  # 의존성 트리  - 메서드 레벨 캐싱 (`@Cacheable`)

inspector.check_circular()  # 순환 의존성 검사  - Redis 통합

```  - 캐시 무효화 전략



**Health Check Endpoint**### 3.2 보안

```python

@Get("/health")- [ ] **인증/인가 프레임워크**

def health_check() -> dict:  - JWT 토큰 검증

    return {  - Role-based access control

        "status": "healthy",  - `@Secured` 데코레이터

        "components": {...},  # 각 컴포넌트 상태

    }- [ ] **CSRF 보호**

```  - CSRF 토큰 생성/검증

  - POST/PUT/DELETE 요청 보호

---

### 3.3 모니터링

### 5.4 테스트 지원

- [ ] **메트릭 수집**

**테스트 유틸리티**  - 요청 수, 응답 시간 등

```python  - Prometheus 연동

from vessel.testing import WebTest, mock_component  - 대시보드 제공



@WebTest- [ ] **로깅 개선**

class TestUserController:  - 구조화된 로깅 (JSON)

    def test_create_user(self, client, mock_db):  - 로그 레벨 설정

        # client: Test HTTP client  - 외부 로깅 서비스 연동

        # mock_db: Mock 컴포넌트 (자동 주입)

        response = client.post("/users", json={...})## 🌐 Phase 4: 생태계 확장

        assert response.status_code == 201

```### 4.1 ORM 통합



**구현 계획:**- [ ] **SQLAlchemy 통합**

- `@WebTest` 데코레이터  - `@Repository` 데코레이터

- Mock 컴포넌트 주입  - 자동 트랜잭션 관리

- Test client 제공  - 연결 풀링

- Fixture 지원

- [ ] **데이터베이스 마이그레이션**

---  - Alembic 통합

  - CLI 명령어 제공

## 📦 Phase 6: 프로덕션 준비 (우선순위: 낮음)

### 4.2 메시징

### 6.1 성능 최적화

- [ ] **RabbitMQ/Kafka 통합**

#### 비동기 지원 (asyncio)  - `@MessageListener` 데코레이터

```python  - 메시지 발행/구독

@Get("/users")  - 재시도 로직

async def get_users(user_service: UserService) -> list:

    return await user_service.get_all_async()### 4.3 외부 서비스 통합

```

- [ ] **HTTP Client**

**구현 계획:**  - `@HttpClient` 데코레이터

- `async def` 핸들러 지원  - 자동 직렬화/역직렬화

- 비동기 미들웨어  - 재시도 및 타임아웃

- 비동기 DI 주입

- ASGI 서버 통합 (uvicorn)---



---## 📊 테스트 현황



#### 캐싱**전체 테스트: 60개**

```python- ✅ test_application.py: 12/12 통과

from vessel.cache import Cacheable- ✅ test_component.py: 5/5 통과

- ✅ test_container.py: 4/4 통과

@Component- ✅ test_dependency.py: 9/9 통과

class UserService:- ✅ test_handler.py: 14/14 통과

    @Cacheable(ttl=300)  # 5분 캐시- ✅ test_integration.py: 7/7 통과

    def get_user(self, user_id: int):- ✅ test_integration_advanced.py: 5/5 통과

        # 무거운 작업- ✅ test_middleware_integration.py: 4/4 통과

        pass

```**결과: 100% 통과 (60/60)** ✨



**구현 계획:**---

- 메서드 레벨 캐싱

- Redis 통합## 🎓 사용 가이드

- 캐시 무효화 전략

- TTL 설정### 기본 사용법


---

### 6.2 보안

#### 인증/인가
```python
from vessel.security import Secured, jwt_required

@Get("/admin")
@Secured(roles=["admin"])  # admin 역할 필요
def admin_page():
    pass

@Get("/profile")
@jwt_required  # JWT 토큰 검증
def profile():
    pass
```

**구현 계획:**
- JWT 토큰 검증
- Role-based access control
- `@Secured` 데코레이터
- Permission 시스템

---

#### CSRF 보호
```python
@Configuration
class SecurityConfig:
    @Factory
    def csrf_middleware(self) -> CsrfMiddleware:
        return CsrfMiddleware(secret="...")
```

**구현 계획:**
- CSRF 토큰 생성/검증
- POST/PUT/DELETE 자동 보호
- 예외 경로 설정

---

### 6.3 모니터링

#### 메트릭 수집
```python
from vessel.metrics import metrics

@Get("/users")
def get_users():
    with metrics.timer("get_users"):
        # ...
        pass
```

**구현 계획:**
- 요청 수, 응답 시간 등
- Prometheus 연동
- Grafana 대시보드
- 알림 시스템

---

#### 로깅 개선
```python
import structlog

logger = structlog.get_logger()
logger.info("user_created", user_id=123, username="john")
# {"event": "user_created", "user_id": 123, "username": "john", "timestamp": "..."}
```

**구현 계획:**
- 구조화된 로깅 (JSON)
- 로그 레벨 설정
- 외부 로깅 서비스 (CloudWatch, Datadog)
- 분산 추적 (Trace ID)

---

## 🌐 Phase 7: 생태계 확장 (우선순위: 낮음)

### 7.1 ORM 통합

**SQLAlchemy**
```python
from vessel.orm import Repository

@Repository
class UserRepository:
    def find_by_id(self, user_id: int) -> User:
        # SQLAlchemy 세션 자동 주입
        pass
```

**구현 계획:**
- `@Repository` 데코레이터
- 자동 트랜잭션 관리
- 연결 풀링
- 세션 관리

---

**데이터베이스 마이그레이션**
```bash
vessel db init       # Alembic 초기화
vessel db migrate    # 마이그레이션 생성
vessel db upgrade    # 마이그레이션 적용
```

---

### 7.2 메시징

**RabbitMQ/Kafka 통합**
```python
from vessel.messaging import MessageListener, RabbitTemplate

@MessageListener(queue="user.created")
def on_user_created(message: dict):
    # 메시지 처리
    pass

@Component
class UserService:
    rabbit: RabbitTemplate
    
    def create_user(self, user: User):
        # ...
        self.rabbit.send("user.created", user.to_dict())
```

**구현 계획:**
- `@MessageListener` 데코레이터
- 메시지 발행/구독
- 재시도 로직
- Dead letter queue

---

### 7.3 외부 서비스 통합

**HTTP Client**
```python
from vessel.http_client import HttpClient

@HttpClient(base_url="https://api.github.com")
class GitHubClient:
    def get_user(self, username: str) -> dict:
        """GET /users/{username}"""
        pass  # 자동 구현
```

**구현 계획:**
- `@HttpClient` 데코레이터
- 자동 직렬화/역직렬화
- 재시도 및 타임아웃
- Circuit breaker

---

# 테스트 현황

## 📊 현재 테스트 커버리지

**전체 테스트: 60개** ✅

| 테스트 파일 | 테스트 수 | 상태 |
|------------|----------|------|
| test_application.py | 12 | ✅ 통과 |
| test_component.py | 5 | ✅ 통과 |
| test_container.py | 4 | ✅ 통과 |
| test_dependency.py | 9 | ✅ 통과 |
| test_handler.py | 14 | ✅ 통과 |
| test_integration.py | 7 | ✅ 통과 |
| test_integration_advanced.py | 5 | ✅ 통과 |
| test_middleware_integration.py | 4 | ✅ 통과 |

**결과: 100% 통과 (60/60)** 🎉

## 테스트 커버리지 목표

**Phase 4 목표:**
- [ ] Constructor Injection 테스트 (+5)
- [ ] Lazy Initialization 테스트 (+3)
- [ ] Scope 테스트 (+5)
- [ ] Qualifier 테스트 (+3)
- [ ] Validation 테스트 (+5)
- [ ] File Upload 테스트 (+3)

**총 목표: 84개 테스트**

---

# 기술 스택

## 현재 사용 중

- **Python**: 3.12+
- **표준 라이브러리**: typing, inspect, importlib, wsgiref
- **테스트**: pytest, pytest-cov
- **문서**: Markdown

## 향후 도입 예정

- **Validation**: Pydantic
- **CLI**: Click / Typer
- **Hot Reload**: watchdog
- **Async**: asyncio, uvicorn
- **Cache**: Redis, aiocache
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Messaging**: pika (RabbitMQ), kafka-python
- **Logging**: structlog
- **Metrics**: prometheus-client

---

# 기여 가이드

## 개발 환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd vessel-framework

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -e .
pip install pytest pytest-cov

# 4. 테스트 실행
pytest

# 5. 커버리지 확인
pytest --cov=vessel --cov-report=html
```

## 커밋 메시지 규칙

```
<type>: <subject>

<body>
```

**Types:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `docs`: 문서 수정
- `chore`: 빌드, 설정 등

**예시:**
```
feat: Constructor Injection 지원 추가

- ComponentInitializer에서 __init__ 파라미터 분석
- Type hints 기반 자동 주입
- 기존 필드 주입과 병행 지원

Closes #123
```

---

# 라이선스

MIT License

---

# 연락처

- GitHub Issues: 버그 리포트 및 기능 요청
- Discussions: 질문 및 아이디어 공유

---

**마지막 업데이트: 2025-11-26**  
**버전: 0.1.0-alpha**  
**상태: 활발히 개발 중** 🚧
