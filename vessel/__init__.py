"""
Vessel - Python Dependency Injection Framework
Spring IOC 스타일의 의존성 주입 프레임워크
"""

from vessel.decorators.di.component import Component
from vessel.decorators.di.factory import Factory
from vessel.decorators.web.controller import Controller, RequestMapping
from vessel.decorators.di.configuration import Configuration
from vessel.decorators.handler.handler import (
    Transaction,
    Logging,
    HandlerInterceptor,
    HandlerContainer,
    create_handler_decorator,
)
from vessel.decorators.web.mapping import (
    Get,
    Post,
    Put,
    Delete,
    Patch,
    HttpMethodMappingHandler,
)
from vessel.di.container_manager import ContainerManager
from vessel.http.request import HttpRequest, HttpResponse
from vessel.web.application import Application
from vessel.web.middleware.chain import Middleware, MiddlewareChain, MiddlewareGroup
from vessel.web.middleware.builtins import (
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
