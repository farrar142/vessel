"""
Parameter injection system using Registry pattern
"""

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.parameter_injection.registry import ParameterInjectorRegistry
from vessel.http.parameter_injection.request_injector import HttpRequestInjector
from vessel.http.parameter_injection.header_injector import HttpHeaderInjector
from vessel.http.parameter_injection.cookie_injector import HttpCookieInjector
from vessel.http.parameter_injection.file_injector import FileInjector
from vessel.web.auth import AuthenticationInjector

__all__ = [
    "ParameterInjector",
    "InjectionContext",
    "ParameterInjectorRegistry",
    "HttpRequestInjector",
    "HttpHeaderInjector",
    "HttpCookieInjector",
    "FileInjector",
    "AuthenticationInjector",
]
