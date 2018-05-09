from unittest import mock
from bcca.pytest_plugin import FakeStringIO, FakeStdIn

def should_print(test_function):
    '''should_print is a helper for testing code that uses print

    For example, if you had a function like this:

    ```python
    def hello(name):
        print('Hello,', name)
    ```

    You might want to test that it prints "Hello, Nate" if you give it the
    name "Nate". To do that, you could write the following test.

    ```python
    @should_print
    def test_hello_nate(output):
        hello("Nate")

        assert output == "Hello, Nate"
    ```

    There are a couple pieces of this:
        - Put `@should_print` directly above the test function.
        - Add an `output` parameter to the test function.
        - Assert against `output`
    '''
    return mock.patch('sys.stdout', new_callable=FakeStringIO)(test_function)

def with_inputs(*inputs):
    '''with_inputs accepts strings to be used as user input

    For example, if you had a function like this:

    ```python
    def get_age():
        age_string = input('What is your age? ')
        return int(age_string)
    ```

    You might want to test that it returns 27 if you give it
    "27" as user input. To do that, you could write the following test.

    ```python
    @with_inputs('27')
    def test_get_age():
        assert get_age() == 27
    ```

    There are a couple pieces to this:
        - Put `@with_inputs` directly above your test function.
        - Provide `@with_inputs(...)` with the strings you want
          to substitute for the user input.
    '''
    def _inner(test_function):
        def test_ignoring_input(input, *args, **kwargs):
            return test_function(*args, **kwargs)
        return mock.patch('sys.stdin', new_callable=lambda: FakeStdIn(inputs))(test_ignoring_input)
    return _inner
