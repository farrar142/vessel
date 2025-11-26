# Parameter Injection Module Reorganization

## 개요
`parameter_injection` 모듈을 `vessel/http`에서 `vessel/web/router`로 이동하여 더 논리적인 구조를 만들었습니다.

## 변경 사항

### 모듈 이동
- **Before**: `vessel/http/parameter_injection/`
- **After**: `vessel/web/router/parameter_injection/`

### 이유
1. **논리적 응집성**: parameter_injection은 router에서만 사용되므로 같은 위치에 있는 것이 자연스러움
2. **명확한 책임**: router와 관련된 모든 기능이 `vessel/web/router`에 모임
3. **더 나은 모듈 구조**: HTTP 프로토콜 레이어(`vessel/http`)와 웹 애플리케이션 레이어(`vessel/web`) 분리

## 새로운 구조

```
vessel/
├── http/                          # HTTP 프로토콜 레이어
│   ├── request.py                 # HttpRequest, HttpResponse
│   ├── file_upload.py             # 파일 업로드 처리
│   └── injection_types.py         # HttpHeader, HttpCookie 타입
│
└── web/                           # 웹 애플리케이션 레이어
    ├── auth/                      # 인증 시스템
    │   ├── middleware.py
    │   └── injector.py
    │
    └── router/                    # 라우팅 시스템
        ├── handler.py             # RouteHandler, Route
        │
        └── parameter_injection/   # 파라미터 주입 시스템
            ├── __init__.py
            ├── base.py            # ParameterInjector 인터페이스
            ├── registry.py        # ParameterInjectorRegistry
            ├── request_injector.py
            ├── header_injector.py
            ├── cookie_injector.py
            ├── file_injector.py
            ├── default_value_injector.py
            └── annotated_value_injector.py
```

## Import 경로 변경

### Parameter Injection 관련
```python
# Before
from vessel.http.parameter_injection import (
    ParameterInjector,
    ParameterInjectorRegistry,
    ValidationError,
)

# After
from vessel.web.router.parameter_injection import (
    ParameterInjector,
    ParameterInjectorRegistry,
    ValidationError,
)
```

### 하위 호환성
`vessel.validation`은 여전히 `ValidationError`를 re-export하므로 기존 코드는 동작합니다:

```python
# 여전히 동작함 (하위 호환성)
from vessel.validation import ValidationError
```

## 업데이트된 파일

**이동된 파일** (vessel/http/parameter_injection → vessel/web/router/parameter_injection):
- `base.py`
- `registry.py`
- `request_injector.py`
- `header_injector.py`
- `cookie_injector.py`
- `file_injector.py`
- `default_value_injector.py`
- `annotated_value_injector.py`
- `__init__.py`

**Import 경로 업데이트**:
- `vessel/validation.py`
- `vessel/web/request_handler.py`
- `vessel/web/router/handler.py`
- `vessel/web/auth/injector.py`
- 모든 parameter_injection 내부 파일들

## 레이어 분리

### vessel/http (HTTP Protocol Layer)
- HTTP 요청/응답 처리
- 파일 업로드
- HTTP 타입 정의 (HttpHeader, HttpCookie)
- **웹 프레임워크 독립적**

### vessel/web (Web Application Layer)
- 웹 애플리케이션 관리
- 라우팅 (router/)
- 파라미터 주입 (router/parameter_injection/)
- 인증 (auth/)
- 미들웨어 (middleware/)
- **vessel/http 위에 구축**

## 장점

1. **더 명확한 책임 분리**: HTTP vs Web Application 레이어
2. **논리적 응집성**: router와 parameter_injection이 함께 위치
3. **더 나은 탐색성**: 관련 기능을 찾기 쉬움
4. **확장성**: 각 레이어가 독립적으로 확장 가능

## 테스트 결과
✅ All 114 tests passing
