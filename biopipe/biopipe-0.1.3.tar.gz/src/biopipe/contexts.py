from contextlib import contextmanager
import os
import sys

@contextmanager
def no_output():
    old_stdout, sys.stdout = sys.stdout, open(os.devnull, 'w')
    try:
        yield None
    finally:
        sys.stdout = old_stdout
