import sys
from functools import wraps


def Pipe(pipe_transformer, argument_transformer):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            # If there is stdin input, get it.
            if not sys.stdin.isatty():
                arg = pipe_transformer.transform(sys.stdin.read())
            # Otherwise, it expects commandline arguments.
            else:
                try:
                    arg = argument_transformer.transform(sys.argv[1])
                except IndexError:
                    message = 'Please provide arguments or pipe it through the function.'
                    raise IndexError(message)
            return func(arg)
        return decorator
    return wrapper
