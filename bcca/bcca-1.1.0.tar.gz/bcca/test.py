from unittest import mock
from bcca.pytest_plugin import FakeStringIO


def should_print(test_function):
    return mock.patch('sys.stdout', new_callable=FakeStringIO)(test_function)
