"""mp-starter exception classes."""


class StarterError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class StarterConfigError(StarterError):
    """Config related errors."""
    pass


class StarterRuntimeError(StarterError):
    """Generic runtime errors."""
    pass


class StarterArgumentError(StarterError):
    """Argument related errors."""
    pass
