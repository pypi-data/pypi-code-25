from nrask.raven import Raven

class Debug(object):

    def log(self, msg):
        try:
            assert self.__logger
        except (AssertionError, AttributeError):
            self.__logger = Raven('Debug')

        self.__logger.info(msg)
