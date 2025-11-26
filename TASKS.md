# Vessel Framework - 개발 작업 목록

> 최종 업데이트: 2025-11-26 | 버전: 0.1.0-alpha

---

## 📊 현재 상태

- **104/104 테스트 통과** ✅
- **39개 파일** - 잘 구조화된 아키텍처
- **완료된 핵심 기능**: DI, Web, Middleware, Validation, FileUpload, HTTP Injection, Registry Pattern

---

## ✅ 완료된 단계

### Phase 1: 핵심 DI 프레임워크 ✅
- Container, DependencyGraph, ContainerManager
- @Component, @Configuration, @Factory
- 타입 기반 의존성 주입
- 싱글톤 패턴

### Phase 2: 웹 프레임워크 ✅
- HttpRequest/HttpResponse, RouteHandler
- 자동 타입 변환을 포함한 경로 매개변수
- @Controller, @Get, @Post, @Put, @Delete, @Patch
- 조기 반환을 지원하는 미들웨어 체인
- Application 파사드, DevServer

### Phase 3: 코드 품질 ✅
- SRP: Application을 4개 클래스로 분리
- 기능별로 vessel/ 재구조화
- di/core와 di/utils 분리

### Phase 4: 핵심 기능 ✅
- **✅ Validation** (13 tests)
  - ParameterValidator: 타입 변환 & 검증
  - ValidationError: 자동 400 응답
  - 상세한 메시지와 함께 다중 오류 수집
  - Query/Path/Body 매개변수 검증
  - **강력한 타입 지정**: 타입 힌트 누락 → 오류
  
- **✅ File Upload** (12 tests)
  - UploadedFile 클래스: read(), save(), secure_filename()
  - **타입 기반 주입**: file: UploadedFile
  - 지원: UploadedFile, Optional[UploadedFile], list[UploadedFile]
  - 파일 크기 검증, MIME 타입 확인
  - 파일명 정제 (경로 탐색 공격 방지)
  - **강력한 타입 지정**: 파일 매개변수는 명시적 타입 힌트 필요

- **✅ HTTP Injection** (19 tests)
  - HttpHeader, HttpCookie 타입 마커
  - **3가지 문법 지원**:
    - 자동 변환: `user_agent: HttpHeader`
    - 명시적 호출: `agent: HttpHeader = HttpHeader("User-Agent")`
    - 브래킷 문법: `agent: HttpHeader["User-Agent"]`
  - Optional 매개변수 지원
  - Annotated 타입 지원

### Phase 5: 아키텍처 개선 ✅
- **✅ Registry Pattern** (리팩토링)
  - 모듈식 파라미터 주입 시스템
  - router.py 간소화 (265+ 라인 → 31 라인)
  - 개별 Injector 구현:
    * HttpRequestInjector (우선순위: 0)
    * HttpHeaderInjector (우선순위: 100)
    * HttpCookieInjector (우선순위: 101)
    * FileInjector (우선순위: 200)
  - **아키텍처 이점**:
    - 단일 책임: 각 injector는 하나의 타입 처리
    - 확장성: ParameterInjector 구현으로 새 타입 추가
    - 테스트 가능성: 각 injector를 독립적으로 테스트
    - 유지보수성: 우선순위 시스템으로 명확한 관심사 분리

---

## 📁 프로젝트 구조

```
vessel/
├── di/
│   ├── core/           # Container, ContainerManager, DependencyGraph
│   └── utils/          # Scanner, Collector, Initializer, Analyzer
├── decorators/
│   ├── di/             # @Component, @Configuration, @Factory
│   ├── web/            # @Controller, HTTP mappings
│   └── handler/        # HandlerContainer, Interceptors
├── http/
│   ├── request.py           # HttpRequest, HttpResponse
│   ├── router.py            # RouteHandler (리팩토링됨)
│   ├── file_upload.py       # UploadedFile
│   ├── injection_types.py   # HttpHeader, HttpCookie ✨ NEW
│   ├── parameter_injection/ # Registry 패턴 ✨ NEW
│   │   ├── base.py          # ParameterInjector, InjectionContext
│   │   ├── registry.py      # ParameterInjectorRegistry
│   │   ├── request_injector.py
│   │   ├── header_injector.py
│   │   ├── cookie_injector.py
│   │   └── file_injector.py
│   └── validation.py        # ParameterValidator, ValidationError
└── web/
    ├── application.py, initializer.py, request_handler.py, server.py
    └── middleware/          # MiddlewareChain, CorsMiddleware
```

---

## 🚀 다음 작업

### Phase 6: 개발자 경험

#### CLI 도구
- [ ] `vessel create my-project` - 프로젝트 스캐폴딩
- [ ] `vessel new controller UserController` - 코드 생성

#### Dev Server
- [ ] **Hot Reload** - 파일 변경 감지
- [ ] **향상된 오류 페이지** - 구문 강조가 있는 스택 추적
- [ ] **컬러풀한 로깅** - 개선된 로그 출력

#### 디버깅
- [ ] **DI Inspector** - 컴포넌트 그래프 시각화
- [ ] **Health Check Endpoint** - `/health`

#### 테스팅
- [ ] **@WebTest 데코레이터** - 테스트 유틸리티
- [ ] **Test Client** - 테스트용 HTTP 클라이언트
- [ ] **Mock Components** - 의존성 모킹

---

### Phase 7: 프로덕션 준비

#### 성능
- [ ] **비동기 지원** - `async def` 핸들러, ASGI
- [ ] **캐싱** - `@Cacheable`, Redis 통합

#### 보안
- [ ] **인증/권한** - JWT, `@Secured(roles=["admin"])`
- [ ] **CSRF 보호** - 토큰 생성/검증

#### 모니터링
- [ ] **메트릭** - Prometheus 통합
- [ ] **구조화된 로깅** - structlog (JSON)

---

### Phase 8: 생태계

- [ ] **ORM 통합** - SQLAlchemy, `@Repository`
- [ ] **데이터베이스 마이그레이션** - Alembic
- [ ] **메시징** - RabbitMQ/Kafka, `@MessageListener`
- [ ] **HTTP Client** - `@HttpClient` 데코레이터

---

### Phase 9: 웹 기능 완성

#### 정적 파일 & 스트리밍
- [ ] **Static Files** - `app.serve_static("/static", "./public")`
- [ ] **Response Streaming** - 대용량 파일 다운로드

#### 추가 미들웨어
- [ ] **CompressionMiddleware** - gzip 압축
- [ ] **RateLimitMiddleware** - 속도 제한
- [ ] **SessionMiddleware** - 세션 관리
- [ ] **SecurityHeadersMiddleware** - 보안 헤더
- [ ] **Middleware Priority** - 순서 제어

---

## 📈 테스트 커버리지

| 파일 | 테스트 | 상태 |
|------|-------|--------|
| test_application.py | 12 | ✅ |
| test_component.py | 5 | ✅ |
| test_container.py | 4 | ✅ |
| test_dependency.py | 9 | ✅ |
| test_handler.py | 14 | ✅ |
| test_integration.py | 7 | ✅ |
| test_integration_advanced.py | 5 | ✅ |
| test_middleware_integration.py | 4 | ✅ |
| test_validation.py | 13 | ✅ |
| test_file_upload.py | 12 | ✅ |
| test_http_injection.py | 19 | ✅ |
| **합계** | **104** | **✅** |

---

## 🛠 기술 스택

**현재**: Python 3.12+, pytest

**향후**: Click, watchdog, asyncio, Redis, SQLAlchemy

---

## 🚨 설계 제약사항

- **❌ 생성자 주입 없음**: 필드 주입만 사용 (명시적 설계 선택)
- **❌ 지연 초기화 없음**: 컴포넌트는 즉시 초기화
- **❌ 스코프 확장 없음**: 싱글톤만 지원 (prototype/request 스코프 없음)
- **❌ Qualifier 지원 없음**: 타입당 단일 빈
- **❌ 템플릿 엔진 없음**: API 중심 프레임워크 (Jinja2 없음)
- **✅ 강력한 타입 지정**: 모든 매개변수는 타입 힌트 필수 (self/HttpRequest 제외)

---

## 💡 주요 설계 원칙

### 타입 안정성 우선
```python
# ❌ 나쁨 - 타입 힌트 없음
def upload(self, file):  # 오류: 타입 힌트 누락

# ✅ 좋음 - 명시적 타입
def upload(self, file: UploadedFile):  # OK
```

### 명시적 > 암시적
```python
# 파일 업로드는 명시적 타입 어노테이션 필요
def upload(self, file: UploadedFile):  # 타입 힌트가 있어야만 작동
    return {"name": file.filename}
```

### 관례 우선 설정
```python
@Controller("/api")
class UserController:
    @Get("/users/{id}")
    def get_user(self, id: int) -> dict:  # 경로 매개변수 자동 주입
        return {"id": id}
```

### Registry 패턴 (새로운 원칙)
```python
# 각 Injector는 단일 책임을 가짐
class HttpHeaderInjector(ParameterInjector):
    def can_inject(self, context) -> bool:
        # HttpHeader 타입인지 확인
        
    def inject(self, context) -> Tuple[Any, bool]:
        # 헤더 값 주입
        
    @property
    def priority(self) -> int:
        return 100  # 실행 우선순위
```

---

## 📝 빠른 시작

```bash
# 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pytest

# 테스트
pytest -v

# 실행
python -m vessel.web.server
```

---

## 💻 사용 예제

### 파일 업로드
```python
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Post, Get
from vessel.http.file_upload import UploadedFile
from typing import Optional

@Controller("/api")
class FileController:
    @Post("/upload")
    def upload(self, file: UploadedFile, title: str, description: str = "") -> dict:
        # 검증은 자동으로 이루어짐
        # file은 UploadedFile임이 보장됨
        # title은 필수 문자열
        # description은 기본값이 있는 선택적 매개변수
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            return {"error": "파일이 너무 큽니다"}
        
        safe_name = file.secure_filename()
        file.save(f"./uploads/{safe_name}")
        
        return {
            "filename": safe_name,
            "size": file.size,
            "title": title
        }
    
    @Get("/files")
    def list_files(self, page: int = 1, limit: int = 10) -> dict:
        # 쿼리 매개변수 자동 검증 및 변환
        return {"page": page, "limit": limit}
```

### HTTP 헤더/쿠키 주입
```python
from vessel.http.injection_types import HttpHeader, HttpCookie
from typing import Optional

@Controller("/api")
class AuthController:
    @Get("/profile")
    def get_profile(
        self,
        user_agent: HttpHeader,  # User-Agent 헤더 자동 변환
        access_token: HttpCookie,  # access_token 쿠키
        auth: HttpHeader = HttpHeader("Authorization"),  # 명시적 이름
        session: Optional[HttpCookie] = None  # 선택적 쿠키
    ) -> dict:
        return {
            "user_agent": user_agent,
            "token": access_token,
            "auth": auth,
            "has_session": session is not None
        }
    
    @Get("/info")
    def get_info(
        self,
        agent: HttpHeader["User-Agent"],  # 브래킷 문법
        sid: HttpCookie["session_id"]  # 브래킷 문법
    ) -> dict:
        return {"agent": agent, "session_id": sid}
```

---

## 🎯 커밋 컨벤션

```
<type>: <subject>

Types: feat, fix, refactor, test, docs, chore
```

**예제**:
```
feat: 타입 기반 주입을 사용한 파일 업로드 지원 추가

- UploadedFile 클래스 구현
- 타입 힌트 검증 추가
- Optional[UploadedFile] 및 list[UploadedFile] 지원
```

---

**버전**: 0.1.0-alpha  
**상태**: 활발한 개발 중 🚧  
**라이선스**: MIT
