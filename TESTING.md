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

### 3. 커버리지 포함 테스트

```bash
# 커버리지 리포트 생성
python run_tests.py --coverage

# 또는
pytest tests/ --cov=pydi --cov-report=html
```

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

### 단위 테스트 (Unit Tests)

#### test_container.py
- ✅ 컨테이너 생성
- ✅ 메타데이터 관리
- ✅ 중첩 컨테이너
- ✅ 초기화 메서드

#### test_component.py
- ✅ @Component 데코레이터 적용
- ✅ 컴포넌트 초기화
- ✅ 의존성 주입
- ✅ 싱글톤 패턴
- ✅ 타입 힌트 없는 컴포넌트

#### test_dependency.py
- ✅ 의존성 추가
- ✅ 위상 정렬 (Topological Sort)
- ✅ 순환 의존성 감지
- ✅ 의존성 추출

#### test_handler.py
- ✅ HandlerInterceptor 기본 동작
- ✅ HandlerContainer 생성 및 관리
- ✅ 인터셉터 래핑
- ✅ 여러 인터셉터 실행 순서
- ✅ 에러 처리
- ✅ create_handler_decorator 팩토리
- ✅ 내장 인터셉터 (Transaction, Logging)

### 통합 테스트 (Integration Tests)

#### test_integration.py
- ✅ 간단한 컴포넌트 초기화
- ✅ 의존성 주입
- ✅ 여러 의존성 주입
- ✅ 컨트롤러 초기화
- ✅ 컴포넌트 스캔
- ✅ 모든 인스턴스 조회

#### test_integration_advanced.py
- ✅ 인터셉터 의존성 주입
- ✅ 여러 인터셉터 + 각각 의존성 주입
- ✅ 의존성 없는 인터셉터
- ✅ 혼합 (의존성 있는/없는)
- ✅ HTTP 라우트 등록

## 🎯 테스트 커버리지 목표

- **전체 코드 커버리지**: 80% 이상
- **핵심 기능**: 95% 이상
  - Container 클래스
  - DependencyGraph
  - ContainerManager
  - Decorator 팩토리

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

# 출력 캡처 비활성화
pytest tests/ -v -s
```

### 실패한 테스트만 재실행

```bash
pytest --lf  # last-failed
pytest --ff  # failed-first
```

## 📈 CI/CD 통합

```yaml
# GitHub Actions 예시
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/ --cov=pydi --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## ✅ 체크리스트

새 기능을 추가할 때:

- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성 (필요시)
- [ ] 엣지 케이스 테스트
- [ ] 에러 케이스 테스트
- [ ] 모든 테스트 통과 확인
- [ ] 커버리지 80% 이상 유지

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

---

**테스트 작성 완료! 🎉**

모든 핵심 기능에 대한 단위 테스트와 통합 테스트가 준비되었습니다.
