# HTTP Module Reorganization

## 개요
HTTP 관련 모듈을 `vessel/http`에서 `vessel/web/http`로 이동하여 웹 애플리케이션 레이어로 통합했습니다.

## 변경 사항

### 모듈 이동
- **Before**: `vessel/http/`
- **After**: `vessel/web/http/`

### 이동된 파일
- `request.py` - HttpRequest, HttpResponse 클래스
- `file_upload.py` - 파일 업로드 처리
- `injection_types.py` - HttpHeader, HttpCookie 타입
- `__init__.py` - 모듈 진입점

## 이유

1. **논리적 위치**: HTTP는 웹 애플리케이션의 일부이므로 `vessel/web` 아래에 위치하는 것이 자연스러움
2. **일관된 구조**: router, auth, middleware 등 모든 웹 관련 기능이 `vessel/web` 아래에 모임
3. **명확한 레이어**: DI 컨테이너(`vessel/di`)와 웹 애플리케이션(`vessel/web`)으로 명확히 분리

## 새로운 구조

```
vessel/
├── di/                      # 의존성 주입 레이어
│   ├── core/
│   └── decorators/
│
└── web/                     # 웹 애플리케이션 레이어
    ├── http/                # HTTP 프로토콜
    │   ├── request.py       # HttpRequest, HttpResponse
    │   ├── file_upload.py   # 파일 업로드
    │   ├── injection_types.py  # HTTP 타입
    │   └── __init__.py
    │
    ├── router/              # 라우팅
    │   ├── handler.py
    │   └── parameter_injection/
    │
    ├── auth/                # 인증
    │   ├── middleware.py
    │   └── injector.py
    │
    ├── middleware/          # 미들웨어
    │   ├── chain.py
    │   └── builtins.py
    │
    ├── application.py       # Application 클래스
    └── server.py            # 개발 서버
```

## Import 경로 변경

### HttpRequest, HttpResponse
```python
# Before
from vessel.http.request import HttpRequest, HttpResponse

# After
from vessel.web.http.request import HttpRequest, HttpResponse
```

### File Upload
```python
# Before
from vessel.http.file_upload import UploadedFile

# After
from vessel.web.http.file_upload import UploadedFile
```

### HTTP Types
```python
# Before
from vessel.http.injection_types import HttpHeader, HttpCookie

# After
from vessel.web.http.injection_types import HttpHeader, HttpCookie
```

### 편의 Import (여전히 동작)
```python
# vessel/__init__.py에서 re-export
from vessel import HttpRequest, HttpResponse, HttpHeader, HttpCookie
```

## 업데이트된 파일

**Core 파일들**:
- `vessel/__init__.py` - import 경로 업데이트
- `vessel/web/http/__init__.py` - 새 위치

**Web 레이어**:
- `vessel/web/application.py`
- `vessel/web/request_handler.py`
- `vessel/web/server.py`
- `vessel/web/middleware/chain.py`
- `vessel/web/middleware/builtins.py`
- `vessel/web/auth/middleware.py`

**Router & Parameter Injection**:
- `vessel/web/router/handler.py`
- `vessel/web/router/parameter_injection/base.py`
- `vessel/web/router/parameter_injection/registry.py`
- `vessel/web/router/parameter_injection/request_injector.py`
- `vessel/web/router/parameter_injection/header_injector.py`
- `vessel/web/router/parameter_injection/cookie_injector.py`
- `vessel/web/router/parameter_injection/file_injector.py`

**Tests**:
- 모든 테스트 파일의 import 경로 업데이트

## 레이어 구조

### vessel/di (Dependency Injection Layer)
- 의존성 주입 컨테이너
- 컴포넌트 스캔 및 관리
- 데코레이터 (@Component, @Configuration, @Factory)
- **웹 프레임워크 독립적**

### vessel/web (Web Application Layer)
- HTTP 프로토콜 처리 (http/)
- 라우팅 시스템 (router/)
- 파라미터 주입 (router/parameter_injection/)
- 인증 시스템 (auth/)
- 미들웨어 (middleware/)
- 애플리케이션 관리 (application.py)
- **vessel/di 위에 구축**

## 장점

1. **명확한 레이어 분리**: DI vs Web Application
2. **논리적 응집성**: 모든 웹 관련 기능이 한 곳에
3. **더 나은 탐색성**: 관련 기능을 찾기 쉬움
4. **확장성**: 각 레이어가 독립적으로 확장 가능
5. **일관성**: 모든 웹 컴포넌트가 vessel/web 아래에 위치

## 테스트 결과
✅ All 114 tests passing in 1.19s
