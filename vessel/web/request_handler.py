"""
RequestHandler - HTTP 요청 처리 로직 분리
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Optional, Callable, Dict
from vessel.web.http.request import HttpRequest, HttpResponse
from vessel.web.router.parameter_injection import ValidationError
from vessel.utils.async_support import run_sync_or_async

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
        debug: bool = False,
    ):
        self.route_handler = route_handler
        if middleware_chain is None:
            from vessel.web.middleware.chain import MiddlewareChain

            middleware_chain = MiddlewareChain()
        self.middleware_chain = middleware_chain
        self.debug = debug
        self.error_handlers: Dict[type, Callable] = {}

    def add_error_handler(
        self, exception_type: type, handler: Callable[[Exception], HttpResponse]
    ):
        """에러 핸들러 등록"""
        self.error_handlers[exception_type] = handler
        logger.debug(f"Error handler registered for {exception_type.__name__}")

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        내부 async 핸들러 (실제 요청 처리)
        """
        try:

            if early_response := await run_sync_or_async(
                self.middleware_chain.execute_request
            )(request):
                # 미들웨어에서 early return한 경우
                response = early_response
            else:
                # 라우트 핸들러 실행
                response = await run_sync_or_async(self.route_handler.handle_request)(
                    request
                )

            # 응답 미들웨어 실행
            processed_response = await run_sync_or_async(
                self.middleware_chain.execute_response
            )(request, response)
            if isinstance(processed_response, HttpResponse):
                response = processed_response

            if not isinstance(response, HttpResponse):
                raise RuntimeError(
                    f"Handler must return HttpResponse, got {type(response)}"
                )

            return response

        except Exception as e:
            return self._handle_error(e, request)

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
            status_code = getattr(error, "status_code", 500)

        return HttpResponse(
            status_code=status_code,
            body={
                "error": type(error).__name__,
                "message": error_message,
                "path": request.path if request else None,
            },
        )
