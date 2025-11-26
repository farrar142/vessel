"""
Abstract base class for injectors that handle Annotated type hints with value objects
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, get_origin, get_args, Union, Annotated

from vessel.web.router.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.web.router.parameter_injection.default_value_injector import ValidationError


class AnnotatedValueInjector(ParameterInjector, ABC):
    """
    Abstract base class for parameter injectors that:
    1. Support a specific marker type (e.g., HttpHeader, HttpCookie)
    2. Support Annotated[MarkerType, "explicit_name"] syntax
    3. Support Optional[MarkerType] and Optional[Annotated[MarkerType, "name"]]
    4. Return value objects instead of raw values

    Subclasses must implement:
    - get_marker_type(): Return the type marker class (e.g., HttpHeader)
    - extract_value_from_request(): Extract raw value from request
    - get_default_name(): Get default name from parameter name
    - create_value_object(): Create the value object to return
    - get_error_message(): Get error message for missing required values
    """

    @abstractmethod
    def get_marker_type(self) -> type:
        """
        Return the marker type this injector handles (e.g., HttpHeader, HttpCookie).

        Returns:
            The type class that this injector processes
        """
        pass

    @abstractmethod
    def extract_value_from_request(
        self, context: InjectionContext, name: str
    ) -> Optional[str]:
        """
        Extract the raw value from the request using the given name.

        Args:
            context: Injection context containing request and other data
            name: The name to look up (e.g., header name, cookie name)

        Returns:
            The raw value as string, or None if not found
        """
        pass

    @abstractmethod
    def get_default_name(self, param_name: str) -> str:
        """
        Convert parameter name to the default lookup name.

        For example:
        - HttpHeader: "user_agent" -> "User-Agent"
        - HttpCookie: "session_id" -> "session_id" (no conversion)

        Args:
            param_name: The parameter name from function signature

        Returns:
            The default name to use for lookup
        """
        pass

    @abstractmethod
    def create_value_object(self, name: str, value: Any) -> Any:
        """
        Create the value object to return.

        Args:
            name: The name (e.g., header name, cookie name, file key)
            value: The raw value (can be string for headers/cookies, or complex data for files)

        Returns:
            The value object (e.g., HttpHeader instance, HttpCookie instance, UploadedFile instance)
        """
        pass

    def supports_list(self) -> bool:
        """
        Whether this injector supports list[MarkerType] types.
        Override this to return True if the injector can handle lists.

        Returns:
            False by default (headers/cookies don't support lists)
        """
        return False

    def create_value_list(self, name: str, values: list) -> list:
        """
        Create a list of value objects.
        Override this if supports_list() returns True.

        Args:
            name: The name (e.g., file key)
            values: List of raw values

        Returns:
            List of value objects
        """
        raise NotImplementedError(
            "Subclass must implement create_value_list() if supports_list() is True"
        )

    @abstractmethod
    def get_error_message(self, name: str, param_name: str) -> str:
        """
        Get error message for missing required value.

        Args:
            name: The name that was looked up
            param_name: The parameter name from function signature

        Returns:
            Error message string
        """
        pass

    def can_inject(self, context: InjectionContext) -> bool:
        """
        Check if this injector can handle the parameter type.

        Supports:
        - MarkerType (e.g., HttpHeader)
        - Annotated[MarkerType, "name"]
        - Optional[MarkerType]
        - Optional[Annotated[MarkerType, "name"]]
        - list[MarkerType] (if supports_list() returns True)
        - list[Annotated[MarkerType, "name"]] (if supports_list() returns True)
        """
        param_type = context.param_type
        marker_type = self.get_marker_type()
        origin = get_origin(param_type)

        # Annotated[MarkerType, "name"] 체크
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == marker_type:
                return True

        # MarkerType 직접 체크
        if param_type == marker_type:
            return True

        # Optional[MarkerType] 또는 Optional[Annotated[MarkerType, "name"]] 체크
        if origin is Union:
            args = get_args(param_type)
            # Union 안에 MarkerType이 있거나, Annotated[MarkerType, ...]가 있는지 확인
            for arg in args:
                if arg == marker_type:
                    return True
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == marker_type:
                        return True

        # list[MarkerType] 또는 list[Annotated[MarkerType, "name"]] 체크
        if self.supports_list() and origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                if list_item_type == marker_type:
                    return True
                # list[Annotated[MarkerType, "name"]] 체크
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if list_item_args and list_item_args[0] == marker_type:
                        return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """
        Inject the value object into the parameter.

        Process:
        1. Extract explicit name from Annotated, or use default name
        2. Check if parameter is Optional or list
        3. Extract raw value from request
        4. Return None for Optional if missing, or raise ValidationError
        5. Create and return value object (or list of value objects)
        """
        param_type = context.param_type
        param_name = context.param_name

        # 명시적 이름 추출 (Annotated에서만)
        explicit_name = self._extract_explicit_name(param_type)

        # Optional 여부 확인
        is_optional = self._is_optional(param_type)

        # list 여부 확인
        is_list = self._is_list(param_type)

        # 이름 결정
        name = explicit_name if explicit_name else self.get_default_name(param_name)

        # 값 가져오기
        value = self.extract_value_from_request(context, name)

        if value is None:
            if is_optional:
                return None, False
            else:
                raise ValidationError(
                    [
                        {
                            "field": param_name,
                            "message": self.get_error_message(name, param_name),
                        }
                    ]
                )

        # list[MarkerType] 처리
        if is_list:
            if not isinstance(value, list):
                value = [value]
            value_objects = self.create_value_list(name, value)
            return value_objects, False

        # 단일 값 객체 생성
        value_object = self.create_value_object(name, value)
        return value_object, False

    def _extract_explicit_name(self, param_type: Any) -> Optional[str]:
        """
        Extract explicitly specified name from Annotated type.

        Handles:
        - Annotated[MarkerType, "name"]
        - Optional[Annotated[MarkerType, "name"]]
        - list[Annotated[MarkerType, "name"]]
        """
        marker_type = self.get_marker_type()
        origin = get_origin(param_type)

        # Annotated[MarkerType, "name"]에서 추출
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == marker_type and len(args) > 1:
                return args[1]

        # Optional[Annotated[MarkerType, "name"]]에서 추출
        if origin is Union:
            for arg in get_args(param_type):
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == marker_type and len(arg_args) > 1:
                        return arg_args[1]

        # list[Annotated[MarkerType, "name"]]에서 추출
        if origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if (
                        list_item_args
                        and list_item_args[0] == marker_type
                        and len(list_item_args) > 1
                    ):
                        return list_item_args[1]

        return None

    def _is_optional(self, param_type: Any) -> bool:
        """
        Check if the parameter type is Optional.

        Returns True for:
        - Optional[MarkerType]
        - Optional[Annotated[MarkerType, "name"]]
        """
        marker_type = self.get_marker_type()
        origin = get_origin(param_type)

        if origin is Union:
            args = get_args(param_type)
            # Union 안에 MarkerType나 Annotated[MarkerType, ...]와 None이 있는지 확인
            has_none = type(None) in args
            has_marker = False

            for arg in args:
                if arg == marker_type:
                    has_marker = True
                    break
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == marker_type:
                        has_marker = True
                        break

            return has_none and has_marker

        return False

    def _is_list(self, param_type: Any) -> bool:
        """
        Check if the parameter type is list[MarkerType].

        Returns True for:
        - list[MarkerType]
        - list[Annotated[MarkerType, "name"]]
        """
        if not self.supports_list():
            return False

        marker_type = self.get_marker_type()
        origin = get_origin(param_type)

        if origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                # list[MarkerType]
                if list_item_type == marker_type:
                    return True
                # list[Annotated[MarkerType, "name"]]
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if list_item_args and list_item_args[0] == marker_type:
                        return True

        return False
