# Injector 추상화 리팩토링

## 🎯 목표

`HttpHeaderInjector`와 `HttpCookieInjector`에서 공통으로 보이는 로직을 추상화하여 코드 중복을 제거하고 확장성을 높인다.

## 📊 변경 전후 비교

### Before (리팩토링 전)

```python
# HttpHeaderInjector: 134 lines
class HttpHeaderInjector(ParameterInjector):
    def can_inject(self, context):
        # 50+ lines of type checking logic
        # - Annotated[HttpHeader, "name"] check
        # - Optional[HttpHeader] check
        # - Optional[Annotated[HttpHeader, "name"]] check
        pass
    
    def inject(self, context):
        # Extract name, check optional, get value, validate
        pass
    
    def _extract_explicit_name(self, param_type):
        # 30+ lines of Annotated extraction logic
        pass
    
    def _is_optional(self, param_type):
        # 20+ lines of Optional checking logic
        pass

# HttpCookieInjector: 127 lines
class HttpCookieInjector(ParameterInjector):
    def can_inject(self, context):
        # DUPLICATE: 50+ lines (same as HttpHeaderInjector)
        pass
    
    def inject(self, context):
        # DUPLICATE: Same pattern as HttpHeaderInjector
        pass
    
    def _extract_explicit_name(self, param_type):
        # DUPLICATE: 30+ lines (same as HttpHeaderInjector)
        pass
    
    def _is_optional(self, param_type):
        # DUPLICATE: 20+ lines (same as HttpHeaderInjector)
        pass
```

**문제점:**
- ❌ 약 170 lines의 코드 중복
- ❌ 버그 수정 시 여러 곳 수정 필요
- ❌ 새로운 인젝터 추가 시 모든 로직 재작성 필요
- ❌ 유지보수 부담 증가

### After (리팩토링 후)

```python
# AnnotatedValueInjector: 239 lines (추상 기본 클래스)
class AnnotatedValueInjector(ParameterInjector, ABC):
    """
    공통 로직 구현:
    - can_inject(): Annotated/Optional 타입 체크
    - inject(): 값 추출 및 검증 패턴
    - _extract_explicit_name(): Annotated에서 이름 추출
    - _is_optional(): Optional 타입 확인
    
    추상 메서드 (서브클래스에서 구현):
    - get_marker_type(): 처리할 타입 반환
    - extract_value_from_request(): 요청에서 값 추출
    - get_default_name(): 기본 이름 결정
    - create_value_object(): 값 객체 생성
    - get_error_message(): 에러 메시지 생성
    """
    pass

# HttpHeaderInjector: 47 lines (-87 lines, 65% 감소)
class HttpHeaderInjector(AnnotatedValueInjector):
    def get_marker_type(self) -> type:
        return HttpHeader
    
    def extract_value_from_request(self, context, name):
        return context.request.headers.get(name)
    
    def get_default_name(self, param_name):
        return self._convert_to_header_name(param_name)  # snake_case -> Title-Case
    
    def create_value_object(self, name, value):
        return HttpHeader(name=name, value=value)
    
    def get_error_message(self, name, param_name):
        return f"Required header '{name}' is missing"

# HttpCookieInjector: 42 lines (-85 lines, 67% 감소)
class HttpCookieInjector(AnnotatedValueInjector):
    def get_marker_type(self) -> type:
        return HttpCookie
    
    def extract_value_from_request(self, context, name):
        return context.request.cookies.get(name)
    
    def get_default_name(self, param_name):
        return param_name  # No conversion needed
    
    def create_value_object(self, name, value):
        return HttpCookie(name=name, value=value)
    
    def get_error_message(self, name, param_name):
        return f"Required cookie '{name}' is missing"
```

**개선점:**
- ✅ 170 lines 중복 코드 → 239 lines 재사용 가능한 기본 클래스
- ✅ 각 인젝터는 5개의 간단한 메서드만 구현
- ✅ 새로운 인젝터 추가 시 45 lines만 작성하면 됨
- ✅ 버그 수정은 한 곳에서만 (AnnotatedValueInjector)
- ✅ 코드 가독성 향상: 각 인젝터의 고유 로직이 명확히 보임

## 📈 통계

| 항목 | Before | After | 변화 |
|-----|--------|-------|------|
| HttpHeaderInjector | 134 lines | 47 lines | **-65%** |
| HttpCookieInjector | 127 lines | 42 lines | **-67%** |
| 공통 로직 | 중복됨 (~170 lines) | 재사용 (239 lines) | ✅ |
| 전체 코드 | 261 lines | 328 lines | +25% |
| 인젝터당 평균 | ~130 lines | ~45 lines | **-65%** |

> **Note**: 전체 코드가 25% 증가했지만, 이는 재사용 가능한 기본 클래스로 인한 것입니다.
> 각 인젝터는 65% 감소하여 훨씬 단순해졌으며, 새로운 인젝터 추가 시 큰 이점이 있습니다.

## 🚀 확장성

이제 새로운 인젝터를 추가하기가 매우 쉽습니다:

```python
# 새로운 HttpQuery 인젝터 추가 예시 (약 45 lines)
class HttpQueryInjector(AnnotatedValueInjector):
    def get_marker_type(self) -> type:
        return HttpQuery
    
    def extract_value_from_request(self, context, name):
        return context.request.query_params.get(name)
    
    def get_default_name(self, param_name):
        return param_name
    
    def create_value_object(self, name, value):
        return HttpQuery(name=name, value=value)
    
    def get_error_message(self, name, param_name):
        return f"Required query parameter '{name}' is missing"
```

**Before**: 새 인젝터 추가 시 ~130 lines 작성 필요  
**After**: 새 인젝터 추가 시 ~45 lines 작성 (66% 감소)

## ✅ 테스트 결과

```bash
pytest -xvs
# 101/101 tests passing ✅
# All HTTP injection features working correctly
```

## 🎓 설계 패턴

이 리팩토링은 **Template Method Pattern**을 적용한 것입니다:

1. **AnnotatedValueInjector** (추상 클래스)
   - 알고리즘의 골격 정의 (`can_inject`, `inject`, `_extract_explicit_name`, `_is_optional`)
   - 변경되지 않는 공통 로직 구현

2. **HttpHeaderInjector, HttpCookieInjector** (구체 클래스)
   - 알고리즘의 세부 단계만 구현 (5개 추상 메서드)
   - 각자의 고유한 로직에만 집중

## 📝 핵심 이점

1. **DRY (Don't Repeat Yourself)**: 중복 제거
2. **SRP (Single Responsibility)**: 각 클래스가 하나의 책임만
3. **OCP (Open/Closed)**: 확장에는 열려있고 수정에는 닫혀있음
4. **코드 가독성**: 각 인젝터의 고유 로직이 명확히 보임
5. **유지보수성**: 버그 수정이나 기능 추가가 한 곳에서만
6. **테스트 용이성**: 공통 로직과 개별 로직을 분리하여 테스트 가능

## 🔍 FileInjector는?

`FileInjector`는 다른 패턴을 사용합니다:
- `UploadedFile` 타입 사용 (Annotated 구문 없음)
- `list[UploadedFile]` 지원
- 파일 데이터 파싱 로직 필요

따라서 `AnnotatedValueInjector`를 사용하지 않고 독립적으로 유지합니다.
만약 나중에 `file: UploadedFile["profile_pic"]` 같은 구문을 지원하려면,
그때 `AnnotatedValueInjector`를 확장할 수 있습니다.

## 🎯 결론

이번 리팩토링으로:
- ✅ 코드 중복 170 lines 제거
- ✅ 각 인젝터의 코드량 65% 감소
- ✅ 새 인젝터 추가 비용 66% 감소
- ✅ 유지보수성과 확장성 크게 향상
- ✅ 모든 테스트 통과 (101/101)

**리팩토링은 성공적이었습니다!** 🎉
