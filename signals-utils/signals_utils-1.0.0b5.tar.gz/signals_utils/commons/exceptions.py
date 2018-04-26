""" Signals Utils Exceptions
"""


class SignalsError(Exception):
    """ Exception raised when a signal connection (binding) fails.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
