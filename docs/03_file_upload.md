# File Upload

> 테스트 기반: `tests/test_file_upload.py`

## 개요

Vessel은 `multipart/form-data` 형식의 파일 업로드를 지원합니다.
파일은 `UploadedFile` 객체로 자동 변환되어 핸들러에 주입됩니다.

## 기본 사용법

### 단일 파일 업로드

```python
from vessel import Controller, Post, UploadedFile

@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        return {
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type
        }
```

**요청 예시:**
```http
POST /api/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

Hello, World!
------WebKitFormBoundary--
```

**응답:**
```json
{
  "filename": "test.txt",
  "size": 13,
  "content_type": "text/plain"
}
```

## UploadedFile 클래스

### 속성

```python
file: UploadedFile

# 파일 이름
file.filename  # "test.txt"

# 파일 크기 (바이트)
file.size  # 13

# MIME 타입
file.content_type  # "text/plain"
```

### 메서드

#### read() - 파일 내용 읽기

```python
@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        content = file.read()  # bytes
        text = content.decode('utf-8')  # str
        return {
            "content": text,
            "length": len(content)
        }
```

#### save() - 파일 저장

```python
import os

@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        # 저장 경로 지정
        upload_dir = "/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        
        return {
            "message": "File saved",
            "path": filepath
        }
```

**경로 탐색 공격 방지:**
`save()` 메서드는 자동으로 파일명을 안전하게 처리합니다:

```python
file.filename = "../../../etc/passwd"
file.save("/uploads/user.txt")
# 실제로 저장되는 경로: /uploads/etc_passwd (안전하게 변환됨)
```

#### secure_filename() - 안전한 파일명 생성

```python
@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        # 원본: "my file (1).txt"
        # 안전한 파일명: "my_file_1.txt"
        safe_name = file.secure_filename()
        
        return {
            "original": file.filename,
            "safe": safe_name
        }
```

**변환 규칙:**
- 공백 → 언더스코어 `_`
- 특수문자 제거
- 경로 구분자 제거 (`/`, `\`)
- ASCII가 아닌 문자 제거

## 여러 파일 업로드

### List[UploadedFile]

```python
from typing import List

@Controller("/api")
class FileController:
    @Post("/upload-multiple")
    def upload_files(self, files: List[UploadedFile]) -> dict:
        return {
            "count": len(files),
            "files": [
                {
                    "filename": f.filename,
                    "size": f.size
                }
                for f in files
            ]
        }
```

**요청 예시:**
```http
POST /api/upload-multiple
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="files"; filename="file1.txt"
Content-Type: text/plain

Content 1
------WebKitFormBoundary
Content-Disposition: form-data; name="files"; filename="file2.txt"
Content-Type: text/plain

Content 2
------WebKitFormBoundary--
```

## 파일과 다른 데이터 함께 받기

```python
@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(
        self,
        file: UploadedFile,
        title: str,
        description: str = ""
    ) -> dict:
        return {
            "file": {
                "filename": file.filename,
                "size": file.size
            },
            "metadata": {
                "title": title,
                "description": description
            }
        }
```

**요청 예시:**
```http
POST /api/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="doc.pdf"
Content-Type: application/pdf

<binary data>
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

Important Document
------WebKitFormBoundary
Content-Disposition: form-data; name="description"

This is a description
------WebKitFormBoundary--
```

## 파일 검증

### 크기 검증

```python
@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        
        if file.size > MAX_SIZE:
            from vessel import HttpResponse, HttpStatus
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": "File too large"}
            )
        
        return {"message": "File uploaded"}
```

### MIME 타입 검증

```python
@Controller("/api")
class FileController:
    @Post("/upload-image")
    def upload_image(self, file: UploadedFile) -> dict:
        ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"]
        
        if file.content_type not in ALLOWED_TYPES:
            from vessel import HttpResponse, HttpStatus
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": "Invalid file type"}
            )
        
        file.save(f"/uploads/images/{file.secure_filename()}")
        return {"message": "Image uploaded"}
```

### 확장자 검증

```python
import os

@Controller("/api")
class FileController:
    @Post("/upload")
    def upload_file(self, file: UploadedFile) -> dict:
        ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
        
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            from vessel import HttpResponse, HttpStatus
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": f"Extension {ext} not allowed"}
            )
        
        return {"message": "File uploaded"}
```

## 실전 예제

### 이미지 업로드 서비스

```python
from vessel import Controller, Post, UploadedFile, HttpResponse, HttpStatus, Component
import os
import uuid
from datetime import datetime

@Component
class FileStorageService:
    def __init__(self):
        self.base_dir = "/var/uploads"
        os.makedirs(self.base_dir, exist_ok=True)
    
    def save_file(self, file: UploadedFile, subdir: str) -> str:
        # 날짜별 디렉토리 생성
        today = datetime.now().strftime("%Y/%m/%d")
        upload_dir = os.path.join(self.base_dir, subdir, today)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 유니크한 파일명 생성
        unique_id = str(uuid.uuid4())
        _, ext = os.path.splitext(file.secure_filename())
        filename = f"{unique_id}{ext}"
        
        # 파일 저장
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        return filepath

@Controller("/api/images")
class ImageController:
    storage: FileStorageService
    
    @Post("/upload")
    def upload_image(self, file: UploadedFile) -> HttpResponse:
        # 크기 검증
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if file.size > MAX_SIZE:
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": "Image must be smaller than 5MB"}
            )
        
        # MIME 타입 검증
        ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in ALLOWED_TYPES:
            return HttpResponse(
                status_code=HttpStatus.BAD_REQUEST,
                body={"error": "Only JPEG, PNG, GIF, WebP images are allowed"}
            )
        
        # 파일 저장
        try:
            filepath = self.storage.save_file(file, "images")
            return HttpResponse(
                status_code=HttpStatus.CREATED,
                body={
                    "message": "Image uploaded successfully",
                    "filename": file.filename,
                    "path": filepath,
                    "size": file.size,
                    "content_type": file.content_type
                }
            )
        except Exception as e:
            return HttpResponse(
                status_code=HttpStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)}
            )
```

## 주의사항

1. **메모리**: 큰 파일은 메모리에 전체를 로드하므로 크기 제한 필요
2. **보안**: 항상 파일명을 `secure_filename()`으로 정제
3. **검증**: 크기, MIME 타입, 확장자를 반드시 검증
4. **스토리지**: 프로덕션에서는 S3 같은 클라우드 스토리지 사용 권장
