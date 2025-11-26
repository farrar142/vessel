# Project Rename: PyDI → Vessel

## Overview
프로젝트 이름이 `PyDI`에서 `Vessel`로 변경되었습니다.

## Changes Made

### 1. Directory Structure
```
pydi/ → vessel/
```

### 2. Import Statements
모든 Python 파일의 import 문이 변경되었습니다:
```python
# Before
from pydi import Component
from pydi.core.container import Container

# After
from vessel import Component
from vessel.core.container import Container
```

### 3. Package Configuration
- **setup.py**: 패키지 이름이 `pydi`에서 `vessel`로 변경
- **vessel/__init__.py**: 프로젝트 설명 업데이트

### 4. Documentation
다음 문서들이 업데이트되었습니다:
- README.md
- TESTING.md
- REFACTORING.md

### 5. Test Results
모든 테스트가 성공적으로 통과했습니다:
- **44개 테스트** 모두 통과 ✅
- **73% 코드 커버리지** 유지

## Usage Examples

### Basic Component
```python
from vessel import Component, ContainerManager

@Component
class MyService:
    pass

ContainerManager.component_scan("my_package")
ContainerManager.initialize()
```

### HTTP Controller
```python
from vessel import Controller, Get

@Controller("/api")
class MyController:
    @Get("/hello")
    def hello(self):
        return "Hello from Vessel!"
```

### Custom Decorator with Interceptor
```python
from vessel import HandlerInterceptor, create_handler_decorator, Component

@Component
class LoggingInterceptor(HandlerInterceptor):
    def before(self, *args, **kwargs):
        print("Before handler execution")
    
    def after(self, result, *args, **kwargs):
        print("After handler execution")
        return result

# Create custom decorator with dependency injection
CustomDecorator = create_handler_decorator(
    "CustomDecorator",
    [LoggingInterceptor],
    inject_dependencies=True
)
```

## Migration Guide for Users

기존 `pydi`를 사용하던 프로젝트를 `vessel`로 마이그레이션하려면:

1. **Import 문 변경**:
   ```bash
   # 모든 Python 파일에서 일괄 변경
   find . -name "*.py" -type f -exec sed -i 's/from pydi/from vessel/g' {} +
   find . -name "*.py" -type f -exec sed -i 's/import pydi/import vessel/g' {} +
   ```

2. **패키지 재설치**:
   ```bash
   pip uninstall pydi
   pip install vessel
   ```

3. **테스트 실행**:
   ```bash
   python -m pytest tests/ -v
   ```

## Notes
- 모든 API는 동일하게 유지됩니다 (Backward Compatible)
- 내부 구조나 기능에는 변경이 없습니다
- 단순히 패키지 이름만 변경되었습니다
