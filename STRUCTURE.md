# Vessel Framework - 새로운 구조

## 📁 디렉토리 구조

```
vessel/
├── __init__.py                          # 메인 export
│
├── di/                                  # ✨ DI (Dependency Injection) 핵심
│   ├── __init__.py
│   ├── container.py                     # Container 클래스
│   ├── container_manager.py             # ContainerManager (DI 메인)
│   ├── container_collector.py           # 컨테이너 수집
│   ├── component_initializer.py         # 컴포넌트 초기화
│   ├── dependency.py                    # DependencyGraph
│   ├── dependency_analyzer.py           # 의존성 분석
│   ├── interceptor_resolver.py          # 인터셉터 해결
│   └── package_scanner.py               # 패키지 스캐너
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
├── http/                                # 🌐 HTTP 프로토콜 레이어
│   ├── __init__.py
│   ├── request.py                       # HttpRequest, HttpResponse
│   └── router.py                        # RouteHandler, Route 매칭
│
└── web/                                 # 🚀 Web Application 레이어
    ├── __init__.py
    ├── application.py                   # Application (Facade)
    ├── initializer.py                   # ApplicationInitializer
    ├── request_handler.py               # RequestHandler
    ├── server.py                        # DevServer
    │
    └── middleware/                      # 🔗 미들웨어
        ├── __init__.py
        ├── chain.py                     # MiddlewareChain, Middleware
        └── builtins.py                  # CorsMiddleware, LoggingMiddleware
```

## 📊 변경 사항 요약

### Before (구조 혼재)
```
vessel/
├── core/                    # DI + 기타 혼재
├── decorators/              # 모든 데코레이터가 한 곳에
├── http/                    # HTTP + Mapping 혼재
└── web/                     # Application + Middleware 평면
```

### After (기능별 분리)
```
vessel/
├── di/                      # ✨ DI만 집중
├── decorators/
│   ├── di/                  # DI 데코레이터
│   ├── web/                 # Web 데코레이터
│   └── handler/             # Handler 데코레이터
├── http/                    # 🌐 HTTP 프로토콜만
└── web/
    ├── application.py       # 🚀 Application 레이어
    └── middleware/          # 🔗 미들웨어 별도 관리
```

## 🎯 개선 효과

### 1. **명확한 책임 분리**
- `di/`: Dependency Injection 핵심 로직
- `decorators/di/`: DI 관련 데코레이터
- `decorators/web/`: Web 관련 데코레이터
- `decorators/handler/`: Interceptor 패턴
- `http/`: HTTP 프로토콜 처리
- `web/`: Web Application 레이어
- `web/middleware/`: 미들웨어 시스템

### 2. **Import 경로 개선**
```python
# Before
from vessel.core.container_manager import ContainerManager
from vessel.decorators.component import Component
from vessel.http.http_handler import Get

# After
from vessel.di.container_manager import ContainerManager
from vessel.decorators.di.component import Component
from vessel.decorators.web.mapping import Get
```

### 3. **확장성 향상**
- 각 모듈이 독립적으로 확장 가능
- 새로운 데코레이터 추가 시 적절한 위치에 배치
- 미들웨어 시스템 확장 용이

### 4. **가독성 향상**
- 파일 위치만 봐도 기능 파악 가능
- 새로운 개발자의 학습 곡선 감소
- 코드 네비게이션 개선

## 📝 주요 이름 변경

| Before | After | 이유 |
|--------|-------|------|
| `vessel/core/` | `vessel/di/` | DI 기능에 집중 |
| `vessel/decorators/component.py` | `vessel/decorators/di/component.py` | DI 데코레이터 그룹화 |
| `vessel/decorators/controller.py` | `vessel/decorators/web/controller.py` | Web 데코레이터 그룹화 |
| `vessel/http/http_handler.py` | `vessel/decorators/web/mapping.py` | HTTP 매핑은 데코레이터 |
| `vessel/http/route_handler.py` | `vessel/http/router.py` | 간결한 이름 |
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
from vessel.di import ContainerManager
from vessel.decorators.di import Component, Configuration, Factory

# Web 관련
from vessel.decorators.web import Controller, Get, Post
from vessel.http import HttpRequest, HttpResponse
from vessel.web import Application

# Middleware
from vessel.web.middleware import Middleware, MiddlewareChain
from vessel.web.middleware.builtins import CorsMiddleware
```

### 디렉토리별 용도

#### `vessel/di/` - DI 엔진
프레임워크의 핵심 DI 기능 구현

#### `vessel/decorators/` - 데코레이터
사용자가 직접 사용하는 데코레이터들을 기능별로 분류

#### `vessel/http/` - HTTP 레이어
HTTP 프로토콜 수준의 요청/응답 처리

#### `vessel/web/` - Application 레이어
웹 애플리케이션 구성 및 실행

## 📚 참고

- 구조 변경 전체 계획: [RESTRUCTURE_PLAN.md](RESTRUCTURE_PLAN.md)
- 각 모듈의 상세 설명: 각 `__init__.py` 참조
