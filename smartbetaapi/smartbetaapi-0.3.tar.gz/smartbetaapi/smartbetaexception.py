
class SmartBetaServerException(Exception):
    """The SmartBetaServerException class identified server side errors that have been raised by web service.

    These are usually validation errors on data passed to the service.
    """
    def __init__(self, *args,):
        Exception.__init__(self, *args)
