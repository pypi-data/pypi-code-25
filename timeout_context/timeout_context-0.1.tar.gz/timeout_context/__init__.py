import signal


class TimeoutException(Exception):
    pass


class Timeout:
    def __init__(self, timeout):
        """

        :param timeout: in seconds
        """
        self._timeout = timeout
        pass

    def __enter__(self):
        def raiser(signum, frame):
            raise TimeoutException()

        signal.signal(signal.SIGALRM, raiser)
        signal.alarm(self._timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


from time import sleep

if __name__ == '__main__':
    with Timeout(3):
        print "x"
    with Timeout(3):
        sleep(6)
        print "x"
