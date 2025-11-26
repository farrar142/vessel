"""
RequestHandler - HTTP 요청 처리 로직 분리
"""

import logging
from typing import TYPE_CHECKING, Optional, Callable, Dict
from vessel.http.request import HttpRequest, HttpResponse
from vessel.http.parameter_injection import ValidationError

if TYPE_CHECKING:
    from vessel.web.middleware.chain import MiddlewareChain
    from vessel.web.router import RouteHandler

logger = logging.getLogger(__name__)


class RequestHandler:
    """
    HTTP 요청 처리를 담당하는 클래스

    책임:
    - 미들웨어 실행
    - 라우트 핸들러 호출
    - CORS 처리
    - 에러 핸들링
    """

    def __init__(
        self,
        route_handler: "RouteHandler",
        middleware_chain: Optional["MiddlewareChain"] = None,
        enable_cors: bool = False,
        debug: bool = False,
    ):
        self.route_handler = route_handler
        self.middleware_chain = middleware_chain
        self.enable_cors = enable_cors
        self.debug = debug
        self.error_handlers: Dict[type, Callable] = {}

    def add_error_handler(
        self, exception_type: type, handler: Callable[[Exception], HttpResponse]
    ):
        """에러 핸들러 등록"""
        self.error_handlers[exception_type] = handler
        logger.debug(f"Error handler registered for {exception_type.__name__}")

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        HTTP 요청 처리

        Args:
            request: HTTP 요청

        Returns:
            HttpResponse: HTTP 응답
        """
        try:
            response = None

            # MiddlewareChain이 있으면 미들웨어 실행
            if self.middleware_chain:
                # 요청 미들웨어 실행 (early return 가능)
                early_response = self.middleware_chain.execute_request(request)

                if early_response is not None:
                    # 미들웨어에서 early return한 경우
                    response = early_response
                else:
                    # 라우트 핸들러 실행
                    response = self.route_handler.handle_request(request)

                # 응답 미들웨어 실행
                response = self.middleware_chain.execute_response(request, response)

            # 미들웨어 없이 직접 라우트 핸들러 호출
            else:
                response = self.route_handler.handle_request(request)

            # CORS 헤더 추가
            if self.enable_cors:
                response = self._add_cors_headers(response)

            return response

        except Exception as e:
            return self._handle_error(e, request)

    def _add_cors_headers(self, response: HttpResponse) -> HttpResponse:
        """CORS 헤더 추가"""
        if not hasattr(response, "headers"):
            response.headers = {}

        response.headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )

        return response

    def _handle_error(self, error: Exception, request: HttpRequest) -> HttpResponse:
        """에러 처리"""
        # ValidationError 먼저 처리
        if isinstance(error, ValidationError):
            logger.info(f"Validation failed: {error.errors}")
            return HttpResponse(
                status_code=400,
                body=error.to_dict(),
            )

        # 등록된 에러 핸들러 확인
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                logger.info(
                    f"Handling error with registered handler: {error_type.__name__}"
                )
                return handler(error)

        # 기본 에러 처리
        logger.error(
            f"Unhandled error: {type(error).__name__}: {error}", exc_info=self.debug
        )

        status_code = 500
        error_message = str(error)

        # 일반적인 HTTP 에러 처리
        if hasattr(error, "status_code"):
            status_code = error.status_code

        return HttpResponse(
            status_code=status_code,
            body={
                "error": type(error).__name__,
                "message": error_message,
                "path": request.path if request else None,
            },
        )
