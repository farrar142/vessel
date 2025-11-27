# Vessel Framework - 작업 현황

> 최종 업데이트: 2025-11-26  
> 버전: 0.1.0-alpha  
> 테스트: **114/114 통과** ✅

---

## � 문서

### 사용 가이드 (docs/)

1. **[01_dependency_injection.md](docs/01_dependency_injection.md)** - DI 시스템
   - @Component, @Configuration, @Factory
   - 필드 주입 (Field Injection)
   - 의존성 그래프 및 순환 감지

2. **[02_web_framework.md](docs/02_web_framework.md)** - 웹 프레임워크
   - @Controller, HTTP 메서드 데코레이터
   - 경로/쿼리 파라미터, 요청 본문
   - 타입 변환 및 검증

3. **[03_file_upload.md](docs/03_file_upload.md)** - 파일 업로드
   - UploadedFile 클래스
   - 단일/다중 파일 업로드
   - 파일 검증 (크기, MIME, 확장자)

4. **[04_http_injection.md](docs/04_http_injection.md)** - HTTP 주입
   - HttpHeader, HttpCookie 타입
   - 자동 이름 변환
   - 브래킷 문법

5. **[05_authentication.md](docs/05_authentication.md)** - 인증 시스템
   - Authenticator 인터페이스
   - AuthMiddleware, Authentication
   - JWT, API Key 예제

6. **[06_middleware.md](docs/06_middleware.md)** - 미들웨어
   - Middleware 인터페이스
   - 조기 반환 (Early Return)
   - CORS, Logging, Timing 예제

---

## 📊 현재 상태

- **114/114 테스트 통과** ✅
- **완료된 핵심 기능**: DI, Web Framework, Middleware, Authentication, File Upload, HTTP Injection, Parameter Injection

---

## 프로젝트 구조

```
vessel/
├── di/                          # 의존성 주입 레이어
│   ├── core/                    # Container, DependencyGraph, ContainerManager
│   └── decorators/              # @Component, @Configuration, @Factory
│
├── decorators/                  # 전역 데코레이터
│   ├── di/                      # DI 데코레이터
│   ├── web/                     # @Controller, @Get, @Post, ...
│   └── handler/                 # HandlerContainer
│
└── web/                         # 웹 애플리케이션 레이어
    ├── http/                    # HTTP 프로토콜
    │   ├── request.py           # HttpRequest, HttpResponse
    │   ├── file_upload.py       # UploadedFile
    │   └── injection_types.py   # HttpHeader, HttpCookie
    │
    ├── router/                  # 라우팅 시스템
    │   ├── handler.py           # RouteHandler, Route
    │   └── parameter_injection/ # 파라미터 주입 시스템 (9개 파일)
    │       ├── base.py
    │       ├── registry.py
    │       ├── default_value_injector.py
    │       ├── request_injector.py
    │       ├── header_injector.py
    │       ├── cookie_injector.py
    │       ├── file_injector.py
    │       └── annotated_value_injector.py
    │
    ├── auth/                    # 인증 시스템
    │   ├── middleware.py        # AuthMiddleware
    │   └── injector.py          # AuthenticationInjector
    │
    ├── middleware/              # 미들웨어 체인
    │   ├── chain.py
    │   └── builtins.py
    │
    ├── application.py           # Application 클래스
    ├── request_handler.py       # RequestHandler
    └── server.py                # DevServer
```

---

## 핵심 기능

### ✅ 완료됨

**DI (Dependency Injection)**
- @Component, @Configuration, @Factory
- 필드 주입 (Field Injection) - 타입 힌트 기반
- 의존성 그래프, 순환 감지
- 자동 싱글톤 관리

**Web Framework**
- @Controller, @Get, @Post, @Put, @Delete, @Patch
- 경로/쿼리 파라미터 (자동 타입 변환)
- Request Body (dict, dataclass)
- HttpRequest, HttpResponse

**File Upload**
- UploadedFile 클래스 (read, save, secure_filename)
- 단일/다중 파일 업로드 (List[UploadedFile])
- 크기/MIME/확장자 검증

**HTTP Injection**
- HttpHeader, HttpCookie 타입 주입
- 자동 이름 변환 (snake_case → Title-Case)
- 브래킷 문법 (`HttpHeader["User-Agent"]`)

**Authentication**
- Authenticator 인터페이스
- AuthMiddleware, Authentication 객체
- 여러 Authenticator 등록 가능
- 자동 401 응답

**Middleware**
- Middleware 인터페이스
- 조기 반환 (Early Return)
- 의존성 주입 지원
- 자동 감지 (@Component)

**Parameter Injection System**
- Registry 패턴
- 우선순위 시스템
- 확장 가능한 Injector 구조
- ValidationError 자동 처리

---

## 🚀 로드맵

### 다음 단계

1. **비동기 지원** - async/await, ASGI
2. **ORM 통합** - SQLAlchemy
3. **테스트 유틸리티** - @WebTest, TestClient
4. **프로덕션 기능** - Logging, Metrics, Health Check
5. **문서 개선** - 더 많은 예제, 튜토리얼

---

## 테스트 현황

**총 114개 테스트 통과** ✅

| 테스트 파일 | 테스트 수 |
|-----------|---------|
| test_application.py | 12 |
| test_authentication.py | 8 |
| test_component.py | 5 |
| test_container.py | 4 |
| test_dependency.py | 9 |
| test_file_upload.py | 17 |
| test_handler.py | 14 |
| test_http_injection.py | 16 |
| test_integration.py | 7 |
| test_integration_advanced.py | 5 |
| test_middleware_integration.py | 4 |
| test_validation.py | 13 |

---

## 설계 원칙

### ✅ 지원하는 기능

- **필드 주입** - 타입 힌트 기반 의존성 주입
- **싱글톤** - 모든 컴포넌트는 싱글톤으로 관리
- **자동 스캔** - @Component, @Controller 자동 감지
- **타입 안전** - 타입 힌트 필수, 자동 변환
- **미들웨어 체인** - 요청/응답 전후 처리
- **파라미터 주입** - Query, Path, Body, Header, Cookie, File
- **인증 시스템** - Authenticator 인터페이스 기반

### ❌ 지원하지 않는 기능

- **생성자 주입** - 필드 주입만 지원 (의도적 설계)
- **Optional 의존성** - 모든 의존성은 필수
- **Prototype 스코프** - 싱글톤만 지원
- **Qualifier** - 타입당 하나의 빈만 가능
- **템플릿 엔진** - API 중심 (Jinja2 미지원)
- **비동기** - 동기 방식만 지원 (추후 계획)
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
        auth: HttpHeader["Authorization"],  # 브래킷 문법으로 명시적 이름 지정
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
