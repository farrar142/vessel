# PyDI Framework Testing Guide

## 🧪 테스트 구조

```
tests/
├── conftest.py                      # pytest 설정
├── test_container.py                # Container 기본 클래스 단위 테스트
├── test_component.py                # @Component 데코레이터 단위 테스트
├── test_dependency.py               # 의존성 그래프 단위 테스트
├── test_handler.py                  # Handler & Interceptor 단위 테스트
├── test_integration.py              # ContainerManager 통합 테스트
└── test_integration_advanced.py    # 데코레이터 팩토리 통합 테스트
```

## 🚀 테스트 실행 방법

### 1. 테스트 의존성 설치

```bash
pip install -r requirements-test.txt
```

### 2. 모든 테스트 실행

```bash
# 방법 1: pytest 직접 실행
pytest tests/ -v

# 방법 2: 테스트 스크립트 사용
python run_tests.py
```

**결과**: 60/60 테스트 통과 ✓

### 3. 커버리지 포함 테스트

```bash
# 커버리지 리포트 생성
pytest tests/ -v --cov=vessel --cov-report=html --cov-report=term-missing

# HTML 리포트 확인
# htmlcov/index.html 파일 열기
```

**목표 커버리지**: 80% 이상 (핵심 모듈 95% 이상)

### 4. 특정 테스트 파일만 실행

```bash
# 단위 테스트만
pytest tests/test_component.py -v

# 통합 테스트만
pytest tests/test_integration.py -v
```

### 5. 특정 테스트 케이스만 실행

```bash
# 클래스 단위
pytest tests/test_component.py::TestComponent -v

# 메서드 단위
pytest tests/test_component.py::TestComponent::test_component_decorator -v
```

## 📊 테스트 카테고리

### 단위 테스트 (Unit Tests) - 30개

#### test_container.py (4개)
- ✅ 컨테이너 생성
- ✅ 메타데이터 관리
- ✅ 중첩 컨테이너
- ✅ 초기화 메서드

#### test_component.py (5개)
- ✅ @Component 데코레이터 적용
- ✅ 컴포넌트 초기화
- ✅ 의존성 주입
- ✅ 싱글톤 패턴
- ✅ 타입 힌트 없는 컴포넌트

#### test_dependency.py (8개)
- ✅ 의존성 추가
- ✅ 위상 정렬 (Topological Sort) - 단순/복잡
- ✅ **순환 의존성 감지** (Kahn's Algorithm)
- ✅ 의존성 없는 노드 처리
- ✅ 의존성 추출

#### test_handler.py (13개)
- ✅ HandlerInterceptor 기본 동작
- ✅ HandlerContainer 생성 및 관리
- ✅ 인터셉터 래핑
- ✅ 여러 인터셉터 실행 순서 (before/after/on_error)
- ✅ 에러 처리 및 전파
- ✅ create_handler_decorator 팩토리
- ✅ 내장 인터셉터 (Transaction, Logging)

### 통합 테스트 (Integration Tests) - 27개

#### test_integration.py (7개)
- ✅ 간단한 컴포넌트 초기화
- ✅ 필드 주입 방식 의존성 주입
- ✅ 여러 의존성 주입
- ✅ 컨트롤러 초기화
- ✅ 순환 의존성 감지
- ✅ 컴포넌트 스캔 (`__main__` 모듈)
- ✅ 모든 인스턴스 조회

#### test_integration_advanced.py (4개)
- ✅ 인터셉터 의존성 주입
- ✅ 여러 인터셉터 + 각각 의존성 주입
- ✅ 의존성 없는 인터셉터
- ✅ 혼합 (의존성 있는/없는 인터셉터)

#### test_application.py (6개)
- ✅ Application 초기화
- ✅ 컴포넌트 스캔 및 초기화
- ✅ 라우트 등록 및 매칭
- ✅ HTTP 요청 처리
- ✅ 개발 서버 시작

#### test_middleware_integration.py (5개)
- ✅ 미들웨어 체인 실행 순서
- ✅ Early return (process_request에서 응답 반환)
- ✅ 여러 미들웨어 조합
- ✅ 내장 미들웨어 (CORS, Logging)
- ✅ 미들웨어 그룹

#### test_http_injection.py (5개)
- ✅ Header 주입 (단일/다중)
- ✅ Cookie 주입 (단일/다중)
- ✅ Header + Cookie + Body 혼합
- ✅ 필수/선택 파라미터 처리
- ✅ Header 이름 변환 (snake_case → kebab-case)

## 🎯 테스트 커버리지 목표

- **전체 코드 커버리지**: 80% 이상
- **핵심 모듈**: 95% 이상
  - `vessel/di/core/container.py` - Container 클래스
  - `vessel/di/core/dependency.py` - DependencyGraph, Topological Sort
  - `vessel/di/core/container_manager.py` - ContainerManager
  - `vessel/di/utils/*.py` - 5개 유틸리티 모듈
  - `vessel/decorators/**/*.py` - 모든 데코레이터

**현재 상태**: 60/60 테스트 통과 ✓

## 📝 테스트 작성 가이드

### 1. 단위 테스트 작성

```python
import pytest
from vessel import Component

class TestMyFeature:
    """기능 설명"""
    
    def test_basic_functionality(self):
        """기본 기능 테스트"""
        # Given
        @Component
        class MyService:
            pass
        
        # When
        container = MyService.__pydi_container__
        instance = container.initialize()
        
        # Then
        assert instance is not None
```

### 2. 통합 테스트 작성

```python
def test_full_workflow(self):
    """전체 워크플로우 테스트"""
    # Setup
    @Component
    class ServiceA:
        pass
    
    @Component
    class ServiceB:
        service_a: ServiceA
    
    # Execute
    manager = ContainerManager()
    manager.component_scan("__main__")
    manager.initialize()
    
    # Verify
    instance = manager.get_instance(ServiceB)
    assert instance.service_a is not None
```

### 3. 예외 테스트

```python
def test_circular_dependency(self):
    """순환 의존성 감지 테스트"""
    graph = DependencyGraph()
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "A")
    
    with pytest.raises(ValueError, match="Circular"):
        graph.topological_sort()
```

## 🐛 디버깅

### 특정 테스트만 디버깅

```bash
# 자세한 출력
pytest tests/test_component.py::TestComponent::test_component_decorator -vv

# 출력 캡처 비활성화 (print 문 보기)
pytest tests/ -v -s

# 실패 시 즉시 중단
pytest tests/ -v -x
```

### 실패한 테스트만 재실행

```bash
pytest --lf  # last-failed
pytest --ff  # failed-first (실패한 테스트 먼저, 나머지도 실행)
```

### 테스트 격리 (Test Isolation)

**중요**: 각 테스트는 독립적이어야 합니다.

```python
# conftest.py의 cleanup_registry fixture
@pytest.fixture(autouse=True)
def cleanup_registry():
    """각 테스트 전후 전역 레지스트리 초기화"""
    from vessel.di.core.container import _registry
    _registry.clear()
    yield
    _registry.clear()
```

**새로운 데코레이터를 추가할 때**는 이 fixture를 확장하여 해당 레지스트리도 초기화하세요.

## 📈 CI/CD 통합

```yaml
# GitHub Actions 예시
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      
      - name: Run Tests with Coverage
        run: |
          pytest tests/ -v --cov=vessel --cov-report=xml --cov-report=term-missing
      
      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## ✅ 체크리스트

### 새 기능을 추가할 때:

- [ ] 단위 테스트 작성 (핵심 로직 검증)
- [ ] 통합 테스트 작성 (필요시 - 전체 워크플로우)
- [ ] 엣지 케이스 테스트 (경계값, 빈 값 등)
- [ ] 에러 케이스 테스트 (`pytest.raises` 사용)
- [ ] 모든 테스트 통과 확인 (`pytest tests/ -v`)
- [ ] 커버리지 80% 이상 유지 (핵심 모듈 95% 이상)
- [ ] 테스트 격리 확인 (cleanup_registry 활용)

### 리팩토링 시:

- [ ] 기존 테스트가 모두 통과하는지 확인
- [ ] 새로운 모듈에 대한 단위 테스트 추가
- [ ] Import 경로 변경이 반영되었는지 확인
- [ ] 공개 API가 변경되지 않았는지 확인

## 🎓 pytest 팁

### Fixtures 사용

```python
@pytest.fixture
def sample_service():
    @Component
    class SampleService:
        pass
    return SampleService

def test_with_fixture(sample_service):
    container = sample_service.__pydi_container__
    assert container is not None
```

### Parametrize로 여러 케이스 테스트

```python
@pytest.mark.parametrize("value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(value, expected):
    assert value * 2 == expected
```

### 표준 출력 캡처

```python
def test_logging(capsys):
    print("Hello")
    captured = capsys.readouterr()
    assert "Hello" in captured.out
```

## 📚 주요 테스트 패턴

### 1. 필드 주입 테스트
```python
@Component
class ServiceA:
    pass

@Component
class ServiceB:
    service_a: ServiceA  # 필드 주입 (NOT 생성자)

manager = ContainerManager()
manager.component_scan("__main__")
manager.initialize()

instance = manager.get_instance(ServiceB)
assert instance.service_a is not None
```

### 2. 순환 의존성 테스트
```python
graph = DependencyGraph()
graph.add_dependency("A", "B")
graph.add_dependency("B", "A")  # 순환!

with pytest.raises(ValueError, match="Circular dependency"):
    graph.topological_sort()
```

### 3. 미들웨어 체인 테스트
```python
@Configuration
class Config:
    @Factory
    def middleware_chain(self, mw1: Middleware1) -> MiddlewareChain:
        chain = MiddlewareChain()
        chain.get_default_group().add(mw1)
        return chain

# 미들웨어 실행 순서 검증
```

### 4. 인터셉터 의존성 주입 테스트
```python
class MyInterceptor(HandlerInterceptor):
    service: MyService  # 인터셉터도 DI 가능

# 인터셉터는 메인 컴포넌트 초기화 AFTER에 해결됨
InterceptorResolver.resolve_handler_interceptors(container_manager)
```

## 🔗 관련 문서

- `TEST_RESULTS.md` - 전체 테스트 결과 요약
- `REFACTORING.md` - ContainerManager 리팩토링 상세
- `docs/01_dependency_injection.md` - DI 기능 가이드
- `conftest.py` - pytest 설정 및 fixtures

---

**테스트 작성 완료! 🎉**

모든 핵심 기능에 대한 단위 테스트와 통합 테스트가 준비되었습니다.
