"""
DataclassInjector - Handles dataclass conversion from request body
"""

from typing import Any, Tuple, get_origin
from dataclasses import fields, is_dataclass, MISSING

from vessel.web.router.parameter_injection.base import (
    ParameterInjector,
    InjectionContext,
)
from vessel.web.router.parameter_injection.default_value_injector import ValidationError


class DataclassInjector(ParameterInjector):
    """
    Converts request body data to dataclass instances.

    Handles:
    - Type conversion
    - Required field validation
    - Default values
    - Nested dataclasses
    - List and Dict fields

    Priority: Not used directly in registry (helper class for RequestBodyInjector)
    """

    @property
    def priority(self) -> int:
        """
        Priority for dataclass injection.
        Should be after RequestBody (150) and before DefaultValue (999).
        This allows direct dataclass parameters like: def create(self, user: UserData)
        """
        return 300

    def can_inject(self, context: InjectionContext) -> bool:
        """
        Check if parameter is a dataclass type.

        Note: This is typically not used directly as this injector is called
        by RequestBodyInjector. Can be used for direct dataclass injection.
        """
        param_type = context.param_type

        # Skip generic types
        if get_origin(param_type) is not None:
            return False

        # Check if it's a dataclass
        return is_dataclass(param_type)

    def inject(self, context: InjectionContext) -> Tuple[Any, bool]:
        """
        Inject dataclass instance from request body.

        Only supports nested mode:
        - param_name must exist in request_data as a dict
        - e.g., body = {"user": {"name": "john", "age": 30}}
          -> def create(self, user: UserData)

        For flat mode (fields directly in body), use RequestBody[T] instead:
        - e.g., body = {"name": "john", "age": 30}
          -> def create(self, user: RequestBody[UserData])

        Args:
            context: Injection context

        Returns:
            Tuple[dataclass_instance, should_remove_from_request_data]

        Raises:
            ValidationError: If param_name not found in request_data
        """
        model_type = context.param_type
        request_data = context.request_data
        param_name = context.param_name

        # Check if param_name exists in request_data as nested object
        if param_name not in request_data:
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"Required parameter '{param_name}' not found in request body. "
                        f"For flat mode (fields directly in body), use RequestBody[{model_type.__name__}] instead.",
                    }
                ]
            )

        param_value = request_data[param_name]
        if not isinstance(param_value, dict):
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"Parameter '{param_name}' must be a dict/object, got {type(param_value).__name__}",
                    }
                ]
            )

        # Nested mode: use the nested dict
        instance = self.inject_dataclass(model_type, param_value, param_name)
        # Remove the nested object from request_data
        request_data.pop(param_name, None)
        return instance, False

    def inject_dataclass(
        self, model_type: type, request_data: dict, param_name: str
    ) -> Any:
        """
        Convert request body to dataclass instance.

        Args:
            model_type: Dataclass type
            request_data: Request data dictionary
            param_name: Parameter name for error messages

        Returns:
            Dataclass instance

        Raises:
            ValidationError: If validation fails
        """
        if not is_dataclass(model_type):
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"{model_type.__name__} is not a dataclass",
                    }
                ]
            )

        body_data = {}
        dataclass_fields = {f.name: f for f in fields(model_type)}
        errors = []

        for field_name, field_info in dataclass_fields.items():
            if field_name in request_data:
                value = request_data[field_name]
                # Type conversion
                try:
                    converted_value = self._convert_type(
                        value, field_info.type, field_name
                    )
                    body_data[field_name] = converted_value
                except ValueError as e:
                    errors.append(
                        {"field": f"{param_name}.{field_name}", "message": str(e)}
                    )
            else:
                # Check if field has default value
                if field_info.default is not MISSING:
                    body_data[field_name] = field_info.default
                elif field_info.default_factory is not MISSING:
                    body_data[field_name] = field_info.default_factory()
                else:
                    # Required field is missing
                    errors.append(
                        {
                            "field": f"{param_name}.{field_name}",
                            "message": f"Missing required field '{field_name}'",
                        }
                    )

        if errors:
            raise ValidationError(errors)

        # Create dataclass instance
        try:
            instance = model_type(**body_data)
        except Exception as e:
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"Failed to create {model_type.__name__}: {str(e)}",
                    }
                ]
            )

        return instance

    def _convert_type(self, value: Any, target_type: type, field_name: str) -> Any:
        """Convert value to target type"""
        from typing import get_origin, get_args

        # Handle generic types (List, Dict, etc.) first
        origin = get_origin(target_type)
        if origin is not None:
            if origin is list:
                return self._convert_to_list(value, target_type, field_name)
            elif origin is dict:
                return self._convert_to_dict(value, target_type, field_name)
            # For other generic types, return as-is
            return value

        # Handle nested dataclasses
        if is_dataclass(target_type):
            if isinstance(value, dict):
                # Recursively convert nested dataclass
                return self._convert_to_dataclass(value, target_type, field_name)
            else:
                raise ValueError(
                    f"Field '{field_name}' expects a dict for dataclass {target_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        # Already correct type (check after generic/dataclass handling)
        try:
            if isinstance(value, target_type):
                return value
        except TypeError:
            # isinstance may fail for some types, continue with conversion
            pass

        # Basic type conversion
        try:
            if target_type == bool:
                return self._convert_to_bool(value)
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == str:
                return str(value)
            else:
                # Can't convert, return as-is
                return value
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert field '{field_name}' to {target_type.__name__}: {str(e)}"
            )

    def _convert_to_bool(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            else:
                raise ValueError(f"Cannot convert '{value}' to boolean")
        return bool(value)

    def _convert_to_list(self, value: Any, target_type: type, field_name: str) -> list:
        """Convert value to list"""
        from typing import get_args

        if isinstance(value, list):
            args = get_args(target_type)
            if args:
                element_type = args[0]
                return [
                    self._convert_type(item, element_type, f"{field_name}[{i}]")
                    for i, item in enumerate(value)
                ]
            return value
        elif isinstance(value, str):
            # Split string by comma
            items = [item.strip() for item in value.split(",")]
            args = get_args(target_type)
            if args:
                element_type = args[0]
                return [
                    self._convert_type(item, element_type, f"{field_name}[{i}]")
                    for i, item in enumerate(items)
                ]
            return items
        else:
            # Wrap single value in list
            return [value]

    def _convert_to_dict(self, value: Any, target_type: type, field_name: str) -> dict:
        """Convert value to dict"""
        if isinstance(value, dict):
            return value
        else:
            raise ValueError(
                f"Field '{field_name}' expects dict, got {type(value).__name__}"
            )

    def _convert_to_dataclass(
        self, value: dict, dataclass_type: type, field_name: str
    ) -> Any:
        """Convert dict to nested dataclass"""
        dataclass_fields = {f.name: f for f in fields(dataclass_type)}
        nested_data = {}
        errors = []

        for nested_field_name, nested_field_info in dataclass_fields.items():
            if nested_field_name in value:
                nested_value = value[nested_field_name]
                try:
                    converted = self._convert_type(
                        nested_value,
                        nested_field_info.type,
                        f"{field_name}.{nested_field_name}",
                    )
                    nested_data[nested_field_name] = converted
                except ValueError as e:
                    errors.append(
                        {
                            "field": f"{field_name}.{nested_field_name}",
                            "message": str(e),
                        }
                    )
            else:
                # Check for default
                if nested_field_info.default is not MISSING:
                    nested_data[nested_field_name] = nested_field_info.default
                elif nested_field_info.default_factory is not MISSING:
                    nested_data[nested_field_name] = nested_field_info.default_factory()
                else:
                    errors.append(
                        {
                            "field": f"{field_name}.{nested_field_name}",
                            "message": f"Missing required field '{nested_field_name}'",
                        }
                    )

        if errors:
            raise ValidationError(errors)

        try:
            return dataclass_type(**nested_data)
        except Exception as e:
            raise ValueError(
                f"Failed to create nested {dataclass_type.__name__}: {str(e)}"
            )
