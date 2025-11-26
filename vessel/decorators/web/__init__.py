"""
Vessel Decorators - Web Module

Web 관련 데코레이터:
- @Controller: 컨트롤러 등록
- @Get, @Post, @Put, @Delete, @Patch: HTTP 메서드 매핑
"""

from vessel.decorators.web.controller import (
    Controller,
    RequestMapping,
)
from vessel.decorators.web.mapping import (
    Get,
    Post,
    Put,
    Delete,
    Patch,
    HttpMethodMappingHandler,
)

__all__ = [
    "Controller",
    "RequestMapping",
    "Get",
    "Post",
    "Put",
    "Delete",
    "Patch",
    "HttpMethodMappingHandler",
]
