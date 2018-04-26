from time import time, sleep
from types import LambdaType


def condition(condition: LambdaType, timeout=10, pause=1):
    must_end = time() + timeout
    while time() < must_end:
        if condition():
            return
        sleep(pause)
    raise TimeoutError(f'Timeout {timeout} sec expired for condition')
