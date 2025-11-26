"""
Vessel Decorators Module

데코레이터를 기능별로 분류:
- di: DI 관련 (@Component, @Configuration, @Factory)
- web: Web 관련 (@Controller, @Get, @Post, etc.)
- handler: Handler/Interceptor 관련
"""

from vessel.decorators.di import Component, Configuration, Factory
from vessel.decorators.web import (
    Controller,
    RequestMapping,
    Get,
    Post,
    Put,
    Delete,
    Patch,
)
from vessel.decorators.handler import HandlerContainer, create_handler_decorator

__all__ = [
    # DI
    "Component",
    "Configuration",
    "Factory",
    # Web
    "Controller",
    "RequestMapping",
    "Get",
    "Post",
    "Put",
    "Delete",
    "Patch",
    # Handler
    "HandlerContainer",
    "create_handler_decorator",
]
