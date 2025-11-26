"""
HTTP 요청/응답 관련 클래스
"""

from typing import Dict, Any, Optional
from enum import Enum


class HttpMethod(Enum):
    """HTTP 메서드"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class HttpRequest:
    """HTTP 요청 객체"""

    def __init__(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        path_params: Optional[Dict[str, str]] = None,
    ):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.body = body
        self.path_params = path_params or {}
        self.context: Dict[str, Any] = {}  # 미들웨어/핸들러 간 데이터 공유용

    def get_header(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """헤더 값 조회"""
        return self.headers.get(key, default)

    def get_query_param(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """쿼리 파라미터 조회"""
        return self.query_params.get(key, default)

    def get_path_param(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """경로 파라미터 조회"""
        return self.path_params.get(key, default)


class HttpResponse:
    """HTTP 응답 객체"""

    def __init__(
        self,
        body: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {}

    def set_header(self, key: str, value: str):
        """헤더 설정"""
        self.headers[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "body": self.body,
            "status_code": self.status_code,
            "headers": self.headers,
        }
