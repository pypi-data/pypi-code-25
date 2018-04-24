from nrask.raven import Raven
import os

class Debug(object):
    enabled = (os.getenv('NRASK_DEBUG') == '1')

    def __init__(self, name):
        self.name = name

    def log(self, msg):
        try:
            assert self.__logger
        except (AssertionError, AttributeError):
            self.__logger = Raven('[debug] ' + self.name)

        try:
            assert self.enabled
        except AssertionError:
            pass
        else:
            self.__logger.info(msg)
