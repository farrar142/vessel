# FileInjector Annotated 구문 지원

## 🎯 목표

`FileInjector`도 `HttpHeader`, `HttpCookie`와 마찬가지로 `Annotated` 구문을 지원하여 명시적인 파일 키를 지정할 수 있도록 개선합니다.

## 💡 동기

파일 업로드 시 multipart/form-data의 필드 이름과 파라미터 이름이 다를 수 있습니다:

```python
# Before: 파라미터 이름 = 폼 필드 이름
def upload(self, profile_pic: UploadedFile):
    # 클라이언트는 "profile_pic"이라는 필드명으로 보내야 함
    pass

# Problem: 파라미터 이름을 바꾸고 싶지만 필드명은 유지하고 싶은 경우
def upload(self, avatar: UploadedFile):
    # ❌ "avatar" 필드를 찾지만 클라이언트는 "profile_pic"으로 보냄
    pass
```

## ✨ 해결 방법

`Annotated` 구문으로 명시적 키 지정:

```python
def upload(self, avatar: UploadedFile["profile_pic"]):
    # ✅ 파라미터 이름은 "avatar"지만 "profile_pic" 필드를 찾음
    pass
```

## 📊 변경사항

### 1. UploadedFile 클래스 개선

```python
class UploadedFile:
    # ... existing code ...
    
    @classmethod
    def __class_getitem__(cls, key: str):
        """
        Support UploadedFile["key"] syntax for type annotations.
        
        Example:
            def upload(self, profile: UploadedFile["profile_pic"]):
                pass
        """
        return Annotated[cls, key]
```

### 2. FileInjector 개선

**Before (67 lines)**:
- 기본 `UploadedFile` 타입만 지원
- `Optional[UploadedFile]` 지원
- `list[UploadedFile]` 지원

**After (184 lines, +117 lines)**:
- ✅ `Annotated[UploadedFile, "key"]` 지원
- ✅ `Optional[Annotated[UploadedFile, "key"]]` 지원
- ✅ `list[Annotated[UploadedFile, "key"]]` 지원
- 새 메서드 추가:
  - `_extract_explicit_key()`: Annotated에서 키 추출
  - `_is_optional()`: Optional 타입 체크
  - `_is_list()`: list 타입 체크

## 🎨 사용 예시

### 1. 기본 사용 (기존 방식 유지)

```python
@Post("/upload")
def upload_file(self, file: UploadedFile) -> dict:
    # 폼 필드명: "file"
    return {"filename": file.filename}
```

### 2. 명시적 키 지정 (새로운 방식)

```python
@Post("/upload")
def upload_file(self, avatar: UploadedFile["profile_pic"]) -> dict:
    # 파라미터명: "avatar"
    # 폼 필드명: "profile_pic"
    return {"filename": avatar.filename}
```

### 3. Optional과 함께 사용

```python
@Post("/upload")
def upload_file(
    self, 
    avatar: Optional[UploadedFile["profile_pic"]] = None
) -> dict:
    if avatar is None:
        return {"has_file": False}
    return {"filename": avatar.filename}
```

### 4. List와 함께 사용

```python
@Post("/upload")
def upload_files(
    self, 
    images: list[UploadedFile["gallery_pics"]]
) -> dict:
    return {
        "count": len(images),
        "filenames": [img.filename for img in images]
    }
```

### 5. 혼합 사용

```python
@Post("/upload")
def upload_multiple(
    self,
    document: UploadedFile,  # 자동: "document" 필드
    avatar: UploadedFile["profile_pic"],  # 명시적: "profile_pic" 필드
) -> dict:
    return {
        "doc": document.filename,
        "avatar": avatar.filename
    }
```

### 6. 실전 예시 (프로필 업데이트)

```python
@Controller("/api")
class UserController:
    @Post("/profile")
    def update_profile(
        self,
        avatar: UploadedFile["user_avatar"],
        cover: UploadedFile["cover_image"],
    ) -> dict:
        return {
            "avatar_uploaded": avatar.filename,
            "cover_uploaded": cover.filename,
        }

# 클라이언트 요청:
# POST /api/profile
# Content-Type: multipart/form-data
# 
# user_avatar: [file data]
# cover_image: [file data]
```

## 🔍 FileInjector가 AnnotatedValueInjector를 사용하지 않는 이유

`HttpHeaderInjector`와 `HttpCookieInjector`는 `AnnotatedValueInjector`를 상속받지만, `FileInjector`는 독립적으로 유지됩니다:

### 차이점

| 특성 | HttpHeader/Cookie | UploadedFile |
|-----|------------------|--------------|
| 반환 타입 | 값 객체 (name, value) | 파일 객체 (filename, content, size) |
| 값 추출 | 단순 문자열 | 복잡한 파일 데이터 |
| 리스트 지원 | ❌ | ✅ `list[UploadedFile]` |
| 값 생성 | `HttpHeader(name, value)` | `parse_file_from_dict()` |
| 검증 로직 | 간단 (None 체크) | 복잡 (`_is_file_data()`) |

### FileInjector만의 특수 기능

1. **파일 데이터 검증**: `_is_file_data()` - dict 구조 확인
2. **리스트 처리**: 단일 파일과 리스트를 모두 처리
3. **파일 파싱**: `parse_file_from_dict()`, `parse_files_from_list()`
4. **우선순위**: `priority = 200` (다른 인젝터보다 높음)

### 코드 재사용

공통 패턴은 재사용:
- `_extract_explicit_key()` ≈ `AnnotatedValueInjector._extract_explicit_name()`
- `_is_optional()` ≈ `AnnotatedValueInjector._is_optional()`

하지만 전체 상속은 오히려 복잡도를 높임:
- 파일 특화 로직이 많음
- 리스트 처리 로직 필요
- `create_value_object()` 패턴이 맞지 않음 (파일 파싱 로직)

## 📈 통계

### 코드 메트릭

| 항목 | Before | After | 변화 |
|-----|--------|-------|------|
| UploadedFile | 91 lines | 106 lines | +15 lines |
| FileInjector | 137 lines | 184 lines | +47 lines |
| 테스트 | 12 tests | 17 tests | +5 tests |
| 전체 테스트 | 101 tests | 106 tests | +5 tests |

### 지원하는 구문

| 구문 | Before | After |
|-----|--------|-------|
| `file: UploadedFile` | ✅ | ✅ |
| `file: Optional[UploadedFile]` | ✅ | ✅ |
| `files: list[UploadedFile]` | ✅ | ✅ |
| `avatar: UploadedFile["key"]` | ❌ | ✅ |
| `avatar: Optional[UploadedFile["key"]]` | ❌ | ✅ |
| `images: list[UploadedFile["key"]]` | ❌ | ✅ |

## ✅ 테스트 결과

```bash
pytest tests/test_file_upload.py -xvs
# 17/17 tests passing ✅

pytest -xvs
# 106/106 tests passing ✅
```

### 새로운 테스트

1. `test_bracket_syntax_single_file`: 단일 파일 명시적 키
2. `test_bracket_syntax_with_optional`: Optional과 함께
3. `test_bracket_syntax_with_list`: 리스트와 함께
4. `test_mixed_auto_and_bracket_files`: 자동/명시적 혼합
5. `test_example_from_user`: 실전 예시

## 🎓 일관성

이제 모든 HTTP 인젝터가 동일한 패턴을 따릅니다:

```python
# Headers
user_agent: HttpHeader                    # 자동: "User-Agent"
agent: HttpHeader["User-Agent"]           # 명시적

# Cookies
session_id: HttpCookie                    # 자동: "session_id"
token: HttpCookie["access_token"]         # 명시적

# Files
file: UploadedFile                        # 자동: "file"
avatar: UploadedFile["profile_pic"]       # 명시적
```

## 🚀 실제 사용 사례

### Case 1: 레거시 API 유지

```python
# 클라이언트는 계속 "userAvatar"로 보냄 (카멜케이스)
# 서버 코드는 Python 스타일 (스네이크케이스)
def upload(self, user_avatar: UploadedFile["userAvatar"]):
    pass
```

### Case 2: API 게이트웨이 통과

```python
# API Gateway가 "X-File-Upload"를 "uploaded_file"로 변환
def upload(self, file: UploadedFile["uploaded_file"]):
    pass
```

### Case 3: 다중 파일 업로드

```python
def upload_profile(
    self,
    avatar: UploadedFile["user_avatar"],
    cover: UploadedFile["cover_image"],
    documents: list[UploadedFile["attachments"]],
):
    pass
```

## 🎯 결론

`FileInjector`가 이제 `Annotated` 구문을 지원하여:

- ✅ HTTP 인젝터들과 일관된 API
- ✅ 파라미터 이름과 폼 필드명 분리 가능
- ✅ 레거시 시스템 통합 용이
- ✅ 더 명확하고 유연한 파일 업로드 처리
- ✅ 모든 106개 테스트 통과

**FileInjector enhancement is complete!** 🎉
