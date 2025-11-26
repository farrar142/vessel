"""
Built-in Middleware 구현
Middleware들은 @Component가 아닌 @Factory로 생성되어야 함
"""

from typing import Optional, List, Any
from vessel.web.middleware.chain import Middleware
from vessel.http.request import HttpRequest, HttpResponse


class CorsMiddleware(Middleware):
    """
    CORS (Cross-Origin Resource Sharing) 미들웨어

    설정 가능한 CORS 정책 제공
    """

    def __init__(self):
        self.allowed_origins: List[str] = ["*"]
        self.allowed_methods: List[str] = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
        ]
        self.allowed_headers: List[str] = ["Content-Type", "Authorization"]
        self.allow_credentials: bool = False
        self.max_age: Optional[int] = None

    def set_allowed_origins(self, *origins: str) -> "CorsMiddleware":
        """
        허용할 Origin 설정

        Args:
            *origins: 허용할 origin 목록 (예: "https://example.com")

        Returns:
            self (메서드 체이닝용)
        """
        self.allowed_origins = list(origins)
        return self

    def set_allowed_methods(self, *methods: str) -> "CorsMiddleware":
        """
        허용할 HTTP 메서드 설정

        Args:
            *methods: HTTP 메서드 목록 (예: "GET", "POST")

        Returns:
            self (메서드 체이닝용)
        """
        self.allowed_methods = [m.upper() for m in methods]
        return self

    def set_allowed_headers(self, *headers: str) -> "CorsMiddleware":
        """
        허용할 헤더 설정

        Args:
            *headers: 헤더 목록

        Returns:
            self (메서드 체이닝용)
        """
        self.allowed_headers = list(headers)
        return self

    def set_allow_credentials(self, allow: bool = True) -> "CorsMiddleware":
        """
        자격 증명 허용 여부 설정

        Args:
            allow: 허용 여부

        Returns:
            self (메서드 체이닝용)
        """
        self.allow_credentials = allow
        return self

    def set_max_age(self, seconds: int) -> "CorsMiddleware":
        """
        Preflight 요청 캐시 시간 설정

        Args:
            seconds: 초 단위 시간

        Returns:
            self (메서드 체이닝용)
        """
        self.max_age = seconds
        return self

    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """
        OPTIONS 요청(Preflight)을 처리

        Args:
            request: HTTP 요청

        Returns:
            OPTIONS 요청인 경우 응답, 아니면 None
        """
        if request.method == "OPTIONS":
            # Preflight 요청에 대한 응답
            response = HttpResponse(status_code=204, body={})
            response.headers = self._get_cors_headers(request)
            return response

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        응답에 CORS 헤더 추가

        Args:
            request: HTTP 요청
            response: HTTP 응답

        Returns:
            CORS 헤더가 추가된 응답
        """
        if not hasattr(response, "headers"):
            response.headers = {}

        cors_headers = self._get_cors_headers(request)
        response.headers.update(cors_headers)

        return response

    def _get_cors_headers(self, request: HttpRequest) -> dict:
        """CORS 헤더 생성"""
        headers = {}

        # Origin
        if "*" in self.allowed_origins:
            headers["Access-Control-Allow-Origin"] = "*"
        else:
            origin = request.headers.get("Origin", "")
            if origin in self.allowed_origins:
                headers["Access-Control-Allow-Origin"] = origin

        # Methods
        headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)

        # Headers
        headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

        # Credentials
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        # Max Age
        if self.max_age is not None:
            headers["Access-Control-Max-Age"] = str(self.max_age)

        return headers


class LoggingMiddleware(Middleware):
    """
    요청/응답 로깅 미들웨어
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """요청 로깅"""
        print(f"→ {request.method} {request.path}")

        if self.verbose:
            print(f"  Headers: {request.headers}")
            if request.body:
                print(f"  Body: {request.body}")

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """응답 로깅"""
        print(f"← {response.status_code}")

        if self.verbose:
            print(f"  Body: {response.body}")

        return response


class AuthenticationMiddleware(Middleware):
    """
    인증 미들웨어 예제
    """

    def __init__(self, exclude_paths: Optional[List[str]] = None):
        self.exclude_paths = exclude_paths or ["/health", "/api/public"]

    def process_request(self, request: HttpRequest) -> Optional[Any]:
        """인증 확인"""
        # 제외 경로는 스킵
        if request.path in self.exclude_paths:
            return None

        # 토큰 확인
        token = request.headers.get("Authorization", "")

        if not token or not token.startswith("Bearer "):
            return HttpResponse(
                status_code=401,
                body={"error": "Unauthorized", "message": "Missing or invalid token"},
            )

        # 토큰 검증 로직 (여기서는 생략)
        # ...

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """응답은 그대로 반환"""
        return response
