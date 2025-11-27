from typing import Any, Callable, Generic, TypeVar

from vessel.decorators.di.component import Component
from vessel.decorators.di.configuration import Configuration
from vessel.decorators.di.factory import Factory
from vessel.decorators.web.controller import Controller
from vessel.web.http.request import HttpResponse


class TestErrorHandler:
    def test_error_handler_chain(self):
        # E = TypeVar("E", bound=Exception)

        class ErrorHandler[E: Exception]:
            def __init__(
                self, exception: type[E], handler: Callable[[Any, E], HttpResponse]
            ):
                self.exception = exception
                self.handler = handler

            def can_handle(self, error):
                return isinstance(error, self.exception)

            def handle(self, error) -> HttpResponse:
                return self.handler(None, error)

            def __call__(self, *args, **kwargs): ...

        class ErrorHandlerChain:
            def __init__(self):
                self.handlers: list[ErrorHandler] = []

            def add_handler(self, *handler: ErrorHandler):
                self.handlers.extend(handler)

            def handle(self, error):
                for handler in self.handlers:
                    if handler.can_handle(error):
                        return handler.handle(error)
                raise error

            @staticmethod
            def add_error_handler[E: Exception](exception: type[E]):
                def decorator(
                    func: Callable[[Any, E], HttpResponse],
                ) -> ErrorHandler[E]:

                    return ErrorHandler(exception, func)

                return decorator

        @Configuration
        class ErrorConfig:
            @Factory
            def error_handler_chain(self, *args: ErrorHandler) -> ErrorHandlerChain:
                chain = ErrorHandlerChain()
                for handler in args:
                    chain.add_handler(handler)
                return chain

        @Component
        class LoggingService:
            def log(self, message: str):
                print(f"[LOG]: {message}")

        class UserNotFoundError(Exception):
            pass

        @Controller("/api/users")
        class UserController:
            logging_service: LoggingService

            @ErrorHandlerChain.add_error_handler(UserNotFoundError)
            def handle_error(self, error: UserNotFoundError):
                self.logging_service.log(f"UserNotFoundError handled: {str(error)}")
                return HttpResponse({"error": str(error)}, status_code=404)

            def get_users(self):
                self.handle_error
                raise UserNotFoundError("User not found")
