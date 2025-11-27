"""
Parameter injection system using Registry pattern
"""

from vessel.web.router.parameter_injection.base import (
    ParameterInjector,
    InjectionContext,
)
from vessel.web.router.parameter_injection.registry import ParameterInjectorRegistry
from vessel.web.router.parameter_injection.request_injector import HttpRequestInjector
from vessel.web.router.parameter_injection.header_injector import HttpHeaderInjector
from vessel.web.router.parameter_injection.cookie_injector import HttpCookieInjector
from vessel.web.router.parameter_injection.file_injector import FileInjector
from vessel.web.router.parameter_injection.default_value_injector import (
    DefaultValueInjector,
    ValidationError,
)
from vessel.web.router.parameter_injection.request_body_injector import (
    RequestBodyInjector,
)
from vessel.web.auth import AuthenticationInjector

__all__ = [
    "ParameterInjector",
    "InjectionContext",
    "ParameterInjectorRegistry",
    "HttpRequestInjector",
    "HttpHeaderInjector",
    "HttpCookieInjector",
    "FileInjector",
    "RequestBodyInjector",
    "DefaultValueInjector",
    "ValidationError",
    "AuthenticationInjector",
]
