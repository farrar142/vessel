"""
Vessel Web - Middleware Module

미들웨어 시스템:
- MiddlewareChain: 미들웨어 체인 관리
- Middleware: 미들웨어 기본 클래스
- Built-in middlewares: CORS, Logging, Authentication
"""

from vessel.web.middleware.chain import (
    Middleware,
    MiddlewareChain,
    MiddlewareGroup,
)
from vessel.web.middleware.builtins import (
    CorsMiddleware,
    LoggingMiddleware,
    AuthenticationMiddleware,
)

__all__ = [
    "Middleware",
    "MiddlewareChain",
    "MiddlewareGroup",
    "CorsMiddleware",
    "LoggingMiddleware",
    "AuthenticationMiddleware",
]
