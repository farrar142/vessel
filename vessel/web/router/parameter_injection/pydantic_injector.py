"""
PydanticInjector - Handles Pydantic BaseModel conversion from request body
"""

from typing import Any, Tuple, get_origin

from pydantic import BaseModel, ValidationError as PydanticValidationError

from vessel.web.router.parameter_injection.base import (
    ParameterInjector,
    InjectionContext,
)
from vessel.web.router.parameter_injection.default_value_injector import ValidationError


class PydanticInjector(ParameterInjector):
    """
    Converts request body data to Pydantic BaseModel instances.

    Leverages Pydantic powerful validation and type coercion features.

    Priority: Not used directly in registry (helper class for RequestBodyInjector)
    """

    @property
    def priority(self) -> int:
        """
        Priority for Pydantic BaseModel injection.
        Should be after DataclassInjector (300) and before DefaultValue (999).
        This allows direct BaseModel parameters like: def create(self, user: UserModel)
        """
        return 310

    def can_inject(self, context: InjectionContext) -> bool:
        """
        Check if parameter is a Pydantic BaseModel type.

        Note: This is typically not used directly as this injector is called
        by RequestBodyInjector. Can be used for direct BaseModel injection.
        """
        param_type = context.param_type

        # Skip generic types
        if get_origin(param_type) is not None:
            return False

        # Check if it's a Pydantic BaseModel
        try:
            return isinstance(param_type, type) and issubclass(param_type, BaseModel)
        except TypeError:
            return False

    def inject(self, context: InjectionContext) -> Tuple[Any, bool]:
        """
        Inject Pydantic BaseModel instance from request body.

        Supports two modes:
        1. Nested mode: param_name exists in request_data as a dict
           e.g., body = {"user": {"name": "john", "age": 30}}
           -> def create(self, user: UserModel)

        2. Flat mode: model fields directly in request_data
           e.g., body = {"name": "john", "age": 30}
           -> def create(self, user: UserModel)

        Args:
            context: Injection context

        Returns:
            Tuple[basemodel_instance, should_remove_from_request_data]
        """
        model_type = context.param_type
        request_data = context.request_data
        param_name = context.param_name

        # Check if param_name exists in request_data as nested object
        if param_name in request_data:
            param_value = request_data[param_name]
            if isinstance(param_value, dict):
                # Nested mode: use the nested dict
                instance = self.inject_pydantic(model_type, param_value, param_name)
                # Remove the nested object from request_data
                request_data.pop(param_name, None)
                return instance, False

        # Flat mode: use request_data directly
        instance = self.inject_pydantic(model_type, request_data, param_name)

        # Remove all used fields from request_data
        if hasattr(model_type, "model_fields"):
            # Pydantic v2
            field_names = model_type.model_fields.keys()
        elif hasattr(model_type, "__fields__"):
            # Pydantic v1
            field_names = model_type.__fields__.keys()
        else:
            field_names = []

        for field_name in field_names:
            request_data.pop(field_name, None)

        return instance, False

    def inject_pydantic(
        self, model_type: type, request_data: dict, param_name: str
    ) -> Any:
        """
        Convert request body to Pydantic BaseModel instance.

        Args:
            model_type: Pydantic BaseModel class
            request_data: Request data dictionary
            param_name: Parameter name for error messages

        Returns:
            BaseModel instance

        Raises:
            ValidationError: If validation fails
        """
        if not (isinstance(model_type, type) and issubclass(model_type, BaseModel)):
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"{model_type.__name__} is not a Pydantic BaseModel",
                    }
                ]
            )

        try:
            instance = model_type(**request_data)
            return instance

        except PydanticValidationError as e:
            errors = []
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                errors.append(
                    {
                        "field": (
                            f"{param_name}.{field_path}" if field_path else param_name
                        ),
                        "message": error["msg"],
                    }
                )
            raise ValidationError(errors)
