import signal
import sys

from pytest_cov.embed import cleanup


# https://pytest-cov.readthedocs.io/en/latest/mp.html#abusing-process-terminate
# https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
def handle_termination_signal(signum, frame):
    try:
        cleanup()
    finally:
        sys.exit(0)


signal.signal(signal.SIGTERM, handle_termination_signal)


def test_dummy():
    pass
