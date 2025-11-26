# Vessel Framework - Development Tasks

> Last Updated: 2025-11-26 | Version: 0.1.0-alpha

---

## 📊 Current Status

- **85/85 Tests Passing** ✅
- **32 Files** - Well-structured architecture
- **Core Features Complete**: DI, Web, Middleware, Validation, FileUpload

---

## ✅ Completed Phases

### Phase 1: Core DI Framework ✅
- Container, DependencyGraph, ContainerManager
- @Component, @Configuration, @Factory
- Type-based dependency injection
- Singleton pattern

### Phase 2: Web Framework ✅
- HttpRequest/HttpResponse, RouteHandler
- Path parameters with auto type conversion
- @Controller, @Get, @Post, @Put, @Delete, @Patch
- Middleware chain with early return support
- Application facade, DevServer

### Phase 3: Code Quality ✅
- SRP: Split Application into 4 classes
- Restructured vessel/ by feature
- Separated di/core and di/utils

### Phase 4: Core Features (In Progress)
- **✅ Validation** (13 tests)
  - ParameterValidator: Type conversion & validation
  - ValidationError: Auto 400 responses
  - Multi-error collection with detailed messages
  - Query/Path/Body parameter validation
  - **Strong typing**: Missing type hints → Error
  
- **✅ File Upload** (12 tests)
  - UploadedFile class: read(), save(), secure_filename()
  - **Type-based injection**: file: UploadedFile
  - Support: UploadedFile, Optional[UploadedFile], list[UploadedFile]
  - File size validation, MIME type checking
  - Filename sanitization (path traversal prevention)
  - **Strong typing**: File params require explicit type hints

---

## 📁 Project Structure

```
vessel/
├── di/
│   ├── core/           # Container, ContainerManager, DependencyGraph
│   └── utils/          # Scanner, Collector, Initializer, Analyzer
├── decorators/
│   ├── di/             # @Component, @Configuration, @Factory
│   ├── web/            # @Controller, HTTP mappings
│   └── handler/        # HandlerContainer, Interceptors
├── http/
│   ├── request.py      # HttpRequest, HttpResponse
│   ├── router.py       # RouteHandler
│   ├── file_upload.py  # UploadedFile ✨ NEW
│   └── validation.py   # ParameterValidator, ValidationError
└── web/
    ├── application.py, initializer.py, request_handler.py, server.py
    └── middleware/     # MiddlewareChain, CorsMiddleware
```

---

## 🚀 Next Tasks

### Phase 4 Completion

#### Web Features
- [ ] **Static Files** - `app.serve_static("/static", "./public")`
- [ ] **Response Streaming** - Large file downloads

#### Middleware
- [ ] **CompressionMiddleware** - gzip compression
- [ ] **RateLimitMiddleware** - Rate limiting
- [ ] **SessionMiddleware** - Session management
- [ ] **SecurityHeadersMiddleware** - Security headers
- [ ] **Middleware Priority** - Order control

---

### Phase 5: Developer Experience

#### CLI Tools
- [ ] `vessel create my-project` - Project scaffolding
- [ ] `vessel new controller UserController` - Code generation

#### Dev Server
- [ ] **Hot Reload** - File change detection
- [ ] **Enhanced Error Pages** - Stack traces with syntax highlighting
- [ ] **Colorful Logging** - Better log output

#### Debugging
- [ ] **DI Inspector** - Component graph visualization
- [ ] **Health Check Endpoint** - `/health`

#### Testing
- [ ] **@WebTest Decorator** - Test utilities
- [ ] **Test Client** - HTTP client for testing
- [ ] **Mock Components** - Dependency mocking

---

### Phase 6: Production Ready

#### Performance
- [ ] **Async Support** - `async def` handlers, ASGI
- [ ] **Caching** - `@Cacheable`, Redis integration

#### Security
- [ ] **Authentication/Authorization** - JWT, `@Secured(roles=["admin"])`
- [ ] **CSRF Protection** - Token generation/validation

#### Monitoring
- [ ] **Metrics** - Prometheus integration
- [ ] **Structured Logging** - structlog (JSON)

---

### Phase 7: Ecosystem

- [ ] **ORM Integration** - SQLAlchemy, `@Repository`
- [ ] **Database Migration** - Alembic
- [ ] **Messaging** - RabbitMQ/Kafka, `@MessageListener`
- [ ] **HTTP Client** - `@HttpClient` decorator

---

## 📈 Test Coverage

| File | Tests | Status |
|------|-------|--------|
| test_application.py | 12 | ✅ |
| test_component.py | 5 | ✅ |
| test_container.py | 4 | ✅ |
| test_dependency.py | 9 | ✅ |
| test_handler.py | 14 | ✅ |
| test_integration.py | 7 | ✅ |
| test_integration_advanced.py | 5 | ✅ |
| test_middleware_integration.py | 4 | ✅ |
| test_validation.py | 13 | ✅ |
| test_file_upload.py | 12 | ✅ |
| **Total** | **85** | **✅** |

---

## 🛠 Tech Stack

**Current**: Python 3.12+, pytest

**Future**: Click, watchdog, asyncio, Redis, SQLAlchemy

---

## 🚨 Design Constraints

- **❌ NO Constructor Injection**: Field injection only (explicit design choice)
- **❌ NO Lazy Initialization**: Components initialized eagerly
- **❌ NO Scope Extensions**: Singleton only (no prototype/request scopes)
- **❌ NO Qualifier Support**: Single bean per type
- **❌ NO Template Engine**: API-focused framework (no Jinja2)
- **✅ STRONG TYPING**: All parameters must have type hints (except self/HttpRequest)

---

## 💡 Key Design Principles

### Type Safety First
```python
# ❌ BAD - No type hint
def upload(self, file):  # Error: Missing type hint

# ✅ GOOD - Explicit type
def upload(self, file: UploadedFile):  # OK
```

### Explicit > Implicit
```python
# File upload requires explicit type annotation
def upload(self, file: UploadedFile):  # Only works with type hint
    return {"name": file.filename}
```

### Convention over Configuration
```python
@Controller("/api")
class UserController:
    @Get("/users/{id}")
    def get_user(self, id: int) -> dict:  # Path param auto-injected
        return {"id": id}
```

---

## 📝 Quick Start

```bash
# Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pytest

# Test
pytest -v

# Run
python -m vessel.web.server
```

---

## 💻 Example Usage

```python
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Post, Get
from vessel.http.file_upload import UploadedFile
from typing import Optional

@Controller("/api")
class FileController:
    @Post("/upload")
    def upload(self, file: UploadedFile, title: str, description: str = "") -> dict:
        # Validation happens automatically
        # file is guaranteed to be UploadedFile
        # title is required string
        # description is optional with default
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            return {"error": "File too large"}
        
        safe_name = file.secure_filename()
        file.save(f"./uploads/{safe_name}")
        
        return {
            "filename": safe_name,
            "size": file.size,
            "title": title
        }
    
    @Get("/files")
    def list_files(self, page: int = 1, limit: int = 10) -> dict:
        # Query params auto-validated and converted
        return {"page": page, "limit": limit}
```

---

## 🎯 Commit Convention

```
<type>: <subject>

Types: feat, fix, refactor, test, docs, chore
```

**Example**:
```
feat: Add file upload support with type-based injection

- Implement UploadedFile class
- Add type hint validation
- Support Optional[UploadedFile] and list[UploadedFile]
```

---

**Version**: 0.1.0-alpha  
**Status**: Active Development 🚧  
**License**: MIT
