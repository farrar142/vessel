# Vessel Framework - TODO# Vessel Framework - TODO# Vessel Framework - TODO# Vessel Framework - TODO



> Last Updated: 2025-11-26 | Version: 0.1.0-alpha



---> Last Updated: 2025-11-26 | Version: 0.1.0-alpha



## 📊 현재 상태



- **85/85 테스트 통과** ✅---> 마지막 업데이트: 2025-11-26> Last Updated: 2025-11-26 | Version: 0.1.0-alpha

- **32개 파일** 체계적 구조

- **핵심 기능 완료** (DI, Web, Middleware, Validation, FileUpload)



---## 📊 현재 상태



## ✅ 완료된 작업



### Phase 1: DI 프레임워크- **73/73 테스트 통과** ✅------

- Container, DependencyGraph, ContainerManager

- @Component, @Configuration, @Factory- **31개 파일** 체계적 구조

- 타입 기반 자동 주입, 싱글톤 패턴

- **핵심 기능 완료** (DI, Web, Middleware, Validation)

### Phase 2: Web Framework

- HttpRequest/HttpResponse, RouteHandler

- Path Parameters, 자동 타입 변환

- @Controller, @Get, @Post, @Put, @Delete, @Patch---## ✅ 완료된 작업## ��� 현재 상태

- Middleware (MiddlewareChain, Early Return, DI 지원)

- Application (Facade), DevServer



### Phase 3: 코드 품질 개선## ✅ 완료된 작업

- SRP 적용: Application 4개 클래스 분리

- 구조 개편: vessel/ 전체 기능별 재구성

- di/core + di/utils 분리

### Phase 1: DI 프레임워크### Phase 1: 핵심 DI 프레임워크- **60/60 테스트 통과** ✅

### Phase 4: 핵심 기능 강화 (진행 중)

- **✅ Validation (완료)**- Container, DependencyGraph, ContainerManager

  - ParameterValidator: 타입 변환 및 검증

  - ValidationError: 400 에러 자동 반환- @Component, @Configuration, @Factory- **DI 시스템**: Container, DependencyGraph, ContainerManager- **30개 파일** 체계적 구조

  - 다중 에러 수집 및 상세 메시지

  - Query/Path/Body 파라미터 검증- 타입 기반 자동 주입, 싱글톤 패턴

  - **타입 힌트 강제**: 타입 없는 파라미터 → TypeError

  - 테스트: 13/13 통과- **데코레이터**: @Component, @Configuration, @Factory, @Controller- **핵심 기능 완료** (DI, Web, Middleware)



- **✅ File Upload (완료)**### Phase 2: Web Framework

  - **UploadedFile 클래스**: read(), save(), secure_filename()

  - **타입 힌트 기반 파일 주입**: - HttpRequest/HttpResponse, RouteHandler- **HTTP 매핑**: @Get, @Post, @Put, @Delete, @Patch (with @overload)

    - `file: UploadedFile` - 단일 파일

    - `files: list[UploadedFile]` - 다중 파일- Path Parameters, 자동 타입 변환

    - `file: Optional[UploadedFile]` - 선택적 파일

  - 단일/다중 파일 업로드- @Controller, @Get, @Post, @Put, @Delete, @Patch- **Interceptor**: HandlerContainer, @Transaction, @Logging---

  - 파일 검증 (크기, MIME 타입)

  - 파일명 sanitization (경로 순회 공격 방지)- Middleware (MiddlewareChain, Early Return, DI 지원)

  - 폼 데이터와 파일 혼합

  - 테스트: 12/12 통과- Application (Facade), DevServer



---



## 📁 프로젝트 구조### Phase 3: 코드 품질 개선### Phase 2: Web Framework## ✅ 완료된 작업



```- SRP 적용: Application 4개 클래스 분리

vessel/

├── di/- 구조 개편: vessel/ 전체 기능별 재구성- **HTTP 처리**: HttpRequest/HttpResponse, RouteHandler

│   ├── core/          # Container, ContainerManager, DependencyGraph

│   └── utils/         # Scanner, Collector, Initializer, Analyzer- di/core + di/utils 분리

├── decorators/

│   ├── di/            # @Component, @Configuration, @Factory- **Path Parameters**: `/users/{id}` 패턴, 자동 타입 변환### Phase 1: DI 프레임워크

│   ├── web/           # @Controller, HTTP mappings

│   └── handler/       # HandlerContainer, Interceptors### Phase 4: 핵심 기능 강화 (진행 중)

├── http/

│   ├── request.py     # HttpRequest, HttpResponse- **✅ Validation (완료)**- **Middleware**: MiddlewareChain, CorsMiddleware, LoggingMiddleware- Container, DependencyGraph, ContainerManager

│   ├── router.py      # RouteHandler

│   └── file_upload.py # UploadedFile ✨ NEW  - ParameterValidator: 타입 변환 및 검증

├── validation.py      # ParameterValidator, ValidationError

└── web/  - ValidationError: 400 에러 자동 반환- **Application**: Facade 패턴, 자동 초기화, DevServer- @Component, @Configuration, @Factory

    ├── application.py, initializer.py, request_handler.py, server.py

    └── middleware/    # MiddlewareChain, CorsMiddleware  - 다중 에러 수집 및 상세 메시지

```

  - Query/Path/Body 파라미터 검증- 타입 기반 자동 주입, 싱글톤 패턴

---

  - 테스트: 13/13 통과

## 🚀 향후 개발 계획

### Phase 3: 코드 품질 개선

### Phase 4 완료 목표 (남은 작업)

---

#### Web 기능

- [ ] **Static Files** - `app.serve_static("/static", "./public")`- **SRP 적용**: Application → 4개 클래스로 분리### Phase 2: Web Framework



#### Middleware## 📁 프로젝트 구조

- [ ] CompressionMiddleware (gzip)

- [ ] RateLimitMiddleware (rate limiting)  - Application (Facade)- HttpRequest/HttpResponse, RouteHandler

- [ ] SessionMiddleware (세션 관리)

- [ ] SecurityHeadersMiddleware```

- [ ] 우선순위 지정 기능

vessel/  - ApplicationInitializer- Path Parameters, 자동 타입 변환

---

├── di/

### Phase 5: 개발 편의성 (우선순위: 중간)

│   ├── core/          # Container, ContainerManager, DependencyGraph  - RequestHandler- @Controller, @Get, @Post, @Put, @Delete, @Patch

#### CLI

- [ ] `vessel create my-project` - 프로젝트 생성│   └── utils/         # Scanner, Collector, Initializer, Analyzer

- [ ] `vessel new controller UserController` - 코드 생성

├── decorators/  - DevServer- Middleware (MiddlewareChain, Early Return, DI 지원)

#### 개발 서버

- [ ] Hot Reload (파일 변경 감지)│   ├── di/            # @Component, @Configuration, @Factory

- [ ] 개선된 에러 페이지 (stacktrace)

- [ ] 컬러풀한 로깅│   ├── web/           # @Controller, HTTP mappings- Application (Facade), DevServer



#### 디버깅│   └── handler/       # HandlerContainer, Interceptors

- [ ] DI Inspector (컴포넌트 조회, 의존성 그래프)

- [ ] Health Check Endpoint├── http/              # HttpRequest, HttpResponse, RouteHandler- **디렉토리 구조화**:



#### 테스트├── validation.py      # ParameterValidator, ValidationError ✨ NEW

- [ ] `@WebTest` 데코레이터

- [ ] Test Client└── web/```### Phase 3: 코드 품질 개선

- [ ] Mock 컴포넌트 주입

    ├── application.py, initializer.py, request_handler.py, server.py

---

    └── middleware/    # MiddlewareChain, CorsMiddlewarevessel/- SRP 적용: Application 4개 클래스 분리

### Phase 6: 프로덕션 (우선순위: 낮음)

```

#### 성능

- [ ] **Async 지원** - `async def` 핸들러, ASGI├── di/core/         # Container, ContainerManager, DependencyGraph- 구조 개편: vessel/ 전체 기능별 재구성

- [ ] **Caching** - `@Cacheable`, Redis 통합

---

#### 보안

- [ ] **인증/인가** - JWT, `@Secured(roles=["admin"])`├── di/utils/        # Scanner, Collector, Initializer, Analyzer- di/core + di/utils 분리

- [ ] **CSRF** - 토큰 생성/검증

## 🚀 향후 개발 계획

#### 모니터링

- [ ] **Metrics** - Prometheus 연동├── decorators/di/   # @Component, @Configuration, @Factory

- [ ] **Logging** - structlog (JSON)

### Phase 4 완료 목표 (남은 작업)

---

├── decorators/web/  # @Controller, HTTP 매핑---

### Phase 7: 생태계 (우선순위: 낮음)

#### Web 기능

- [ ] **ORM** - SQLAlchemy, `@Repository`

- [ ] **Migration** - Alembic- [ ] **File Upload** - Multipart form data 파싱├── decorators/handler/  # HandlerContainer, Interceptors

- [ ] **Messaging** - RabbitMQ/Kafka, `@MessageListener`

- [ ] **HTTP Client** - `@HttpClient` 데코레이터- [ ] **Static Files** - `app.serve_static("/static", "./public")`



---├── http/            # HttpRequest, HttpResponse, RouteHandler## ��� 프로젝트 구조



## 📈 테스트 현황#### Middleware



| 파일 | 테스트 |- [ ] CompressionMiddleware (gzip)└── web/             # Application, Initializer, RequestHandler, Server

|------|--------|

| test_application.py | 12 ✅ |- [ ] RateLimitMiddleware (rate limiting)

| test_component.py | 5 ✅ |

| test_container.py | 4 ✅ |- [ ] SessionMiddleware (세션 관리)    └── middleware/  # MiddlewareChain, Builtins```

| test_dependency.py | 9 ✅ |

| test_file_upload.py | 12 ✅ |- [ ] SecurityHeadersMiddleware

| test_handler.py | 14 ✅ |

| test_integration.py | 7 ✅ |- [ ] 우선순위 지정 기능```vessel/

| test_integration_advanced.py | 5 ✅ |

| test_middleware_integration.py | 4 ✅ |

| test_validation.py | 13 ✅ |

| **총계** | **85 ✅** |---├── di/



---



## 🛠 기술 스택### Phase 5: 개발 편의성 (우선순위: 중간)---│   ├── core/          # Container, ContainerManager, DependencyGraph



**현재:** Python 3.12+, pytest



**향후:** Click, watchdog, asyncio, Redis, SQLAlchemy#### CLI│   └── utils/         # Scanner, Collector, Initializer, Analyzer



---- [ ] `vessel create my-project` - 프로젝트 생성



## 🚨 개발 제약사항- [ ] `vessel new controller UserController` - 코드 생성## 📊 현재 상태├── decorators/



- **DI 기능 개발 안함**: Constructor Injection, Lazy, Scope, Qualifier (!!절대 관련 기능 개발 안할것임)

- **템플릿 엔진 지원 안함**: Jinja2 통합 안함 (!!템플릿 엔진 지원 안할것임)

#### 개발 서버│   ├── di/            # @Component, @Configuration, @Factory

---

- [ ] Hot Reload (파일 변경 감지)

## 💡 타입 안정성 원칙

- [ ] 개선된 에러 페이지 (stacktrace)**테스트**: 60/60 통과 ✅  │   ├── web/           # @Controller, HTTP mappings

**강한 타입 기반 프레임워크**: 모든 핸들러 파라미터는 타입 힌트 필수

- [ ] 컬러풀한 로깅

```python

# ✅ 올바른 사용**파일 수**: 30개  │   └── handler/       # HandlerContainer, Interceptors

@Post("/upload")

def upload_file(self, file: UploadedFile, title: str) -> dict:#### 디버깅

    return {"filename": file.filename}

- [ ] DI Inspector (컴포넌트 조회, 의존성 그래프)**라인 수**: ~3,000줄  ├── http/              # HttpRequest, HttpResponse, RouteHandler

# ❌ 에러 발생

@Post("/upload")- [ ] Health Check Endpoint

def upload_file(self, file) -> dict:  # TypeError: 타입 힌트 없음

    return {"filename": file.filename}**문서**: STRUCTURE.md, RESTRUCTURE_PLAN.md└── web/

```

#### 테스트

---

- [ ] `@WebTest` 데코레이터    ├── application.py, initializer.py, request_handler.py, server.py

## 📝 빠른 시작

- [ ] Test Client

```bash

# 설치- [ ] Mock 컴포넌트 주입---    └── middleware/    # MiddlewareChain, CorsMiddleware

python -m venv venv

source venv/bin/activate

pip install pytest

---```

# 테스트

pytest

```

### Phase 6: 프로덕션 (우선순위: 낮음)## 🚀 향후 개발 계획

---



## 💡 커밋 규칙

#### 성능---

`<type>: <subject>`

- [ ] **Async 지원** - `async def` 핸들러, ASGI

**Types:** feat, fix, refactor, test, docs, chore

- [ ] **Caching** - `@Cacheable`, Redis 통합### Phase 4: 핵심 기능 강화 (우선순위: 높음)

---



**버전**: 0.1.0-alpha  

**상태**: 활발히 개발 중 🚧  #### 보안## ��� 향후 개발 계획

**라이선스**: MIT

- [ ] **인증/인가** - JWT, `@Secured(roles=["admin"])`

- [ ] **CSRF** - 토큰 생성/검증#### DI 개선 - !!절대 관련 기능 개발 안할것임



#### 모니터링- [ ] **Constructor Injection** - 생성자 파라미터 자동 주입### Phase 4: 핵심 기능 강화 (우선순위: 높음)

- [ ] **Metrics** - Prometheus 연동

- [ ] **Logging** - structlog (JSON)- [ ] **Lazy Initialization** - `@Component(lazy=True)`



---- [ ] **Scope 확장** - Prototype, Request scope**DI 개선**



### Phase 7: 생태계 (우선순위: 낮음)- [ ] **Qualifier** - `@Inject(name="mysql_db")`로 빈 구분- [ ] Constructor Injection



- [ ] **ORM** - SQLAlchemy, `@Repository`- [ ] Lazy Initialization

- [ ] **Migration** - Alembic

- [ ] **Messaging** - RabbitMQ/Kafka, `@MessageListener`#### Web 기능- [ ] Scope 확장 (Prototype, Request)

- [ ] **HTTP Client** - `@HttpClient` 데코레이터

- [ ] **Validation** - Pydantic 통합, 자동 검증- [ ] Qualifier 지원

---

- [ ] **File Upload** - Multipart form data 파싱

## 📈 테스트 현황

- [ ] **Static Files** - `app.serve_static("/static", "./public")`**Web 기능**

| 파일 | 테스트 |

|------|--------|- [ ] **Template Engine** - Jinja2 통합- [ ] 요청 바디 검증 (Pydantic) - !!템플릿 엔진 지원 안할것임.

| test_application.py | 12 ✅ |

| test_component.py | 5 ✅ |- [ ] 파일 업로드

| test_container.py | 4 ✅ |

| test_dependency.py | 9 ✅ |#### Middleware- [ ] 정적 파일 서빙

| test_handler.py | 14 ✅ |

| test_integration.py | 7 ✅ |- [ ] CompressionMiddleware (gzip)- [ ] 템플릿 엔진 (Jinja2)

| test_integration_advanced.py | 5 ✅ |

| test_middleware_integration.py | 4 ✅ |- [ ] RateLimitMiddleware (rate limiting)

| test_validation.py | 13 ✅ |

| **총계** | **73 ✅** |- [ ] SessionMiddleware (세션 관리)**Middleware**



---- [ ] SecurityHeadersMiddleware- [ ] CompressionMiddleware



## 🛠 기술 스택- [ ] 우선순위 지정 기능- [ ] RateLimitMiddleware



**현재:** Python 3.12+, pytest- [ ] SessionMiddleware



**향후:** Pydantic, Click, watchdog, asyncio, Redis, SQLAlchemy---- [ ] SecurityHeadersMiddleware



---



## 🚨 개발 제약사항### Phase 5: 개발 편의성 (우선순위: 중간)---



- **DI 기능 개발 안함**: Constructor Injection, Lazy, Scope, Qualifier (!!절대 관련 기능 개발 안할것임)

- **템플릿 엔진 지원 안함**: Jinja2 통합 안함 (!!템플릿 엔진 지원 안할것임)

#### CLI### Phase 5: 개발 편의성 (우선순위: 중간)

---

- [ ] `vessel create my-project` - 프로젝트 생성

## 📝 빠른 시작

- [ ] `vessel new controller UserController` - 코드 생성- [ ] CLI 도구

```bash

# 설치- [ ] Hot Reload

python -m venv venv

source venv/bin/activate#### 개발 서버- [ ] 에러 페이지 개선

pip install pytest

- [ ] Hot Reload (파일 변경 감지)- [ ] DI Inspector

# 테스트

pytest- [ ] 개선된 에러 페이지 (stacktrace)- [ ] Health Check

```

- [ ] 컬러풀한 로깅- [ ] 테스트 유틸리티

---



## 💡 커밋 규칙

#### 디버깅---

`<type>: <subject>`

- [ ] DI Inspector (컴포넌트 조회, 의존성 그래프)

**Types:** feat, fix, refactor, test, docs, chore

- [ ] Health Check Endpoint### Phase 6: 프로덕션 준비 (우선순위: 낮음)

---



**버전**: 0.1.0-alpha  

**상태**: 활발히 개발 중 🚧  #### 테스트**성능**

**라이선스**: MIT

- [ ] `@WebTest` 데코레이터- [ ] 비동기 지원 (asyncio, uvicorn)

- [ ] Test Client- [ ] 캐싱 (Redis)

- [ ] Mock 컴포넌트 주입

**보안**

---- [ ] 인증/인가 (JWT, @Secured)

- [ ] CSRF 보호

### Phase 6: 프로덕션 (우선순위: 낮음)

**모니터링**

#### 성능- [ ] 메트릭 (Prometheus)

- [ ] **Async 지원** - `async def` 핸들러, ASGI- [ ] 로깅 (structlog)

- [ ] **Caching** - `@Cacheable`, Redis 통합

---

#### 보안

- [ ] **인증/인가** - JWT, `@Secured(roles=["admin"])`### Phase 7: 생태계 확장 (우선순위: 낮음)

- [ ] **CSRF** - 토큰 생성/검증

- [ ] ORM 통합 (SQLAlchemy, @Repository)

#### 모니터링- [ ] 마이그레이션 (Alembic)

- [ ] **Metrics** - Prometheus 연동- [ ] 메시징 (RabbitMQ/Kafka)

- [ ] **Logging** - structlog (JSON)- [ ] HTTP Client (@HttpClient)



------



### Phase 7: 생태계 (우선순위: 낮음)## ��� 테스트 현황



- [ ] **ORM** - SQLAlchemy, `@Repository`| 파일 | 테스트 |

- [ ] **Migration** - Alembic|------|--------|

- [ ] **Messaging** - RabbitMQ/Kafka, `@MessageListener`| test_application.py | 12 ✅ |

- [ ] **HTTP Client** - `@HttpClient` 데코레이터| test_component.py | 5 ✅ |

| test_container.py | 4 ✅ |

---| test_dependency.py | 9 ✅ |

| test_handler.py | 14 ✅ |

## 📈 테스트 목표| test_integration.py | 7 ✅ |

| test_integration_advanced.py | 5 ✅ |

| Phase | 현재 | 목표 || test_middleware_integration.py | 4 ✅ |

|-------|------|------|| **총계** | **60 ✅** |

| Phase 3 | 60 | 60 ✅ |

| Phase 4 | 60 | 84 |---

| Phase 5 | 84 | 100 |

| Phase 6 | 100 | 120 |## ��� 기술 스택



---**현재:** Python 3.12+, pytest



## 🛠 기술 스택**향후:** Pydantic, Click, watchdog, asyncio, Redis, SQLAlchemy



**현재**:---

- Python 3.12+

- 표준 라이브러리 (typing, inspect, wsgiref)## ��� 빠른 시작

- pytest

```bash

**향후**:# 설치

- Pydantic, Click/Typer, watchdogpython -m venv venv

- asyncio, uvicorn, Redissource venv/bin/activate

- SQLAlchemy, Alembicpip install pytest

- structlog, prometheus-client

# 테스트

---pytest

```

## 📝 개발 가이드

---

### 환경 설정

```bash## ��� 커밋 규칙

python -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate`<type>: <subject>`

pip install pytest pytest-cov

pytest**Types:** feat, fix, refactor, test, docs, chore

```

---

### 커밋 메시지

```**상태: 활발히 개발 중** ���

<type>: <subject>

<body>
```

**Types**: feat, fix, refactor, test, docs, chore

**예시**:
```
feat: Constructor Injection 지원 추가

- ComponentInitializer에서 __init__ 파라미터 분석
- Type hints 기반 자동 주입
```

---

## 📂 주요 파일

| 파일 | 설명 |
|------|------|
| `vessel/di/core/container_manager.py` | DI 메인 |
| `vessel/web/application.py` | Application Facade |
| `vessel/http/router.py` | 라우팅 |
| `vessel/web/middleware/chain.py` | 미들웨어 체인 |
| `tests/test_*.py` | 60개 테스트 |

---

## 🎯 다음 작업 (Phase 4 시작)

1. **Constructor Injection** 구현
   - `ComponentInitializer` 수정
   - `__init__` 파라미터 분석 추가
   - 테스트 5개 작성

2. **Lazy Initialization** 구현
   - Proxy 패턴 적용
   - `@Component(lazy=True)` 옵션
   - 테스트 3개 작성

3. **Validation** 구현
   - Pydantic 통합
   - 타입 힌트 기반 검증
   - 테스트 5개 작성

---

**버전**: 0.1.0-alpha  
**상태**: 활발히 개발 중 🚧  
**라이선스**: MIT
