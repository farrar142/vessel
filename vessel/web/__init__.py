"""
Vessel Web Module - 웹 애플리케이션 프레임워크

아키텍처:
- Application: 파사드 패턴으로 전체 조정
- ApplicationInitializer: 초기화 로직 분리
- RequestHandler: 요청 처리 로직 분리
- DevServer: 개발 서버 분리
"""

from vessel.web.application import Application, create_app
from vessel.web.initializer import ApplicationInitializer
from vessel.web.request_handler import RequestHandler
from vessel.web.server import DevServer

__all__ = [
    "Application",
    "create_app",
    "ApplicationInitializer",
    "RequestHandler",
    "DevServer",
]
