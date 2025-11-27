# ContainerManager 리팩토링 문서

## 📋 개요
`container_manager.py` 파일이 너무 많은 책임을 가지고 있어 **Single Responsibility Principle (SRP)**을 위반하고 있었습니다. 이를 해결하기 위해 기능을 5개의 독립적인 모듈로 분리했습니다.

## 🔍 문제점

### 리팩토링 전
- **327줄**의 큰 파일
- **6가지 주요 책임**을 한 클래스가 처리
  1. 패키지 스캐닝
  2. 컨테이너 수집
  3. 의존성 분석
  4. 컴포넌트 초기화
  5. 인터셉터 의존성 해결
  6. 조회 API 제공

### 문제
- 코드 가독성 저하
- 테스트 어려움
- 유지보수 복잡도 증가
- 단일 책임 원칙 위반

## 🏗️ 리팩토링 구조

### 새로운 모듈 구조

```
vessel/di/
├── core/
│   ├── container_manager.py         # 📊 Orchestrator (102줄)
│   ├── container.py                 # Container 베이스 클래스
│   └── dependency.py                # DependencyGraph (Topological Sort)
│
└── utils/                           # 단일 책임 원칙 (SRP) 준수
    ├── package_scanner.py           # 📦 패키지 스캐닝 (57줄)
    ├── container_collector.py       # 🗂️ 컨테이너 수집 (90줄)
    ├── dependency_analyzer.py       # 🔍 의존성 분석 (122줄)
    ├── component_initializer.py     # 🏭 컴포넌트 초기화 (151줄)
    └── interceptor_resolver.py      # 🔗 인터셉터 해결 (97줄)
```

## 📦 각 모듈의 책임

### 1. PackageScanner (`vessel/di/utils/package_scanner.py`)
**책임**: 패키지 스캐닝 및 모듈 import

```python
from vessel.di.utils.package_scanner import PackageScanner

PackageScanner.scan_packages("my_package", "another_package")
```

**주요 메서드**:
- `scan_packages(*packages)`: 여러 패키지 스캔
- `_scan_package(package_name)`: 단일 패키지 스캔 (재귀적)

**파일 크기**: 57줄

---

### 2. ContainerCollector (`vessel/di/utils/container_collector.py`)
**책임**: 전역 레지스트리에서 컨테이너 수집

```python
from vessel.di.utils.container_collector import ContainerCollector

components, controllers, factories = ContainerCollector.collect_containers()
```

**주요 메서드**:
- `collect_containers()`: 모든 컨테이너 수집 및 반환
- `_collect_factory_methods()`: @Factory 메서드 수집

**파일 크기**: 90줄

---

### 3. DependencyAnalyzer (`vessel/di/utils/dependency_analyzer.py`)
**책임**: 컴포넌트 간 의존성 분석 - DependencyGraph 구축

```python
from vessel.di.utils.dependency_analyzer import DependencyAnalyzer

DependencyAnalyzer.analyze_dependencies(
    components, controllers, factories, dependency_graph
)
```

**주요 메서드**:
- `analyze_dependencies()`: 전체 의존성 분석
- `_collect_factory_types()`: 팩토리 타입 수집
- `_analyze_component_dependencies()`: 컴포넌트 의존성 분석
- `_analyze_controller_dependencies()`: 컨트롤러 의존성 분석
- `_analyze_factory_dependencies()`: 팩토리 의존성 분석

**파일 크기**: 122줄

---

### 4. ComponentInitializer (`vessel/di/utils/component_initializer.py`)
**책임**: Topological Sort된 순서대로 컴포넌트 초기화

```python
from vessel.di.utils.component_initializer import ComponentInitializer

ComponentInitializer.initialize_components(
    sorted_types, components, controllers, factories, instances
)
```

**주요 메서드**:
- `initialize_components()`: 전체 초기화 조율
- `_initialize_factory_parents()`: 팩토리 부모 초기화
- `_build_factory_type_mapping()`: 팩토리 타입 매핑 생성
- `_initialize_sorted_types()`: 정렬된 타입 초기화
- `_initialize_factory_type()`: 팩토리를 통한 타입 생성
- `_initialize_remaining_components()`: 의존성 없는 컴포넌트 초기화

**파일 크기**: 151줄

---

### 5. InterceptorResolver (`vessel/di/utils/interceptor_resolver.py`)
**책임**: 인터셉터의 의존성 수집 및 해결

```python
from vessel.di.utils.interceptor_resolver import InterceptorResolver

InterceptorResolver.collect_and_initialize_interceptor_dependencies(
    components, instances
)
InterceptorResolver.resolve_handler_interceptors(container_manager)
```

**주요 메서드**:
- `collect_and_initialize_interceptor_dependencies()`: 인터셉터 의존성 수집/초기화
- `_collect_interceptor_dependency_types()`: 인터셉터 의존성 타입 수집
- `_initialize_interceptor_dependencies()`: 인터셉터 의존성 초기화
- `resolve_handler_interceptors()`: 핸들러 인터셉터 해결

**파일 크기**: 97줄

**중요**: 인터셉터는 메인 컴포넌트 초기화 **이후**에 해결됩니다.

---

### 6. ContainerManager (리팩토링 후) (`vessel/di/core/container_manager.py`)
**책임**: Orchestrator - 전체 프로세스 조율 및 외부 API 제공

```python
from vessel.di.core.container_manager import ContainerManager

manager = ContainerManager()
manager.component_scan("my_package")
manager.initialize()

instance = manager.get_instance(MyService)
```

**주요 메서드**:
- `component_scan(*packages)`: 패키지 스캔 (PackageScanner에 위임)
- `initialize()`: 전체 초기화 프로세스 조율
- `get_instance(type_)`: 인스턴스 조회
- `get_all_instances()`: 모든 인스턴스 조회
- `get_controllers()`: 컨트롤러 인스턴스 조회
- `get_container(type_)`: 컨테이너 조회

**파일 크기**: 102줄 (리팩토링 전 327줄에서 **69% 감소**)

## 🔄 초기화 프로세스 흐름

```
ContainerManager.initialize()
    ├─> 1. DependencyAnalyzer.analyze_dependencies()
    │      ├─> 팩토리 타입 수집
    │      ├─> 컴포넌트 의존성 분석
    │      ├─> 컨트롤러 의존성 분석
    │      └─> 팩토리 의존성 분석
    │
    ├─> 2. DependencyGraph.topological_sort()
    │      └─> 초기화 순서 결정
    │
    ├─> 3. ComponentInitializer.initialize_components()
    │      ├─> 팩토리 부모 초기화
    │      ├─> 팩토리 타입 매핑 생성
    │      ├─> Sorted types 초기화
    │      └─> 의존성 없는 컴포넌트 초기화
    │
    ├─> 4. InterceptorResolver.collect_and_initialize_interceptor_dependencies()
    │      ├─> 인터셉터 의존성 타입 수집
    │      └─> 인터셉터 의존성 초기화
    │
    └─> 5. InterceptorResolver.resolve_handler_interceptors()
           └─> 핸들러 인터셉터 인스턴스 해결
```

## 🎯 개선 효과

### 코드 품질
- ✅ **Single Responsibility Principle (SRP)**: 각 클래스가 하나의 책임만 가짐
- ✅ **가독성 향상**: 작은 파일들로 분리되어 이해하기 쉬움
- ✅ **테스트 용이**: 각 모듈을 독립적으로 테스트 가능
- ✅ **유지보수성**: 수정 시 영향 범위가 명확함
- ✅ **Orchestrator 패턴**: ContainerManager는 조율만 담당

### 파일 크기 비교
| 파일 | 리팩토링 전 | 리팩토링 후 | 감소율 |
|------|------------|------------|--------|
| container_manager.py | 327줄 | 102줄 | **-69%** |
| package_scanner.py | - | 57줄 | 신규 |
| container_collector.py | - | 90줄 | 신규 |
| dependency_analyzer.py | - | 122줄 | 신규 |
| component_initializer.py | - | 151줄 | 신규 |
| interceptor_resolver.py | - | 97줄 | 신규 |
| **전체 (di/utils 포함)** | 327줄 | **619줄** | +89% (모듈화) |

### 모듈성
- **높은 응집도**: 관련 기능이 함께 위치
- **낮은 결합도**: 모듈 간 의존성 최소화
- **재사용성**: 각 모듈을 독립적으로 사용 가능
- **테스트 가능**: 각 유틸리티를 독립적으로 테스트
- **확장 용이**: 새로운 기능 추가 시 적절한 모듈에 배치

## 🔧 기술적 세부사항

### 순환 Import 해결
리팩토링 과정에서 순환 import 문제가 발생했습니다:
```
container_manager → component → container → container_manager (순환!)
```

**해결 방법**:
1. **런타임 import**: isinstance 검사가 필요한 곳에서만 import
2. **타입 힌트 완화**: `Dict[Type, Any]` 사용

```python
# 런타임 import 예시
def collect_containers():
    from vessel.decorators.component import ComponentContainer
    # ... isinstance(container, ComponentContainer)
```

### 정적 메서드 사용
모든 새 모듈은 정적 메서드(`@staticmethod`)를 사용합니다:
- 상태를 가지지 않음 (stateless)
- 유틸리티 클래스로 동작
- 인스턴스 생성 불필요

## 🧪 테스트 결과

```bash
$ python -m pytest tests/ -v
```

**결과**: ✅ **44/44 tests passed** (100% 성공)

모든 기존 테스트가 수정 없이 통과하여 **Backward Compatibility**가 완벽히 보장됩니다.

## 📚 사용 예시

### 기존 코드 (변경 없음)
```python
from vessel import ContainerManager, Component

@Component
class MyService:
    pass

manager = ContainerManager()
manager.component_scan("my_package")
manager.initialize()

service = manager.get_instance(MyService)
```

### 내부 모듈 직접 사용 (선택적)
```python
from vessel.core.package_scanner import PackageScanner
from vessel.core.container_collector import ContainerCollector

# 패키지만 스캔
PackageScanner.scan_packages("my_package")

# 컨테이너만 수집
components, controllers, factories = ContainerCollector.collect_containers()
```

## 🚀 향후 개선 방향

1. **테스트 추가**: 각 리팩토링된 모듈에 대한 단위 테스트
2. **타입 힌트 개선**: `TYPE_CHECKING` 블록 활용
3. **문서화**: 각 모듈에 대한 상세 docstring
4. **성능 최적화**: 프로파일링 후 병목 지점 개선
5. **에러 처리**: 각 단계별 명확한 예외 처리

## 📝 마이그레이션 가이드

### 기존 사용자
- ✅ **변경 불필요**: 모든 public API는 동일
- ✅ **Backward Compatible**: 기존 코드 그대로 동작

### 고급 사용자 (내부 구현 사용)
```python
# 이전
from vessel.core.container_manager import ContainerManager
manager._analyze_dependencies()  # Private method

# 이후
from vessel.core.dependency_analyzer import DependencyAnalyzer
DependencyAnalyzer.analyze_dependencies(...)  # Public static method
```

## 📖 참고 자료

- **SOLID 원칙**: Single Responsibility Principle
- **Design Patterns**: Facade Pattern (ContainerManager), Strategy Pattern (각 책임 클래스)
- **Clean Code**: Robert C. Martin

## ✅ 체크리스트

- [x] 코드 리팩토링 완료
- [x] 모든 테스트 통과 (44/44)
- [x] 순환 import 해결
- [x] 문서 작성
- [x] Backward Compatibility 보장
- [ ] 각 모듈 단위 테스트 추가
- [ ] 성능 벤치마크
- [ ] 추가 문서화 (README 업데이트)

## 🎉 결론

`ContainerManager`의 리팩토링을 통해:
- **코드 가독성** 대폭 향상
- **유지보수성** 개선
- **테스트 용이성** 증가
- **모듈성** 강화

모든 기능은 **100% 호환**되며, 외부 API는 **변경 없음**입니다!
