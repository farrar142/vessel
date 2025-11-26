"""
Unit Tests for Handler and Interceptor
"""

import pytest
from vessel.decorators.handler import (
    HandlerContainer,
    HandlerInterceptor,
    TransactionInterceptor,
    LoggingInterceptor,
    create_handler_decorator,
)


class TestHandlerInterceptor:
    """HandlerInterceptor 기본 테스트"""

    def test_interceptor_before(self):
        """before 메서드 테스트"""
        interceptor = HandlerInterceptor()
        args = (1, 2, 3)
        kwargs = {"key": "value"}

        result_args, result_kwargs = interceptor.before(*args, **kwargs)

        assert result_args == args
        assert result_kwargs == kwargs

    def test_interceptor_after(self):
        """after 메서드 테스트"""
        interceptor = HandlerInterceptor()
        result = {"data": "test"}

        modified_result = interceptor.after(result, 1, 2, key="value")

        assert modified_result == result

    def test_interceptor_on_error(self):
        """on_error 메서드 테스트"""
        interceptor = HandlerInterceptor()
        error = ValueError("test error")

        with pytest.raises(ValueError):
            interceptor.on_error(error, 1, 2)


class TestHandlerContainer:
    """HandlerContainer 테스트"""

    def test_handler_container_creation(self):
        """핸들러 컨테이너 생성 테스트"""

        def my_handler():
            return "result"

        container = HandlerContainer(my_handler)

        assert container.target == my_handler
        assert len(container.interceptors) == 0
        assert len(container.interceptor_classes) == 0

    def test_add_interceptor(self):
        """인터셉터 추가 테스트"""

        def my_handler():
            return "result"

        container = HandlerContainer(my_handler)
        interceptor = HandlerInterceptor()
        container.add_interceptor(interceptor)

        assert len(container.interceptors) == 1
        assert container.interceptors[0] == interceptor

    def test_add_interceptor_class(self):
        """인터셉터 클래스 추가 테스트"""

        def my_handler():
            return "result"

        container = HandlerContainer(my_handler)
        container.add_interceptor_class(HandlerInterceptor)

        assert len(container.interceptor_classes) == 1
        assert container.interceptor_classes[0] == HandlerInterceptor

    def test_wrap_handler(self):
        """핸들러 래핑 테스트"""
        call_order = []

        class TestInterceptor(HandlerInterceptor):
            def before(self, *args, **kwargs):
                call_order.append("before")
                return args, kwargs

            def after(self, result, *args, **kwargs):
                call_order.append("after")
                return result

        def my_handler():
            call_order.append("handler")
            return "result"

        container = HandlerContainer(my_handler)
        container.add_interceptor(TestInterceptor())

        wrapped = container.wrap_handler(my_handler)
        result = wrapped()

        assert result == "result"
        assert call_order == ["before", "handler", "after"]

    def test_wrap_handler_multiple_interceptors(self):
        """여러 인터셉터 테스트"""
        call_order = []

        class Interceptor1(HandlerInterceptor):
            def before(self, *args, **kwargs):
                call_order.append("before1")
                return args, kwargs

            def after(self, result, *args, **kwargs):
                call_order.append("after1")
                return result

        class Interceptor2(HandlerInterceptor):
            def before(self, *args, **kwargs):
                call_order.append("before2")
                return args, kwargs

            def after(self, result, *args, **kwargs):
                call_order.append("after2")
                return result

        def my_handler():
            call_order.append("handler")
            return "result"

        container = HandlerContainer(my_handler)
        container.add_interceptor(Interceptor1())
        container.add_interceptor(Interceptor2())

        wrapped = container.wrap_handler(my_handler)
        wrapped()

        # before는 순서대로, after는 역순
        assert call_order == ["before1", "before2", "handler", "after2", "after1"]

    def test_wrap_handler_error_handling(self):
        """에러 처리 테스트"""
        error_handled = []

        class ErrorInterceptor(HandlerInterceptor):
            def on_error(self, error, *args, **kwargs):
                error_handled.append(str(error))
                raise error

        def failing_handler():
            raise ValueError("test error")

        container = HandlerContainer(failing_handler)
        container.add_interceptor(ErrorInterceptor())

        wrapped = container.wrap_handler(failing_handler)

        with pytest.raises(ValueError):
            wrapped()

        assert "test error" in error_handled


class TestCreateHandlerDecorator:
    """create_handler_decorator 팩토리 테스트"""

    def test_create_single_interceptor_decorator(self):
        """단일 인터셉터 데코레이터 생성"""

        class TestInterceptor(HandlerInterceptor):
            pass

        decorator = create_handler_decorator(TestInterceptor, inject_dependencies=False)

        def my_function():
            return "result"

        decorated = decorator(my_function)

        assert hasattr(decorated, "__pydi_container__")
        assert isinstance(decorated.__pydi_container__, HandlerContainer)

    def test_create_multiple_interceptors_decorator(self):
        """여러 인터셉터 데코레이터 생성"""

        class Interceptor1(HandlerInterceptor):
            pass

        class Interceptor2(HandlerInterceptor):
            pass

        decorator = create_handler_decorator(
            Interceptor1, Interceptor2, inject_dependencies=False
        )

        def my_function():
            return "result"

        decorated = decorator(my_function)
        container = decorated.__pydi_container__

        # inject_dependencies=False이므로 바로 interceptors에 추가됨
        assert len(container.interceptors) == 2

    def test_create_decorator_with_metadata(self):
        """메타데이터가 있는 데코레이터 생성"""

        class TestInterceptor(HandlerInterceptor):
            pass

        decorator = create_handler_decorator(
            TestInterceptor,
            metadata_key="__test_metadata__",
            inject_dependencies=False,
        )

        def my_function():
            return "result"

        decorated = decorator(my_function)

        assert hasattr(decorated, "__test_metadata__")
        assert decorated.__test_metadata__ is True


class TestBuiltInInterceptors:
    """내장 인터셉터 테스트"""

    def test_transaction_interceptor(self, capsys):
        """TransactionInterceptor 테스트"""
        interceptor = TransactionInterceptor()

        # Before
        interceptor.before()
        captured = capsys.readouterr()
        assert "BEGIN" in captured.out

        # After
        interceptor.after("result")
        captured = capsys.readouterr()
        assert "COMMIT" in captured.out

        # Error
        with pytest.raises(ValueError):
            interceptor.on_error(ValueError("test"), 1, 2)
        captured = capsys.readouterr()
        assert "ROLLBACK" in captured.out

    def test_logging_interceptor(self, capsys):
        """LoggingInterceptor 테스트"""
        interceptor = LoggingInterceptor()

        # Before
        interceptor.before(1, 2, key="value")
        captured = capsys.readouterr()
        assert "요청 시작" in captured.out

        # After
        interceptor.after("result", 1, 2)
        captured = capsys.readouterr()
        assert "요청 완료" in captured.out
