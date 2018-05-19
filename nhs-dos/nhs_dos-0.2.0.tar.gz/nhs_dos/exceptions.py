class DosClientException(Exception):
    pass


class NoConnectionError(DosClientException):
    pass
