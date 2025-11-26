"""
Application - 웹 애플리케이션 전체 라이프사이클 관리
Spring Boot의 SpringApplication과 유사한 역할

리팩토링: 책임 분리
- ApplicationInitializer: 초기화 로직
- RequestHandler: 요청 처리 로직
- DevServer: 개발 서버
"""

from typing import TYPE_CHECKING, Optional, Any, Callable
import logging
from vessel.di.container_manager import ContainerManager
from vessel.http.request import HttpRequest, HttpResponse
from vessel.web.initializer import ApplicationInitializer
from vessel.web.request_handler import RequestHandler

if TYPE_CHECKING:
    from vessel.web.middleware.chain import MiddlewareChain
    from vessel.http.router import RouteHandler

logger = logging.getLogger(__name__)


class Application:
    """
    웹 애플리케이션 메인 클래스 (파사드 패턴)

    책임:
    - 애플리케이션 설정 관리
    - 하위 컴포넌트 조정 (Initializer, RequestHandler, DevServer)
    - 애플리케이션 라이프사이클 관리

    주요 컴포넌트:
    - ApplicationInitializer: 초기화 담당
    - RequestHandler: 요청 처리 담당
    - DevServer: 개발 서버 담당
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
        # 설정
        self.packages = list(packages) if packages else []
        self.enable_cors = enable_cors
        self.debug = debug
        self.host = host
        self.port = port

        # 상태
        self.is_initialized = False
        self.is_running = False

        # 핵심 컴포넌트
        self.container_manager = ContainerManager()
        self.route_handler: Optional["RouteHandler"] = None
        self.middleware_chain: Optional["MiddlewareChain"] = None

        # 하위 컴포넌트 (초기화 후 생성)
        self._initializer: Optional[ApplicationInitializer] = None
        self._request_handler: Optional[RequestHandler] = None

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

        ApplicationInitializer를 사용하여 초기화 수행

        Returns:
            Application: self (메서드 체이닝용)
        """
        if self.is_initialized:
            logger.warning("Application already initialized")
            return self

        # ApplicationInitializer 생성 및 초기화
        self._initializer = ApplicationInitializer(
            self.container_manager, debug=self.debug
        )

        # 초기화 실행
        self.middleware_chain, self.route_handler = self._initializer.initialize(
            self.packages
        )

        # RequestHandler 생성
        self._request_handler = RequestHandler(
            route_handler=self.route_handler,
            middleware_chain=self.middleware_chain,
            enable_cors=self.enable_cors,
            debug=self.debug,
        )

        self.is_initialized = True

        return self

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
        if not self._request_handler:
            raise RuntimeError("Application not initialized. Call initialize() first.")

        self._request_handler.add_error_handler(exception_type, handler)
        return self

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        HTTP 요청 처리

        RequestHandler에 위임

        Args:
            request: HTTP 요청

        Returns:
            HttpResponse: HTTP 응답
        """
        if not self.is_initialized or not self._request_handler:
            raise RuntimeError("Application not initialized. Call initialize() first.")

        return self._request_handler.handle_request(request)

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

        if server:
            # 외부 서버 사용 (예: Uvicorn)
            logger.info("Starting with external server...")
            server.run(self)
        else:
            # DevServer 사용
            from vessel.web.server import DevServer

            dev_server = DevServer(self, host=self.host, port=self.port)
            try:
                dev_server.run()
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down server...")
            finally:
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
