"""
Authentication Parameter Injector
"""

from typing import get_origin, get_args, Optional, Tuple, Any
from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.web.auth.middleware import Authentication


class AuthenticationException(Exception):
    """인증 관련 예외"""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationInjector(ParameterInjector):
    """
    Authentication 파라미터를 주입하는 Injector

    AuthMiddleware가 request에 저장한 인증 정보를
    컨트롤러 메서드의 파라미터로 주입합니다.

    Supports:
        - Authentication
        - CustomAuthentication (Authentication을 상속한 클래스)
        - Optional[Authentication]
        - Optional[CustomAuthentication]
    """

    @property
    def priority(self) -> int:
        """우선순위: 150 (일반 주입기보다 높음)"""
        return 150

    def can_inject(self, context: InjectionContext) -> bool:
        """
        파라미터가 Authentication 타입 또는 그 하위 타입인지 확인

        Args:
            context: 주입 컨텍스트

        Returns:
            주입 가능하면 True
        """
        param_type = context.param_type

        # Optional[Authentication] 처리
        if (
            get_origin(param_type) is type(None)
            or str(get_origin(param_type)) == "typing.Union"
        ):
            args = get_args(param_type)
            if args and len(args) == 2 and type(None) in args:
                # Optional[T]는 Union[T, None]과 동일
                actual_type = args[0] if args[1] is type(None) else args[1]
                return self._is_authentication_type(actual_type)

        # Authentication 또는 그 하위 클래스
        return self._is_authentication_type(param_type)

    def inject(self, context: InjectionContext) -> Tuple[Any, bool]:
        """
        request에서 인증 정보를 가져와 주입

        Args:
            context: 주입 컨텍스트

        Returns:
            (Authentication 인스턴스, should_remove=False)

        Raises:
            AuthenticationException: 인증 필수인데 인증되지 않은 경우
        """
        param_type = context.param_type

        # Optional 타입 체크
        is_optional = self._is_optional(param_type)

        # request에서 인증 정보 가져오기
        authentication = None
        if hasattr(context.request, "_auth_data") and context.request._auth_data:
            authentication = context.request._auth_data.get("authentication")

        # Optional이 아닌데 인증 정보가 없으면 401 에러
        if not is_optional and (
            authentication is None or not authentication.authenticated
        ):
            raise AuthenticationException("Authentication required", 401)

        # Optional이면 None 반환 가능
        if is_optional and (authentication is None or not authentication.authenticated):
            return (None, False)

        return (authentication, False)

    def _is_authentication_type(self, param_type: type) -> bool:
        """
        파라미터 타입이 Authentication 또는 그 하위 타입인지 확인

        Args:
            param_type: 확인할 타입

        Returns:
            Authentication 타입이면 True
        """
        try:
            # Authentication 클래스 자체
            if param_type is Authentication:
                return True

            # Authentication을 상속한 클래스
            if isinstance(param_type, type) and issubclass(param_type, Authentication):
                return True
        except TypeError:
            # issubclass에서 TypeError가 발생할 수 있음 (제네릭 타입 등)
            pass

        return False

    def _is_optional(self, param_type: type) -> bool:
        """
        파라미터가 Optional 타입인지 확인

        Args:
            param_type: 확인할 타입

        Returns:
            Optional이면 True
        """
        origin = get_origin(param_type)

        # Union 타입 확인
        if origin is type(None) or str(origin) == "typing.Union":
            args = get_args(param_type)
            # Optional[T]는 Union[T, None]
            if args and len(args) == 2 and type(None) in args:
                return True

        return False
