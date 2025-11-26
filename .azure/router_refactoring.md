# Router Module Refactoring

## 개요
router 기능을 `vessel/web/router`로 정리하고, 파라미터 validation을 parameter injection 시스템으로 통합했습니다.

## 변경 사항

### 1. Router 모듈 재구성
- **Before**: `vessel/http/router.py`
- **After**: `vessel/web/router/`
  - `handler.py` - Route, RouteHandler 클래스
  - `__init__.py` - 모듈 진입점

### 2. DefaultValueInjector 추가
새로운 parameter injector를 추가하여 기본 파라미터 타입 변환 및 검증을 처리합니다.

**파일**: `vessel/http/parameter_injection/default_value_injector.py`

**특징**:
- Priority: 999 (가장 낮은 우선순위 - fallback injector)
- 다른 injector가 처리하지 않은 일반 파라미터 처리
- 타입 변환 (int, bool, list, dict 등)
- 필수 파라미터 검증
- 기본값 처리

**지원하는 타입 변환**:
- `int`, `float`, `str`, `bool`
- `List[T]` - 쉼표로 구분된 문자열을 리스트로 변환
- `Dict[K, V]`

### 3. ValidationError 이동
- `ValidationError`를 `vessel.http.parameter_injection.default_value_injector`로 이동
- `vessel.validation`은 하위 호환성을 위해 re-export

### 4. ParameterInjectorRegistry 개선
여러 파라미터의 validation 에러를 모아서 한 번에 반환하도록 개선:

```python
# Before: 첫 번째 에러만 반환
inject() -> ValidationError

# After: 모든 에러를 모아서 반환
inject_parameters() -> ValidationError with multiple errors
```

### 5. RouteHandler 간소화
`ParameterValidator.validate_and_convert()` 호출 제거:

**Before**:
```python
# 레지스트리를 통한 파라미터 주입
kwargs = self.injector_registry.inject_parameters(...)

# Validation 수행 (이미 주입된 파라미터는 제외)
skip_params = set(kwargs.keys())
validated_params = ParameterValidator.validate_and_convert(
    handler, request_data, skip_params
)
kwargs.update(validated_params)
```

**After**:
```python
# 레지스트리를 통한 모든 파라미터 주입 (validation 포함)
kwargs = self.injector_registry.inject_parameters(
    handler, request, request_data, hints
)
```

## Import 경로 변경

### Router
```python
# Before
from vessel.http.router import RouteHandler, Route

# After
from vessel.web.router import RouteHandler, Route
```

### ValidationError
```python
# Before
from vessel.validation import ValidationError

# After
from vessel.http.parameter_injection import ValidationError
# 또는 (하위 호환성)
from vessel.validation import ValidationError
```

## 업데이트된 파일

**Router 이동**:
- `vessel/http/router.py` → `vessel/web/router/handler.py`
- `vessel/web/router/__init__.py` (NEW)

**Parameter Injection**:
- `vessel/http/parameter_injection/default_value_injector.py` (NEW)
- `vessel/http/parameter_injection/__init__.py` (updated)
- `vessel/http/parameter_injection/registry.py` (updated)
- `vessel/http/parameter_injection/annotated_value_injector.py` (updated import)

**Import 경로 업데이트**:
- `vessel/http/__init__.py`
- `vessel/web/application.py`
- `vessel/web/initializer.py`
- `vessel/web/request_handler.py`
- `vessel/validation.py` (deprecated, re-export only)
- `tests/test_integration_advanced.py`

## 장점

1. **일관된 구조**: 모든 파라미터 주입이 Registry 패턴으로 통합
2. **확장성**: 새로운 타입의 injector 추가가 쉬움
3. **우선순위 관리**: Priority를 통한 명확한 실행 순서
4. **더 나은 에러 처리**: 여러 파라미터의 에러를 한 번에 반환
5. **모듈 정리**: router가 web 모듈에 위치하여 논리적 구조 개선

## Injector Priority

```
0-99:   특수 타입 (HttpRequest: 10)
100-199: HTTP 관련 (AuthenticationInjector: 150, HttpHeader: 100, HttpCookie: 110)
200-299: 파일 (FileInjector: 200)
999:     기본값/타입 변환 (DefaultValueInjector: 999 - fallback)
```

## 테스트 결과
✅ All 114 tests passing
