# Vessel Framework - 새로운 구조

## 📁 디렉토리 구조

```
vessel/
├── __init__.py                          # 메인 export
│
├── di/                                  # ✨ DI (Dependency Injection) 핵심
│   ├── core/                            # DI 코어 모듈
│   │   ├── __init__.py
│   │   ├── container.py                 # Container 클래스
│   │   ├── container_manager.py         # ContainerManager (Orchestrator)
│   │   └── dependency.py                # DependencyGraph (Topological Sort)
│   │
│   └── utils/                           # DI 유틸리티 (단일 책임 분리)
│       ├── __init__.py
│       ├── package_scanner.py           # 패키지 스캐닝
│       ├── container_collector.py       # 컨테이너 수집
│       ├── dependency_analyzer.py       # 의존성 분석
│       ├── component_initializer.py     # 컴포넌트 초기화
│       └── interceptor_resolver.py      # 인터셉터 해결
│
├── decorators/                          # 🎨 데코레이터
│   ├── __init__.py
│   │
│   ├── di/                              # DI 관련 데코레이터
│   │   ├── __init__.py
│   │   ├── component.py                 # @Component
│   │   ├── configuration.py             # @Configuration
│   │   └── factory.py                   # @Factory
│   │
│   ├── web/                             # Web 관련 데코레이터
│   │   ├── __init__.py
│   │   ├── controller.py                # @Controller, @RequestMapping
│   │   └── mapping.py                   # @Get, @Post, @Put, @Delete, @Patch
│   │
│   └── handler/                         # Handler/Interceptor
│       ├── __init__.py
│       └── handler.py                   # HandlerContainer, Interceptor
│
└── web/                                 # 🚀 Web Application 레이어
    ├── __init__.py
    ├── application.py                   # Application (Facade)
    ├── initializer.py                   # ApplicationInitializer
    ├── request_handler.py               # RequestHandler
    ├── server.py                        # DevServer
    │
    ├── http/                            # 🌐 HTTP 프로토콜 레이어
    │   ├── __init__.py
    │   ├── request.py                   # HttpRequest, HttpResponse
    │   ├── request_body.py              # RequestBody 타입
    │   ├── parameter_injector.py        # 파라미터 주입 (우선순위 기반)
    │   └── router.py                    # RouteHandler, Route 매칭
    │
    ├── middleware/                      # 🔗 미들웨어
    │   ├── __init__.py
    │   ├── chain.py                     # MiddlewareChain, Middleware
    │   └── builtins.py                  # CorsMiddleware, LoggingMiddleware
    │
    └── auth/                            # 🔐 인증
        ├── __init__.py
        ├── authentication.py            # Authentication 추상 클래스
        └── README.md                    # 인증 가이드
```

## 📊 변경 사항 요약

### Before (구조 혼재)
```
vessel/
├── core/                    # DI + 기타 혼재 (327줄의 거대한 파일)
├── decorators/              # 모든 데코레이터가 한 곳에
├── http/                    # HTTP + Mapping 혼재
└── web/                     # Application + Middleware 평면
```

### After (기능별 분리 + 단일 책임 원칙)
```
vessel/
├── di/                      # ✨ DI만 집중
│   ├── core/                # 핵심 클래스
│   └── utils/               # 단일 책임 분리 (5개 모듈)
├── decorators/
│   ├── di/                  # DI 데코레이터
│   ├── web/                 # Web 데코레이터
│   └── handler/             # Handler 데코레이터
└── web/                     # 🚀 Web Application 레이어
    ├── http/                # 🌐 HTTP 프로토콜 (web 하위로 이동)
    ├── middleware/          # 🔗 미들웨어 별도 관리
    └── auth/                # 🔐 인증 시스템
```

## 🎯 개선 효과

### 1. **명확한 책임 분리**
- `di/core/`: DI 핵심 클래스 (Container, ContainerManager, DependencyGraph)
- `di/utils/`: 단일 책임 원칙을 따르는 5개 유틸리티 모듈
  - `PackageScanner`: 패키지 스캐닝
  - `ContainerCollector`: 컨테이너 수집
  - `DependencyAnalyzer`: 의존성 분석
  - `ComponentInitializer`: 초기화 (Topological Sort 순서)
  - `InterceptorResolver`: 인터셉터 의존성 해결
- `decorators/di/`: DI 관련 데코레이터
- `decorators/web/`: Web 관련 데코레이터
- `decorators/handler/`: Interceptor 패턴
- `web/http/`: HTTP 프로토콜 처리
- `web/middleware/`: 미들웨어 시스템
- `web/auth/`: 인증 시스템

### 2. **Import 경로 개선**
```python
# Before
from vessel.core.container_manager import ContainerManager
from vessel.decorators.component import Component
from vessel.http.http_handler import Get

# After
from vessel.di.core.container_manager import ContainerManager
from vessel.decorators.di.component import Component
from vessel.decorators.web.mapping import Get
from vessel.web.http.request import HttpRequest, HttpResponse
```

### 3. **확장성 향상**
- 각 모듈이 독립적으로 확장 가능
- 새로운 데코레이터 추가 시 적절한 위치에 배치
- 미들웨어 시스템 확장 용이
- 각 유틸리티 모듈을 독립적으로 테스트/수정 가능

### 4. **가독성 향상**
- 파일 위치만 봐도 기능 파악 가능
- 새로운 개발자의 학습 곡선 감소
- 코드 네비게이션 개선
- **ContainerManager가 102줄**로 줄어들며 Orchestrator 역할만 수행

### 5. **단일 책임 원칙 (SRP) 준수**
- 리팩토링 전: ContainerManager 327줄 (6가지 책임)
- 리팩토링 후: 각 클래스가 하나의 책임만 가짐
  - PackageScanner: 57줄
  - ContainerCollector: 90줄
  - DependencyAnalyzer: 122줄
  - ComponentInitializer: 151줄
  - InterceptorResolver: 97줄
  - ContainerManager: 102줄 (Orchestrator)

## 📝 주요 이름 변경

| Before | After | 이유 |
|--------|-------|------|
| `vessel/core/` | `vessel/di/core/` + `vessel/di/utils/` | DI 기능에 집중 + 단일 책임 분리 |
| `vessel/core/container_manager.py` (327줄) | `vessel/di/core/container_manager.py` (102줄) + 5개 utils | SRP 준수 |
| `vessel/decorators/component.py` | `vessel/decorators/di/component.py` | DI 데코레이터 그룹화 |
| `vessel/decorators/controller.py` | `vessel/decorators/web/controller.py` | Web 데코레이터 그룹화 |
| `vessel/http/http_handler.py` | `vessel/decorators/web/mapping.py` | HTTP 매핑은 데코레이터 |
| `vessel/http/` | `vessel/web/http/` | HTTP는 Web 레이어의 일부 |
| `vessel/http/route_handler.py` | `vessel/web/http/router.py` | 간결한 이름 + 경로 정리 |
| `vessel/web/middleware.py` | `vessel/web/middleware/chain.py` | 미들웨어 관련 파일 그룹화 |
| `vessel/web/builtins.py` | `vessel/web/middleware/builtins.py` | 미들웨어와 함께 관리 |
| `vessel/web/app_initializer.py` | `vessel/web/initializer.py` | 간결한 이름 |
| `vessel/web/dev_server.py` | `vessel/web/server.py` | 간결한 이름 |

## ✅ 테스트 결과

- **60/60 테스트 통과** ✓
- 모든 import 경로 업데이트 완료
- 공개 API 변경 없음 (하위 호환성 유지)

## 🎓 사용 예제

### Import 패턴
```python
# DI 관련
from vessel.di.core.container_manager import ContainerManager
from vessel.decorators.di import Component, Configuration, Factory

# Web 관련
from vessel.decorators.web import Controller, Get, Post
from vessel.web.http import HttpRequest, HttpResponse
from vessel.web.http.request_body import RequestBody
from vessel.web import Application

# Middleware
from vessel.web.middleware import Middleware, MiddlewareChain
from vessel.web.middleware.builtins import CorsMiddleware, LoggingMiddleware

# Authentication
from vessel.web.auth import Authentication
```

### 디렉토리별 용도

#### `vessel/di/core/` - DI 코어
- `Container`: 모든 컨테이너의 베이스 클래스
- `ContainerManager`: Orchestrator - 전체 초기화 프로세스 조율
- `DependencyGraph`: Topological Sort를 통한 의존성 해결

#### `vessel/di/utils/` - DI 유틸리티 (단일 책임)
- `PackageScanner`: 패키지 스캐닝 및 모듈 import
- `ContainerCollector`: 전역 레지스트리에서 컨테이너 수집
- `DependencyAnalyzer`: 컴포넌트/컨트롤러/팩토리 의존성 분석
- `ComponentInitializer`: Topological Sort 순서대로 초기화
- `InterceptorResolver`: 인터셉터 의존성 수집 및 해결

#### `vessel/decorators/` - 데코레이터
사용자가 직접 사용하는 데코레이터들을 기능별로 분류
- `di/`: @Component, @Factory, @Configuration
- `web/`: @Controller, @Get, @Post 등
- `handler/`: HandlerInterceptor, create_handler_decorator

#### `vessel/web/http/` - HTTP 프로토콜 레이어
HTTP 프로토콜 수준의 요청/응답 처리
- `request.py`: HttpRequest, HttpResponse
- `request_body.py`: RequestBody 타입 정의
- `parameter_injector.py`: 파라미터 주입 (우선순위 기반)
- `router.py`: 라우트 매칭 및 핸들러 실행

#### `vessel/web/` - Application 레이어
웹 애플리케이션 구성 및 실행
- `application.py`: Application Facade
- `middleware/`: 미들웨어 체인 시스템
- `auth/`: 인증 시스템

## 📚 참고

- 구조 변경 전체 계획: [RESTRUCTURE_PLAN.md](RESTRUCTURE_PLAN.md)
- 각 모듈의 상세 설명: 각 `__init__.py` 참조
