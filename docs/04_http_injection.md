# HTTP Injection (Header & Cookie)

> 테스트 기반: `tests/test_http_injection.py`

## 개요

HTTP 헤더와 쿠키를 타입 안전하게 주입받을 수 있습니다.
`HttpHeader`와 `HttpCookie` 타입 마커를 사용합니다.

## HttpHeader 주입

### 기본 사용법 - 자동 변환

**파라미터 이름**이 자동으로 **헤더 이름**으로 변환됩니다:

```python
from vessel import Controller, Get, HttpHeader

@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, user_agent: HttpHeader) -> dict:
        return {
            "name": user_agent.name,    # "User-Agent"
            "value": user_agent.value   # "Mozilla/5.0 ..."
        }
```

**변환 규칙:**
- `user_agent` → `User-Agent`
- `content_type` → `Content-Type`
- `accept_language` → `Accept-Language`

즉, **snake_case → Title-Case**로 자동 변환됩니다.

### HttpHeader 객체

```python
header: HttpHeader

# 헤더 이름 (변환된 형태)
header.name  # "User-Agent"

# 헤더 값
header.value  # "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
```

### 여러 헤더 주입

```python
@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(
        self,
        user_agent: HttpHeader,
        host: HttpHeader,
        accept: HttpHeader
    ) -> dict:
        return {
            "user_agent": user_agent.value,
            "host": host.value,
            "accept": accept.value
        }
```

**요청 예시:**
```http
GET /api/user HTTP/1.1
User-Agent: Mozilla/5.0
Host: example.com
Accept: application/json
```

**응답:**
```json
{
  "user_agent": "Mozilla/5.0",
  "host": "example.com",
  "accept": "application/json"
}
```

### 브래킷 문법 (명시적 헤더 이름 지정)

타입 힌트에 헤더 이름을 포함하는 방식:

```python
@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, agent: HttpHeader["User-Agent"]) -> dict:
        return {
            "name": agent.name,    # "User-Agent"
            "value": agent.value
        }
```

**두 가지 문법 비교:**

```python
# 1. 자동 변환 (파라미터 이름 → 헤더 이름)
def handler(self, user_agent: HttpHeader): ...

# 2. 브래킷 문법 (명시적 헤더 이름 지정)
def handler(self, agent: HttpHeader["User-Agent"]): ...
```

### 커스텀 헤더

```python
@Controller("/api")
class ApiController:
    @Get("/data")
    def get_data(
        self,
        api_key: HttpHeader["X-API-Key"],
        request_id: HttpHeader["X-Request-ID"]
    ) -> dict:
        return {
            "api_key": api_key.value,
            "request_id": request_id.value
        }
```

**요청:**
```http
GET /api/data HTTP/1.1
X-API-Key: secret123
X-Request-ID: req-abc-123
```

## HttpCookie 주입

### 기본 사용법

```python
from vessel import Controller, Get, HttpCookie

@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, session_id: HttpCookie) -> dict:
        return {
            "name": session_id.name,    # "session_id"
            "value": session_id.value   # "abc123..."
        }
```

**요청:**
```http
GET /api/user HTTP/1.1
Cookie: session_id=abc123xyz
```

### 여러 쿠키 주입

```python
@Controller("/api")
class UserController:
    @Get("/preferences")
    def get_preferences(
        self,
        session_id: HttpCookie,
        theme: HttpCookie,
        language: HttpCookie
    ) -> dict:
        return {
            "session": session_id.value,
            "theme": theme.value,
            "language": language.value
        }
```

**요청:**
```http
GET /api/preferences HTTP/1.1
Cookie: session_id=abc123; theme=dark; language=en
```

### 브래킷 문법 (명시적 쿠키 이름 지정)

```python
@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, sid: HttpCookie["session_id"]) -> dict:
        return {
            "name": sid.name,    # "session_id"
            "value": sid.value
        }
```

## 실전 예제

### API 키 인증

```python
from vessel import Controller, Get, HttpHeader, HttpResponse, HttpStatus

@Controller("/api")
class SecureController:
    @Get("/data")
    def get_secure_data(self, api_key: HttpHeader["X-API-Key"]) -> HttpResponse:
        # API 키 검증
        valid_keys = ["key123", "key456"]
        
        if api_key.value not in valid_keys:
            return HttpResponse(
                status_code=HttpStatus.UNAUTHORIZED,
                body={"error": "Invalid API key"}
            )
        
        return HttpResponse(
            status_code=HttpStatus.OK,
            body={"data": "secure data"}
        )
```

### 세션 기반 인증

```python
from vessel import Controller, Get, HttpCookie, HttpResponse, HttpStatus, Component

@Component
class SessionService:
    def __init__(self):
        self.sessions = {
            "session123": {"user_id": "user1", "username": "john"},
            "session456": {"user_id": "user2", "username": "jane"}
        }
    
    def get_user(self, session_id: str):
        return self.sessions.get(session_id)

@Controller("/api")
class UserController:
    session_service: SessionService
    
    @Get("/me")
    def get_current_user(self, session_id: HttpCookie) -> HttpResponse:
        user = self.session_service.get_user(session_id.value)
        
        if not user:
            return HttpResponse(
                status_code=HttpStatus.UNAUTHORIZED,
                body={"error": "Invalid session"}
            )
        
        return HttpResponse(
            status_code=HttpStatus.OK,
            body=user
        )
```

**요청:**
```http
GET /api/me HTTP/1.1
Cookie: session_id=session123
```

**응답:**
```json
{
  "user_id": "user1",
  "username": "john"
}
```

### 헤더 기반 다국어 지원

```python
@Controller("/api")
class LocaleController:
    @Get("/greeting")
    def greet(
        self,
        accept_language: HttpHeader,
        user_agent: HttpHeader
    ) -> dict:
        # Accept-Language 헤더 파싱
        lang = accept_language.value.split(",")[0].split("-")[0]
        
        greetings = {
            "en": "Hello",
            "ko": "안녕하세요",
            "ja": "こんにちは",
            "es": "Hola"
        }
        
        return {
            "greeting": greetings.get(lang, greetings["en"]),
            "language": lang,
            "user_agent": user_agent.value
        }
```

**요청:**
```http
GET /api/greeting HTTP/1.1
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
User-Agent: Mozilla/5.0
```

**응답:**
```json
{
  "greeting": "안녕하세요",
  "language": "ko",
  "user_agent": "Mozilla/5.0"
}
```

### Content Negotiation

```python
@Controller("/api")
class DataController:
    @Get("/data")
    def get_data(self, accept: HttpHeader) -> HttpResponse:
        data = {"id": 1, "name": "Item"}
        
        # Accept 헤더에 따라 응답 형식 결정
        if "application/json" in accept.value:
            return HttpResponse(
                status_code=HttpStatus.OK,
                body=data,
                headers={"Content-Type": "application/json"}
            )
        elif "text/plain" in accept.value:
            return HttpResponse(
                status_code=HttpStatus.OK,
                body=f"ID: {data['id']}, Name: {data['name']}",
                headers={"Content-Type": "text/plain"}
            )
        else:
            return HttpResponse(
                status_code=HttpStatus.NOT_ACCEPTABLE,
                body={"error": "Unsupported media type"}
            )
```

## Optional 지원

헤더와 쿠키는 `Optional` 타입으로 선언할 수 있습니다:

### Optional HttpHeader

```python
from typing import Optional
from vessel import Controller, Get, HttpHeader

@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, authorization: Optional[HttpHeader]) -> dict:
        if authorization:
            return {
                "auth": authorization.value,
                "name": authorization.name
            }
        return {"auth": None}
```

**요청 (헤더 없음):**
```http
GET /api/user HTTP/1.1
```

**응답:**
```json
{
  "auth": null
}
```

**요청 (헤더 있음):**
```http
GET /api/user HTTP/1.1
Authorization: Bearer token123
```

**응답:**
```json
{
  "auth": "Bearer token123",
  "name": "Authorization"
}
```

### Optional HttpCookie

```python
@Controller("/api")
class UserController:
    @Get("/user")
    def get_user(self, remember_me: Optional[HttpCookie]) -> dict:
        if remember_me:
            return {
                "value": remember_me.value,
                "name": remember_me.name
            }
        return {"value": None}
```

### Optional with 브래킷 문법

```python
@Controller("/api")
class SecureController:
    @Get("/data")
    def get_data(
        self, 
        auth: Optional[HttpHeader["Authorization"]]
    ) -> dict:
        if auth:
            return {"authenticated": True, "token": auth.value}
        return {"authenticated": False}
```

**중요:**
- 값이 없을 때 `None`이 주입됩니다
- `if` 문으로 존재 여부를 확인하세요
- 기본값(`= None`)은 선택 사항입니다 (없어도 작동)

## 정리

### 지원하는 기능

**HttpHeader:**
- ✅ 자동 이름 변환 (snake_case → Title-Case)
- ✅ 명시적 헤더 이름 지정
- ✅ 브래킷 문법
- ✅ 여러 헤더 동시 주입
- ✅ 커스텀 헤더 지원
- ✅ Optional 타입 지원

**HttpCookie:**
- ✅ 자동 쿠키 이름 매칭
- ✅ 명시적 쿠키 이름 지정
- ✅ 브래킷 문법
- ✅ 여러 쿠키 동시 주입
- ✅ Optional 타입 지원

### 필수 vs Optional

```python
# 필수 헤더 - 없으면 400 에러
def handler(self, authorization: HttpHeader): ...

# 선택적 헤더 - 없으면 None (기본값은 선택 사항)
def handler(self, authorization: Optional[HttpHeader]): ...
```

### 지원하지 않는 기능

- ❌ 헤더/쿠키 값의 자동 타입 변환 (모두 str)

### 권장 사항

1. **필수 vs Optional 명확히 구분**
   ```python
   # 필수 - 인증이 반드시 필요한 경우
   authorization: HttpHeader["Authorization"]
   
   # 선택적 - 있으면 사용하고 없어도 괜찮은 경우
   theme: Optional[HttpCookie]
   ```

2. **브래킷 문법 사용**: 가장 명확하고 타입 안전
   ```python
   agent: HttpHeader["User-Agent"]
   ```

3. **Optional은 기본값 선택 사항**
   ```python
   # 둘 다 가능
   auth: Optional[HttpHeader]
   auth: Optional[HttpHeader] = None
   ```

4. **검증 추가**: 헤더/쿠키 값은 항상 검증
   ```python
   if authorization and authorization.value:
       # 처리
   ```

5. **보안**: 민감한 정보는 쿠키보다 헤더 사용 권장
   ```python
   authorization: HttpHeader["Authorization"]
   ```
