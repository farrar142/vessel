# Vessel Framework - Restructuring Plan

## 현재 구조 문제점
1. `vessel/core/` - DI 관련 파일들이 혼재
2. `vessel/decorators/` - 다양한 목적의 데코레이터들이 섞여있음
3. `vessel/http/` - HTTP 관련이지만 역할이 불명확
4. `vessel/web/` - 웹 애플리케이션 관련이지만 정리 필요

## 개선된 구조

```
vessel/
├── __init__.py                      # 메인 export
│
├── di/                              # Dependency Injection 핵심
│   ├── __init__.py
│   ├── container.py                 # Container 클래스
│   ├── container_manager.py         # ContainerManager
│   ├── container_collector.py       # 컨테이너 수집
│   ├── component_initializer.py     # 컴포넌트 초기화
│   ├── dependency.py                # DependencyGraph
│   ├── dependency_analyzer.py       # 의존성 분석
│   ├── interceptor_resolver.py      # 인터셉터 해결
│   └── package_scanner.py           # 패키지 스캐너
│
├── decorators/                      # 데코레이터
│   ├── __init__.py
│   ├── di/                          # DI 관련 데코레이터
│   │   ├── __init__.py
│   │   ├── component.py             # @Component
│   │   ├── configuration.py         # @Configuration
│   │   └── factory.py               # @Factory
│   │
│   ├── web/                         # Web 관련 데코레이터
│   │   ├── __init__.py
│   │   ├── controller.py            # @Controller
│   │   └── mapping.py               # @Get, @Post, @Put, @Delete
│   │
│   └── handler/                     # Handler/Interceptor 데코레이터
│       ├── __init__.py
│       └── handler.py               # HandlerContainer, Interceptor
│
├── http/                            # HTTP 프로토콜 레이어
│   ├── __init__.py
│   ├── request.py                   # HttpRequest, HttpResponse
│   └── router.py                    # RouteHandler, Route 매칭
│
├── web/                             # Web Application 레이어
│   ├── __init__.py
│   ├── application.py               # Application (Facade)
│   ├── initializer.py               # ApplicationInitializer
│   ├── request_handler.py           # RequestHandler
│   ├── server.py                    # DevServer
│   │
│   └── middleware/                  # 미들웨어
│       ├── __init__.py
│       ├── chain.py                 # MiddlewareChain
│       ├── base.py                  # Middleware ABC
│       └── builtins.py              # CorsMiddleware, LoggingMiddleware
│
└── utils/                           # 유틸리티
    └── __init__.py
```

## 마이그레이션 계획

### Phase 1: DI 모듈 정리
- `vessel/core/` → `vessel/di/`
- DI와 관련 없는 파일들 분리

### Phase 2: Decorators 재구조화
- `vessel/decorators/` 를 기능별로 하위 폴더 생성
- DI, Web, Handler로 분리

### Phase 3: HTTP/Web 분리
- `vessel/http/http_handler.py` → `vessel/decorators/web/mapping.py`
- `vessel/http/route_handler.py` → `vessel/http/router.py`

### Phase 4: Middleware 분리
- `vessel/web/middleware.py` → `vessel/web/middleware/chain.py`
- `vessel/web/builtins.py` → `vessel/web/middleware/builtins.py`

### Phase 5: Web 모듈 정리
- 파일명 간소화
- app_initializer.py → initializer.py
- dev_server.py → server.py

## 실행 순서
1. 새 디렉토리 구조 생성
2. 파일 이동 및 import 경로 업데이트
3. __init__.py 파일들 업데이트
4. 테스트 실행 및 검증
5. Git 커밋
