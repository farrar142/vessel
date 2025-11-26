"""
Vessel - Python Dependency Injection Framework
Spring IOC 스타일의 의존성 주입 프레임워크
"""

from vessel.decorators.component import Component
from vessel.decorators.factory import Factory
from vessel.decorators.controller import Controller, RequestMapping
from vessel.decorators.configuration import Configuration
from vessel.decorators.handler import (
    Transaction,
    Logging,
    HandlerInterceptor,
    HandlerContainer,
    create_handler_decorator,
)
from vessel.http.http_handler import (
    Get,
    Post,
    Put,
    Delete,
    Patch,
    HttpMethodMappingHandler,
)
from vessel.core.container_manager import ContainerManager
from vessel.http.request import HttpRequest, HttpResponse
from vessel.web.application import Application
from vessel.web.middleware import Middleware, MiddlewareChain, MiddlewareGroup
from vessel.web.builtins import (
    CorsMiddleware,
    LoggingMiddleware,
    AuthenticationMiddleware,
)

__version__ = "0.1.0"

__all__ = [
    "Component",
    "Factory",
    "Controller",
    "RequestMapping",
    "Configuration",
    "Get",
    "Post",
    "Put",
    "Delete",
    "Patch",
    "Transaction",
    "Logging",
    "HandlerInterceptor",
    "HandlerContainer",
    "HttpMethodMappingHandler",
    "ContainerManager",
    "HttpRequest",
    "HttpResponse",
    "create_handler_decorator",
    "Application",
    "Middleware",
    "MiddlewareChain",
    "MiddlewareGroup",
    "CorsMiddleware",
    "LoggingMiddleware",
    "AuthenticationMiddleware",
]
