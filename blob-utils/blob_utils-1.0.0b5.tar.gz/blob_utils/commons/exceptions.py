""" Blob Utils Exceptions
"""


class BLOBError(Exception):
    """ Exception raised by BLOB Host
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
