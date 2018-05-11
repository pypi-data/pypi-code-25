"""Exceptions raised by this package"""


class ProbException(Exception):
    """Base class for all exceptions raised by this package."""
    pass


class ProbValueException(ProbException, ValueError):
    """Invalid parameter values for probabilities or odds."""
    pass


class ProbTypeException(ProbException, TypeError):
    """Invalid parameter types for probabilities or odds."""
    pass
