from unittest import mock
from bcca.pytest_plugin import FakeStringIO, FakeStdIn

def should_print(test_function):
    return mock.patch('sys.stdout', new_callable=FakeStringIO)(test_function)

def with_inputs(*inputs):
    print(inputs)
    def _inner(test_function):
        def test_ignoring_input(input, *args, **kwargs):
            return test_function(*args, **kwargs)
        return mock.patch('sys.stdin', new_callable=lambda: FakeStdIn(inputs))(test_ignoring_input)
    return _inner
