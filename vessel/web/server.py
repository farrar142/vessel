"""
DevServer - 개발용 HTTP 서버
"""

import logging
import http.server
import socketserver
import json
import asyncio
from typing import TYPE_CHECKING
from vessel.web.http.request import HttpRequest

if TYPE_CHECKING:
    from vessel.web.application import Application

logger = logging.getLogger(__name__)


class DevServer:
    """
    개발용 간단한 HTTP 서버

    주의: 프로덕션에서는 Uvicorn, Gunicorn 등을 사용할 것
    """

    def __init__(self, app: "Application", host: str = "0.0.0.0", port: int = 8080):
        self.app = app
        self.host = host
        self.port = port

    def run(self):
        """서버 실행"""
        logger.info("=" * 60)
        logger.info(f"🚢 Vessel Application Starting...")
        logger.info(f"   Host: {self.host}")
        logger.info(f"   Port: {self.port}")
        logger.info(f"   Debug: {self.app.debug}")
        logger.info("=" * 60)
        logger.info("Starting development server...")
        logger.info("(Use an ASGI/WSGI server like Uvicorn for production)")

        try:
            handler_class = self._create_handler_class()
            with socketserver.TCPServer((self.host, self.port), handler_class) as httpd:
                logger.info(f"✓ Server running at http://{self.host}:{self.port}")
                logger.info("Press CTRL+C to stop")
                httpd.serve_forever()

        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down server...")
        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)

    def _create_handler_class(self):
        """Request Handler 클래스 생성"""
        app = self.app

        class VesselHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self._handle_request("GET")

            def do_POST(self):
                self._handle_request("POST")

            def do_PUT(self):
                self._handle_request("PUT")

            def do_DELETE(self):
                self._handle_request("DELETE")

            def do_PATCH(self):
                self._handle_request("PATCH")

            def _handle_request(self, method: str):
                try:
                    # 요청 바디 읽기
                    content_length = int(self.headers.get("Content-Length", 0))
                    body_bytes = (
                        self.rfile.read(content_length) if content_length > 0 else b""
                    )

                    # HttpRequest 생성
                    request = HttpRequest(
                        method=method,
                        path=self.path.split("?")[0],
                        headers=dict(self.headers),
                        body=json.loads(body_bytes) if body_bytes else {},
                    )

                    # 요청 처리 (async 지원)
                    # asyncio.run()을 사용하여 async 함수를 동기적으로 실행
                    response = asyncio.run(app.handle_request(request))

                    # 응답 전송
                    self.send_response(response.status_code)
                    self.send_header("Content-Type", "application/json")

                    # 응답 헤더 추가
                    if hasattr(response, "headers"):
                        for key, value in response.headers.items():
                            self.send_header(key, value)

                    self.end_headers()

                    # 응답 바디
                    response_body = json.dumps(response.body).encode("utf-8")
                    self.wfile.write(response_body)

                except Exception as e:
                    logger.error(f"Error handling request: {e}", exc_info=True)
                    self.send_error(500, str(e))

            def log_message(self, format, *args):
                # 커스텀 로깅
                logger.info(f"{self.address_string()} - {format % args}")

        return VesselHandler
