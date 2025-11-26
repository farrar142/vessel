"""
Authentication System

인증 시스템의 핵심 컴포넌트들을 제공합니다.

Components:
    - Authentication: 인증 정보를 담는 기본 클래스
    - Authenticator: 인증기 추상 클래스
    - AuthMiddleware: 인증 미들웨어
    - AuthenticationInjector: Authentication 파라미터 주입기
    - AuthenticationException: 인증 예외
"""

from vessel.web.auth.middleware import (
    Authentication,
    Authenticator,
    AuthenticatorRegistry,
    AuthMiddleware,
)
from vessel.web.auth.injector import (
    AuthenticationInjector,
    AuthenticationException,
)

__all__ = [
    # Core Classes
    "Authentication",
    "Authenticator",
    "AuthenticatorRegistry",
    "AuthMiddleware",
    # Injector
    "AuthenticationInjector",
    "AuthenticationException",
]
