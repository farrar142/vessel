"""
Application - 웹 애플리케이션 전체 라이프사이클 관리
Spring Boot의 SpringApplication과 유사한 역할
"""

from typing import TYPE_CHECKING, Optional, List, Any, Callable, Dict
import logging
from vessel.core.container_manager import ContainerManager
from vessel.http.route_handler import RouteHandler
from vessel.http.request import HttpRequest, HttpResponse

if TYPE_CHECKING:
    from vessel.web.middleware import MiddlewareChain
logger = logging.getLogger(__name__)


class Application:
    """
    웹 애플리케이션 메인 클래스

    주요 기능:
    - 컴포넌트 스캔 및 의존성 주입 초기화
    - HTTP 라우팅 설정
    - 애플리케이션 라이프사이클 관리
    - 미들웨어 지원
    - 에러 핸들링
    """

    def __init__(
        self,
        *packages: str,
        enable_cors: bool = False,
        debug: bool = False,
        host: str = "0.0.0.0",
        port: int = 8080,
    ):
        """
        Application 초기화

        Args:
            *packages: 컴포넌트 스캔할 패키지 목록
            enable_cors: CORS 활성화 여부
            debug: 디버그 모드 (상세 로그 출력)
            host: 서버 호스트
            port: 서버 포트
        """
        self.packages = packages or []
        self.enable_cors = enable_cors
        self.debug = debug
        self.host = host
        self.port = port

        # ContainerManager 초기화
        self.container_manager = ContainerManager()

        # RouteHandler 초기화 (나중에)
        self.route_handler: Optional[RouteHandler] = None

        # MiddlewareChain (컴포넌트에서 자동 감지)
        self.middleware_chain: "Optional[MiddlewareChain]" = None

        # 에러 핸들러
        self.error_handlers: Dict[type, Callable] = {}

        # 애플리케이션 상태
        self.is_initialized = False
        self.is_running = False

        # 로깅 설정
        self._setup_logging()

    def _setup_logging(self):
        """로깅 설정"""
        log_level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def initialize(self) -> "Application":
        """
        애플리케이션 초기화
        - 컴포넌트 스캔
        - 의존성 주입 설정
        - 라우트 핸들러 초기화

        Returns:
            Application: self (메서드 체이닝용)
        """
        if self.is_initialized:
            logger.warning("Application already initialized")
            return self

        logger.info("Initializing Vessel Application...")

        # 1. 컴포넌트 스캔
        if self.packages:
            logger.info(f"Scanning packages: {', '.join(self.packages)}")
            for package in self.packages:
                self.container_manager.component_scan(package)
        else:
            logger.info("Scanning __main__ package")
            self.container_manager.component_scan("__main__")

        # 2. 의존성 주입 초기화
        logger.info("Initializing dependency injection...")
        self.container_manager.initialize()

        # 3. MiddlewareChain 감지 및 설정
        logger.info("Detecting middleware chain...")
        self._detect_middleware_chain()

        # 4. RouteHandler 초기화
        logger.info("Initializing route handler...")
        self.route_handler = RouteHandler(self.container_manager)

        # 5. 컨트롤러 정보 로깅
        controllers = self.container_manager.get_controllers()
        logger.info(f"Registered {len(controllers)} controller(s)")

        if self.debug:
            for controller_type in controllers:
                logger.debug(f"  - {controller_type.__name__}")

        self.is_initialized = True
        logger.info("✓ Application initialized successfully")

        return self

    def _detect_middleware_chain(self):
        """
        MiddlewareChain 컴포넌트를 자동으로 감지
        컨테이너에서 MiddlewareChain 타입의 인스턴스를 찾음
        """
        try:
            from vessel.web.middleware import MiddlewareChain

            # MiddlewareChain 인스턴스 찾기
            middleware_chain = self.container_manager.get_instance(MiddlewareChain)

            if middleware_chain:
                self.middleware_chain = middleware_chain
                middleware_count = len(middleware_chain.get_all_middlewares())
                logger.info(
                    f"✓ MiddlewareChain detected with {middleware_count} middleware(s)"
                )

                if self.debug:
                    for middleware in middleware_chain.get_all_middlewares():
                        logger.debug(f"  - {type(middleware).__name__}")
            else:
                logger.debug("No MiddlewareChain found in container")

        except ImportError:
            logger.debug("MiddlewareChain not available")
        except Exception as e:
            logger.warning(f"Failed to detect MiddlewareChain: {e}")

    def add_error_handler(
        self, exception_type: type, handler: Callable[[Exception], HttpResponse]
    ) -> "Application":
        """
        에러 핸들러 등록

        Args:
            exception_type: 처리할 예외 타입
            handler: 에러 처리 함수

        Returns:
            Application: self (메서드 체이닝용)
        """
        self.error_handlers[exception_type] = handler
        logger.debug(f"Error handler registered for {exception_type.__name__}")
        return self

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        HTTP 요청 처리

        Args:
            request: HTTP 요청

        Returns:
            HttpResponse: HTTP 응답
        """
        if not self.is_initialized:
            raise RuntimeError("Application not initialized. Call initialize() first.")

        if not self.route_handler:
            raise RuntimeError("RouteHandler not initialized")

        try:
            response = None

            # MiddlewareChain이 있으면 미들웨어 실행
            if self.middleware_chain:
                # 요청 미들웨어 실행 (early return 가능)
                early_response = self.middleware_chain.execute_request(request)

                if early_response is not None:
                    # 미들웨어에서 early return한 경우
                    response = early_response
                else:
                    # 라우트 핸들러 실행
                    response = self.route_handler.handle_request(request)

                # 응답 미들웨어 실행
                response = self.middleware_chain.execute_response(request, response)

            # 미들웨어 없이 직접 라우트 핸들러 호출
            else:
                response = self.route_handler.handle_request(request)

            # CORS 헤더 추가
            if self.enable_cors:
                response = self._add_cors_headers(response)

            return response

        except Exception as e:
            return self._handle_error(e, request)

    def _add_cors_headers(self, response: HttpResponse) -> HttpResponse:
        """CORS 헤더 추가"""
        if not hasattr(response, "headers"):
            response.headers = {}

        response.headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )

        return response

    def _handle_error(self, error: Exception, request: HttpRequest) -> HttpResponse:
        """에러 처리"""
        # 등록된 에러 핸들러 확인
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                logger.info(
                    f"Handling error with registered handler: {error_type.__name__}"
                )
                return handler(error)

        # 기본 에러 처리
        logger.error(
            f"Unhandled error: {type(error).__name__}: {error}", exc_info=self.debug
        )

        status_code = 500
        error_message = str(error)

        # 일반적인 HTTP 에러 처리
        if hasattr(error, "status_code"):
            status_code = error.status_code

        return HttpResponse(
            status_code=status_code,
            body={
                "error": type(error).__name__,
                "message": error_message,
                "path": request.path if request else None,
            },
        )

    def get_instance(self, target_type: type) -> Any:
        """
        컨테이너에서 인스턴스 가져오기

        Args:
            target_type: 가져올 인스턴스 타입

        Returns:
            인스턴스 또는 None
        """
        if not self.is_initialized:
            raise RuntimeError("Application not initialized")

        return self.container_manager.get_instance(target_type)

    def run(self, server: Optional[Any] = None):
        """
        애플리케이션 실행

        Args:
            server: WSGI/ASGI 서버 (예: Uvicorn, Gunicorn)
                   None인 경우 개발용 간단한 서버 시작
        """
        if not self.is_initialized:
            self.initialize()

        self.is_running = True

        logger.info("=" * 60)
        logger.info(f"🚢 Vessel Application Starting...")
        logger.info(f"   Host: {self.host}")
        logger.info(f"   Port: {self.port}")
        logger.info(f"   Debug: {self.debug}")
        logger.info(f"   CORS: {'Enabled' if self.enable_cors else 'Disabled'}")
        logger.info("=" * 60)

        if server:
            # 외부 서버 사용 (예: Uvicorn)
            logger.info("Starting with external server...")
            server.run(self)
        else:
            # 개발용 간단한 서버
            logger.info("Starting development server...")
            logger.info("(Use an ASGI/WSGI server like Uvicorn for production)")
            self._run_dev_server()

    def _run_dev_server(self):
        """개발용 간단한 서버 (프로덕션에서는 사용하지 말 것)"""
        try:
            import http.server
            import socketserver
            import json
            from urllib.parse import urlparse, parse_qs

            class VesselHandler(http.server.SimpleHTTPRequestHandler):
                app = self

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
                            self.rfile.read(content_length)
                            if content_length > 0
                            else b""
                        )

                        # HttpRequest 생성
                        request = HttpRequest(
                            method=method,
                            path=self.path.split("?")[0],
                            headers=dict(self.headers),
                            body=json.loads(body_bytes) if body_bytes else {},
                        )

                        # 요청 처리
                        response = self.app.handle_request(request)

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

            with socketserver.TCPServer((self.host, self.port), VesselHandler) as httpd:
                logger.info(f"✓ Server running at http://{self.host}:{self.port}")
                logger.info("Press CTRL+C to stop")
                httpd.serve_forever()

        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down server...")
            self.is_running = False
        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            self.is_running = False

    def stop(self):
        """애플리케이션 중지"""
        logger.info("Stopping application...")
        self.is_running = False
        logger.info("✓ Application stopped")

    def __repr__(self) -> str:
        return (
            f"Application(packages={self.packages}, "
            f"initialized={self.is_initialized}, "
            f"running={self.is_running})"
        )


# 편의 함수
def create_app(*packages: str, **kwargs) -> Application:
    """
    Application 인스턴스 생성 편의 함수

    Args:
        *packages: 스캔할 패키지 목록
        **kwargs: Application 초기화 인자

    Returns:
        Application 인스턴스
    """
    return Application(*packages, **kwargs)
