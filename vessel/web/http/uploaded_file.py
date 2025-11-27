"""
File Upload Module

파일 업로드 처리를 위한 클래스와 함수
"""

import os
import re
from typing import Optional, Annotated
from io import BytesIO


class UploadedFile:
    """
    업로드된 파일을 나타내는 클래스

    DO NOT instantiate this class directly. It is created by the framework during injection.
    Use type hints (UploadedFile or UploadedFile["key"]) in function parameters instead.
    """

    def __init__(
        self,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ):
        """
        WARNING: This is for internal use only. Do not instantiate directly.
        Use type hints in function parameters for automatic file injection.
        """
        self.filename = filename
        self._content = content
        self.content_type = content_type
        self.size = len(content)
        self._stream = BytesIO(content)

    def read(self, size: int = -1) -> bytes:
        """
        파일 내용을 읽기

        Args:
            size: 읽을 바이트 수 (-1이면 전체)

        Returns:
            읽은 바이트
        """
        if size == -1:
            return self._content
        return self._stream.read(size)

    def save(self, path: str) -> None:
        """
        파일을 디스크에 저장

        Args:
            path: 저장할 경로
        """
        # 디렉토리가 없으면 생성
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # 파일 저장
        with open(path, "wb") as f:
            f.write(self._content)

    def secure_filename(self) -> str:
        """
        안전한 파일명 생성 (경로 순회 공격 방지)

        Returns:
            안전한 파일명
        """
        # 경로 구분자 제거
        filename = self.filename.replace("\\", "/")
        filename = os.path.basename(filename)

        # 위험한 문자 제거
        # 알파벳, 숫자, 점, 하이픈, 언더스코어만 허용
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # 연속된 점 제거 (..을 . 하나로)
        filename = re.sub(r"\.+", ".", filename)

        # 앞뒤 공백 및 점 제거
        filename = filename.strip(". ")

        # 빈 파일명이면 기본값 사용
        if not filename:
            filename = "unnamed"

        return filename

    def __repr__(self) -> str:
        return f"<UploadedFile: {self.filename} ({self.size} bytes)>"

    @classmethod
    def __class_getitem__(cls, key: str):
        """
        Support UploadedFile["file_key"] syntax for type annotations.
        Returns Annotated[UploadedFile, key] which can be used in type hints.

        Example:
            def upload(self, profile: UploadedFile["profile_pic"]):
                # Will look for file with key "profile_pic" in request data
                pass
        """
        return Annotated[cls, key]


def parse_file_from_dict(file_dict: dict) -> UploadedFile:
    """
    딕셔너리로부터 UploadedFile 생성

    Args:
        file_dict: {'filename': str, 'content': bytes, 'content_type': str}

    Returns:
        UploadedFile 인스턴스
    """
    return UploadedFile(
        filename=file_dict.get("filename", "unnamed"),
        content=file_dict.get("content", b""),
        content_type=file_dict.get("content_type", "application/octet-stream"),
    )


def parse_files_from_list(files_list: list) -> list[UploadedFile]:
    """
    리스트로부터 UploadedFile 리스트 생성

    Args:
        files_list: [{'filename': str, 'content': bytes, ...}, ...]

    Returns:
        UploadedFile 리스트
    """
    return [parse_file_from_dict(file_dict) for file_dict in files_list]
