"""
RequestBodyInjector - Handles RequestBody[DataClass | BaseModel] type hints

Delegates to DataclassInjector or PydanticInjector based on model type.
"""

from typing import Any, Tuple, get_origin, get_args, Annotated
from dataclasses import is_dataclass

from vessel.web.router.parameter_injection.base import (
    ParameterInjector,
    InjectionContext,
)
from vessel.web.router.parameter_injection.default_value_injector import ValidationError
from vessel.web.router.parameter_injection.dataclass_injector import DataclassInjector
from vessel.web.router.parameter_injection.pydantic_injector import PydanticInjector
from vessel.web.http.request_body import RequestBody
from pydantic import BaseModel


class RequestBodyInjector(ParameterInjector):
    """
    Injector for RequestBody[DataClass | BaseModel] type hints.

    Delegates to appropriate injector based on model type:
    - DataclassInjector for dataclasses
    - PydanticInjector for Pydantic BaseModel

    Priority: 150 (high priority, before default injector)
    """

    def __init__(self):
        self.dataclass_injector = DataclassInjector()
        self.pydantic_injector = PydanticInjector()

    @property
    def priority(self) -> int:
        """Higher priority than default injector"""
        return 150

    def can_inject(self, context: InjectionContext) -> bool:
        """
        Check if parameter is RequestBody[SomeDataClass | BaseModel] type.
        """
        param_type = context.param_type
        origin = get_origin(param_type)

        # Check for Annotated[RequestBody, DataClass | BaseModel]
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == RequestBody:
                # Has dataclass or BaseModel type in annotation
                if len(args) > 1:
                    model_type = args[1]
                    # Check if it's a dataclass
                    if is_dataclass(model_type):
                        return True
                    # Check if it's a Pydantic BaseModel
                    try:
                        if isinstance(model_type, type) and issubclass(
                            model_type, BaseModel
                        ):
                            return True
                    except TypeError:
                        pass

        return False

    def inject(self, context: InjectionContext) -> Tuple[Any, bool]:
        """
        Convert request body to dataclass or Pydantic BaseModel instance.

        Delegates to DataclassInjector or PydanticInjector based on model type.

        Returns:
            Tuple[model_instance, should_remove_from_request_data]
        """
        param_type = context.param_type
        request_data = context.request_data
        param_name = context.param_name

        # Extract model type from Annotated[RequestBody, DataClass | BaseModel]
        args = get_args(param_type)
        if len(args) < 2:
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": "RequestBody must specify a type: RequestBody[YourDataClass | YourBaseModel]",
                    }
                ]
            )

        model_type = args[1]

        # Check if it's a Pydantic BaseModel
        is_pydantic = False
        try:
            if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                is_pydantic = True
        except TypeError:
            pass

        # Delegate to appropriate injector
        if is_pydantic:
            instance = self.pydantic_injector.inject_pydantic(
                model_type, request_data, param_name
            )
        elif is_dataclass(model_type):
            instance = self.dataclass_injector.inject_dataclass(
                model_type, request_data, param_name
            )
        else:
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"{model_type.__name__} is not a dataclass or Pydantic BaseModel",
                    }
                ]
            )

        # Remove all used fields from request_data
        # Get model fields based on type
        if is_pydantic:
            # Pydantic BaseModel
            if hasattr(model_type, "model_fields"):
                # Pydantic v2
                field_names = model_type.model_fields.keys()
            elif hasattr(model_type, "__fields__"):
                # Pydantic v1
                field_names = model_type.__fields__.keys()
            else:
                field_names = []
        else:
            # Dataclass
            from dataclasses import fields

            field_names = [f.name for f in fields(model_type)]

        for field_name in field_names:
            request_data.pop(field_name, None)

        return instance, False
