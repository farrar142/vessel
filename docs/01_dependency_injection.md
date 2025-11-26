# Dependency Injection (의존성 주입)

> 테스트 기반: `tests/test_component.py`, `tests/test_dependency.py`, `tests/test_container.py`

## 개요

Vessel 프레임워크는 **필드 주입(Field Injection)** 방식의 의존성 주입을 제공합니다.
- ✅ **필드 주입**: 클래스 필드에 타입 힌트로 의존성 선언
- ❌ **생성자 주입**: 지원하지 않음

## @Component 데코레이터

컴포넌트로 등록할 클래스에 `@Component` 데코레이터를 사용합니다.

### 기본 사용법

```python
from vessel import Component

@Component
class UserService:
    def get_user(self, user_id: str):
        return {"id": user_id, "name": "John"}
```

### 필드 주입으로 의존성 선언

**필드에 타입 힌트를 추가하면 자동으로 주입됩니다:**

```python
from vessel import Component

@Component
class UserRepository:
    def find_by_id(self, user_id: str):
        return {"id": user_id, "email": "user@example.com"}

@Component
class UserService:
    repository: UserRepository  # 👈 필드 주입
    
    def get_user_email(self, user_id: str):
        user = self.repository.find_by_id(user_id)
        return user["email"]
```

**중요:**
- 타입 힌트가 **필수**입니다
- `__init__` 메서드에 의존성을 선언하지 않습니다 (생성자 주입 아님)
- 필드 선언만으로 자동 주입됩니다

### 싱글톤

모든 컴포넌트는 **자동으로 싱글톤**으로 관리됩니다.

```python
@Component
class DatabaseConnection:
    def __init__(self):
        print("DB Connection created")  # 한 번만 출력됨

@Component
class ServiceA:
    db: DatabaseConnection

@Component  
class ServiceB:
    db: DatabaseConnection

# ServiceA와 ServiceB는 같은 DatabaseConnection 인스턴스를 공유
```

## @Configuration과 @Factory

복잡한 객체 생성이나 외부 라이브러리 통합을 위한 패턴입니다.

### @Configuration

설정 클래스를 정의합니다:

```python
from vessel import Configuration, Factory, Component

@Configuration
class AppConfig:
    @Factory
    def database_connection(self) -> DatabaseConnection:
        # 복잡한 초기화 로직
        conn = DatabaseConnection(
            host="localhost",
            port=5432,
            username="admin",
            password="secret"
        )
        conn.connect()
        return conn
    
    @Factory
    def cache_manager(self, db: DatabaseConnection) -> CacheManager:
        # Factory 메서드도 의존성 주입을 받을 수 있음
        return CacheManager(db)
```

### @Factory

Factory 메서드는 다음 특징이 있습니다:

1. **반환 타입 힌트 필수**: 무엇을 생성하는지 명시
2. **파라미터로 의존성 주입 가능**: 다른 컴포넌트를 주입받을 수 있음
3. **싱글톤으로 관리**: 생성된 객체는 한 번만 만들어짐

```python
@Configuration
class ServiceConfig:
    @Factory
    def email_service(self) -> EmailService:
        return EmailService(smtp_host="smtp.gmail.com")
    
    @Factory
    def notification_service(
        self, 
        email: EmailService  # 👈 다른 Factory가 만든 객체 주입
    ) -> NotificationService:
        return NotificationService(email)
```

## 의존성 그래프

Vessel은 자동으로 의존성 그래프를 구성하고 올바른 순서로 초기화합니다.

### 자동 순서 결정

```python
@Component
class DatabaseConnection:
    pass

@Component
class UserRepository:
    db: DatabaseConnection  # DB에 의존

@Component
class UserService:
    repository: UserRepository  # Repository에 의존

# 자동 초기화 순서: DatabaseConnection → UserRepository → UserService
```

### 순환 의존성 감지

순환 의존성이 있으면 애플리케이션 시작 시 에러가 발생합니다:

```python
@Component
class ServiceA:
    service_b: 'ServiceB'  # B에 의존

@Component
class ServiceB:
    service_a: ServiceA  # A에 의존

# ❌ ValueError: Circular dependency detected
```

## Application 초기화

모든 컴포넌트는 `Application.initialize()` 호출 시 자동으로 스캔되고 초기화됩니다:

```python
from vessel import Application

app = Application("__main__")  # 현재 패키지를 스캔
app.initialize()  # 모든 @Component, @Configuration이 등록됨
```

### 여러 패키지 스캔

```python
app = Application("my_app", "plugins", "extensions")
app.initialize()
```

## 컴포넌트 조회

초기화 후에는 `Application.get_instance()`로 컴포넌트를 가져올 수 있습니다:

```python
app = Application("__main__")
app.initialize()

# 타입으로 조회
user_service = app.get_instance(UserService)
user_service.get_user("123")
```

## 내장 타입은 주입되지 않음

`str`, `int`, `bool` 등 파이썬 내장 타입은 의존성으로 간주되지 않습니다:

```python
@Component
class MyService:
    name: str  # ❌ 주입되지 않음 (내장 타입)
    age: int   # ❌ 주입되지 않음
```

이런 값들은 설정 파일이나 환경 변수에서 읽어야 합니다.

## 정리

### ✅ 지원하는 기능
- 필드 주입 (타입 힌트 기반)
- 자동 싱글톤 관리
- 의존성 그래프 자동 구성
- Factory 패턴
- 순환 의존성 감지
- 여러 패키지 스캔

### ❌ 지원하지 않는 기능
- 생성자 주입 (Constructor Injection)
- Optional 의존성 (모든 의존성은 필수)
- 내장 타입 주입 (str, int, bool 등)
- Prototype 스코프 (모두 싱글톤)

## 예제

### 전체 예제

```python
from vessel import Application, Component, Configuration, Factory

# 데이터 계층
@Component
class Database:
    def query(self, sql: str):
        return [{"id": 1, "name": "John"}]

# 리포지토리 계층
@Component
class UserRepository:
    db: Database
    
    def find_all(self):
        return self.db.query("SELECT * FROM users")

# 서비스 계층
@Component
class UserService:
    repository: UserRepository
    
    def get_users(self):
        return self.repository.find_all()

# 외부 라이브러리 통합
@Configuration
class ExternalConfig:
    @Factory
    def redis_client(self) -> RedisClient:
        client = RedisClient(host="localhost", port=6379)
        client.connect()
        return client

# 애플리케이션 시작
app = Application("__main__")
app.initialize()

# 사용
user_service = app.get_instance(UserService)
users = user_service.get_users()
```
