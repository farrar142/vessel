"""
Vessel Web Router Module

This module provides HTTP request routing functionality.

Exported Classes:
    - Route: Route information container
    - RouteHandler: HTTP request router and handler executor

Usage:
    from vessel.web.router import Route, RouteHandler
"""

from vessel.web.router.handler import (
    Route,
    RouteHandler,
)

__all__ = [
    "Route",
    "RouteHandler",
]
