import pathlib
from contextlib import contextmanager

DEFAULT_PATH = pathlib.Path('/run/secrets/')
NOT_SET = object()


def get(name):
    return (DEFAULT_PATH / name).read_text()


@contextmanager
def secrets_path(other_path):
    global DEFAULT_PATH
    _CURRENT_PATH = DEFAULT_PATH
    DEFAULT_PATH = other_path
    yield
    DEFAULT_PATH = _CURRENT_PATH
