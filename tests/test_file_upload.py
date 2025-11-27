"""
File Upload 기능 테스트
"""

import pytest
from vessel.decorators.di.component import Component
from vessel.decorators.web.controller import Controller
from vessel.decorators.web.mapping import Post
from vessel.web.application import Application
from vessel.web.http.request import HttpRequest


class TestBasicFileUpload:
    """기본 파일 업로드 테스트"""

    def test_single_file_upload_success(self):
        """단일 파일 업로드 성공"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                # file은 UploadedFile 인스턴스
                return {
                    "filename": file.filename,
                    "size": file.size,
                    "content_type": file.content_type,
                }

        app = Application("__main__")
        app.initialize()

        # multipart/form-data 시뮬레이션
        file_content = b"Hello, World!"
        request = HttpRequest(
            method="POST",
            path="/api/upload",
            headers={
                "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
            },
            body={
                "file": {
                    "filename": "test.txt",
                    "content": file_content,
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["filename"] == "test.txt"
        assert response.body["size"] == len(file_content)
        assert response.body["content_type"] == "text/plain"

    def test_file_content_read(self):
        """파일 내용 읽기"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                content = file.read()
                return {"content": content.decode("utf-8"), "size": len(content)}

        app = Application("__main__")
        app.initialize()

        file_content = b"Test file content"
        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "test.txt",
                    "content": file_content,
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["content"] == "Test file content"
        assert response.body["size"] == len(file_content)

    def test_file_save(self):
        """파일 저장"""
        import tempfile
        import os
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                # 임시 디렉토리에 저장
                temp_dir = tempfile.gettempdir()
                save_path = os.path.join(temp_dir, file.filename)
                file.save(save_path)

                # 파일이 실제로 저장되었는지 확인
                exists = os.path.exists(save_path)

                # 정리
                if exists:
                    os.remove(save_path)

                return {"saved": exists, "path": save_path}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "test.txt",
                    "content": b"Save me!",
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["saved"] is True


class TestMultipleFileUpload:
    """다중 파일 업로드 테스트"""

    def test_multiple_files_upload(self):
        """여러 파일 동시 업로드"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload-multiple")
            def upload_files(self, files: list[UploadedFile]) -> dict:
                # files는 UploadedFile 리스트
                return {
                    "count": len(files),
                    "filenames": [f.filename for f in files],
                    "total_size": sum(f.size for f in files),
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload-multiple",
            body={
                "files": [
                    {
                        "filename": "file1.txt",
                        "content": b"Content 1",
                        "content_type": "text/plain",
                    },
                    {
                        "filename": "file2.txt",
                        "content": b"Content 2",
                        "content_type": "text/plain",
                    },
                ]
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["count"] == 2
        assert "file1.txt" in response.body["filenames"]
        assert "file2.txt" in response.body["filenames"]
        assert response.body["total_size"] == 18  # 9 + 9

    def test_mixed_form_data_and_files(self):
        """폼 데이터와 파일 혼합"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload-with-data")
            def upload_with_data(
                self, file: UploadedFile, title: str, description: str = ""
            ) -> dict:
                return {
                    "filename": file.filename,
                    "title": title,
                    "description": description,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload-with-data",
            body={
                "file": {
                    "filename": "document.pdf",
                    "content": b"PDF content",
                    "content_type": "application/pdf",
                },
                "title": "Important Document",
                "description": "This is important",
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["filename"] == "document.pdf"
        assert response.body["title"] == "Important Document"
        assert response.body["description"] == "This is important"


class TestFileValidation:
    """파일 검증 테스트"""

    def test_file_size_limit(self):
        """파일 크기 제한 검증"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                max_size = 1024 * 1024  # 1MB
                if file.size > max_size:
                    from vessel.web.http.request import HttpResponse

                    return HttpResponse(
                        status_code=400, body={"error": "File too large"}
                    )

                return {"filename": file.filename, "size": file.size}

        app = Application("__main__")
        app.initialize()

        # 큰 파일
        large_content = b"x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "large.txt",
                    "content": large_content,
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        assert "error" in response.body

    def test_allowed_file_types(self):
        """허용된 파일 타입 검증"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                allowed_types = ["image/jpeg", "image/png", "image/gif"]
                if file.content_type not in allowed_types:
                    from vessel.web.http.request import HttpResponse

                    return HttpResponse(
                        status_code=400, body={"error": "Invalid file type"}
                    )

                return {"filename": file.filename, "content_type": file.content_type}

        app = Application("__main__")
        app.initialize()

        # 허용되지 않은 타입
        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "document.pdf",
                    "content": b"PDF content",
                    "content_type": "application/pdf",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 400
        assert "error" in response.body

    def test_missing_file_parameter(self):
        """파일 파라미터 누락"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                return {"filename": file.filename}

        app = Application("__main__")
        app.initialize()

        # 파일 없이 요청
        request = HttpRequest(method="POST", path="/api/upload", body={})

        response = app.handle_request(request)

        # ValidationError 발생 → 400
        assert response.status_code == 400


class TestFilenameSanitization:
    """파일명 sanitization 테스트"""

    def test_safe_filename(self):
        """안전한 파일명 생성"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                # secure_filename()을 사용하여 안전한 파일명 생성
                safe_name = file.secure_filename()
                return {"original": file.filename, "safe": safe_name}

        app = Application("__main__")
        app.initialize()

        # 위험한 파일명
        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "../../etc/passwd",
                    "content": b"malicious",
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["original"] == "../../etc/passwd"
        # 경로 순회 문자 제거됨
        assert ".." not in response.body["safe"]
        assert "/" not in response.body["safe"]


class TestTypeHintBasedFileInjection:
    """타입 힌트 기반 파일 주입 테스트"""

    def test_without_type_hint_raises_error(self):
        """타입 힌트가 없으면 에러 발생"""

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file) -> dict:
                # file 타입 힌트가 없으면 에러
                return {"filename": "test"}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={"file": "value"},
        )

        response = app.handle_request(request)

        # 타입 힌트 없는 파라미터 → 500 에러
        assert response.status_code == 500
        assert (
            "type hint" in response.body.get("message", "").lower()
            or "annotation" in response.body.get("message", "").lower()
        )

    def test_with_uploadedfile_type_hint(self):
        """UploadedFile 타입 힌트가 있으면 파일로 처리"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: UploadedFile) -> dict:
                return {"is_uploaded_file": isinstance(file, UploadedFile)}

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "test.txt",
                    "content": b"content",
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request)

        assert response.status_code == 200
        assert response.body["is_uploaded_file"] is True

    def test_optional_uploadedfile(self):
        """Optional[UploadedFile] 지원"""
        from vessel.web.http.uploaded_file import UploadedFile
        from typing import Optional

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, file: Optional[UploadedFile] = None) -> dict:
                if file is None:
                    return {"has_file": False}
                return {"has_file": True, "filename": file.filename}

        app = Application("__main__")
        app.initialize()

        # 파일이 있는 경우
        request_with_file = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "file": {
                    "filename": "test.txt",
                    "content": b"content",
                    "content_type": "text/plain",
                }
            },
        )

        response = app.handle_request(request_with_file)
        assert response.status_code == 200
        assert response.body["has_file"] is True

        # 파일이 없는 경우
        request_without_file = HttpRequest(
            method="POST",
            path="/api/upload",
            body={},
        )

        response = app.handle_request(request_without_file)
        assert response.status_code == 200
        assert response.body["has_file"] is False


class TestExplicitFileKeySpecification:
    """명시적 파일 키 지정 테스트 (Annotated 구문)"""

    def test_bracket_syntax_single_file(self):
        """UploadedFile["key"] 구문으로 명시적 키 지정"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(self, avatar: UploadedFile["profile_pic"]) -> dict:
                # avatar 파라미터는 "profile_pic" 키로 전송된 파일을 받음
                return {
                    "param_name": "avatar",
                    "filename": avatar.filename,
                    "size": avatar.size,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "profile_pic": {  # 명시적 키
                    "filename": "avatar.jpg",
                    "content": b"fake image data",
                    "content_type": "image/jpeg",
                }
            },
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["param_name"] == "avatar"
        assert response.body["filename"] == "avatar.jpg"
        assert response.body["size"] == 15

    def test_bracket_syntax_with_optional(self):
        """Optional[UploadedFile["key"]] 구문 테스트"""
        from vessel.web.http.uploaded_file import UploadedFile
        from typing import Optional

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_file(
                self, avatar: Optional[UploadedFile["profile_pic"]] = None
            ) -> dict:
                if avatar is None:
                    return {"has_file": False}
                return {"has_file": True, "filename": avatar.filename}

        app = Application("__main__")
        app.initialize()

        # 파일이 있는 경우
        request_with_file = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "profile_pic": {
                    "filename": "avatar.jpg",
                    "content": b"data",
                    "content_type": "image/jpeg",
                }
            },
        )

        response = app.handle_request(request_with_file)
        assert response.status_code == 200
        assert response.body["has_file"] is True

        # 파일이 없는 경우
        request_without_file = HttpRequest(
            method="POST",
            path="/api/upload",
            body={},
        )

        response = app.handle_request(request_without_file)
        assert response.status_code == 200
        assert response.body["has_file"] is False

    def test_bracket_syntax_with_list(self):
        """list[UploadedFile["key"]] 구문 테스트"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_files(self, images: list[UploadedFile["gallery_pics"]]) -> dict:
                return {
                    "count": len(images),
                    "filenames": [img.filename for img in images],
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "gallery_pics": [
                    {
                        "filename": "photo1.jpg",
                        "content": b"data1",
                        "content_type": "image/jpeg",
                    },
                    {
                        "filename": "photo2.jpg",
                        "content": b"data2",
                        "content_type": "image/jpeg",
                    },
                ]
            },
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["count"] == 2
        assert response.body["filenames"] == ["photo1.jpg", "photo2.jpg"]

    def test_mixed_auto_and_bracket_files(self):
        """자동 변환과 브래킷 구문 혼합 사용"""
        from vessel.web.http.uploaded_file import UploadedFile

        @Controller("/api")
        class FileController:
            @Post("/upload")
            def upload_files(
                self,
                document: UploadedFile,  # 자동: "document" 키 사용
                avatar: UploadedFile["profile_pic"],  # 명시적: "profile_pic" 키 사용
            ) -> dict:
                return {
                    "document_name": document.filename,
                    "avatar_name": avatar.filename,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/upload",
            body={
                "document": {
                    "filename": "report.pdf",
                    "content": b"pdf data",
                    "content_type": "application/pdf",
                },
                "profile_pic": {
                    "filename": "avatar.jpg",
                    "content": b"image data",
                    "content_type": "image/jpeg",
                },
            },
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["document_name"] == "report.pdf"
        assert response.body["avatar_name"] == "avatar.jpg"

    def test_example_from_user(self):
        """사용자 요구사항 예시: 다른 키로 파일 전송"""
        from vessel.web.http.uploaded_file import UploadedFile

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
                    "avatar_size": avatar.size,
                    "cover_uploaded": cover.filename,
                    "cover_size": cover.size,
                }

        app = Application("__main__")
        app.initialize()

        request = HttpRequest(
            method="POST",
            path="/api/profile",
            body={
                "user_avatar": {
                    "filename": "my_photo.jpg",
                    "content": b"avatar data here",
                    "content_type": "image/jpeg",
                },
                "cover_image": {
                    "filename": "background.png",
                    "content": b"cover data here",
                    "content_type": "image/png",
                },
            },
        )

        response = app.handle_request(request)
        assert response.status_code == 200
        assert response.body["avatar_uploaded"] == "my_photo.jpg"
        assert response.body["avatar_size"] == 16
        assert response.body["cover_uploaded"] == "background.png"
        assert response.body["cover_size"] == 15
