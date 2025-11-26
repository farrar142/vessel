"""
ApplicationInitializer - 애플리케이션 초기화 로직 분리
"""

import logging
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from vessel.web.middleware.chain import MiddlewareChain
    from vessel.di.core.container_manager import ContainerManager

logger = logging.getLogger(__name__)


class ApplicationInitializer:
    """
    애플리케이션 초기화를 담당하는 클래스

    책임:
    - 컴포넌트 스캔
    - 의존성 주입 초기화
    - 미들웨어 체인 감지
    - 라우트 핸들러 설정
    """

    def __init__(self, container_manager: "ContainerManager", debug: bool = False):
        self.container_manager = container_manager
        self.debug = debug
        self.is_initialized = False

    def initialize(
        self, packages: List[str]
    ) -> tuple[Optional["MiddlewareChain"], object]:
        """
        애플리케이션 초기화 수행

        Args:
            packages: 스캔할 패키지 목록

        Returns:
            tuple: (middleware_chain, route_handler)
        """
        if self.is_initialized:
            logger.warning("Application already initialized")
            return None, None

        logger.info("Initializing Vessel Application...")

        # 1. 컴포넌트 스캔
        self._scan_components(packages)

        # 2. 의존성 주입 초기화
        logger.info("Initializing dependency injection...")
        self.container_manager.initialize()

        # 3. MiddlewareChain 감지
        logger.info("Detecting middleware chain...")
        middleware_chain = self._detect_middleware_chain()

        # 4. RouteHandler 초기화
        logger.info("Initializing route handler...")
        route_handler = self._create_route_handler()

        # 5. 컨트롤러 정보 로깅
        self._log_controllers()

        self.is_initialized = True
        logger.info("✓ Application initialized successfully")

        return middleware_chain, route_handler

    def _scan_components(self, packages: List[str]):
        """컴포넌트 스캔"""
        if packages:
            logger.info(f"Scanning packages: {', '.join(packages)}")
            for package in packages:
                self.container_manager.component_scan(package)
        else:
            logger.info("Scanning __main__ package")
            self.container_manager.component_scan("__main__")

    def _detect_middleware_chain(self) -> Optional["MiddlewareChain"]:
        """MiddlewareChain 자동 감지"""
        try:
            from vessel.web.middleware.chain import MiddlewareChain

            middleware_chain = self.container_manager.get_instance(MiddlewareChain)

            if middleware_chain:
                middleware_count = len(middleware_chain.get_all_middlewares())
                logger.info(
                    f"✓ MiddlewareChain detected with {middleware_count} middleware(s)"
                )

                if self.debug:
                    for middleware in middleware_chain.get_all_middlewares():
                        logger.debug(f"  - {type(middleware).__name__}")

                return middleware_chain
            else:
                logger.debug("No MiddlewareChain found in container")
                return None

        except ImportError:
            logger.debug("MiddlewareChain not available")
            return None
        except Exception as e:
            logger.warning(f"Failed to detect MiddlewareChain: {e}")
            return None

    def _create_route_handler(self):
        """RouteHandler 생성"""
        from vessel.http.router import RouteHandler

        return RouteHandler(self.container_manager)

    def _log_controllers(self):
        """등록된 컨트롤러 로깅"""
        controllers = self.container_manager.get_controllers()
        logger.info(f"Registered {len(controllers)} controller(s)")

        if self.debug:
            for controller_type in controllers:
                logger.debug(f"  - {controller_type.__name__}")
