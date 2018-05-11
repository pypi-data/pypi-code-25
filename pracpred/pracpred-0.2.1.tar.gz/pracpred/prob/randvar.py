"""Classes and functions for working with random variables"""
import math
import numbers
from .probdist import ProbDist
from . import exceptions


class RandVar(ProbDist):
    """A univariate discrete finite random variable."""
    slots = (
        '_mean',
        '_var',
        '_stdev',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tuple = False
        for x in self._space:
            if not isinstance(x, numbers.Number):
                msg = 'Random variable elements must be numeric'
                raise exceptions.ProbTypeError(msg)
        self._mean = None
        self._var = None
        self._stdev = None

    @property
    def mean(self):
        """Mean."""
        if not self._mean:
            self._mean = sum(self[x] * x for x in self)
        return self._mean

    @property
    def var(self):
        """Variance."""
        if not self._var:
            self._var = sum(self[x] * (x - self.mean) ** 2 for x in self)
        return self._var

    @property
    def stdev(self):
        """Standard deviation."""
        if not self._stdev:
            self._stdev = math.sqrt(self.var)
        return self._stdev

    def expect(self, func):
        """Expectation of a function over the random variable."""
        return sum(self[x] * func(x) for x in self)

    def moment(self, n):
        """Nth moment."""
        return sum(self[x] * x ** n for x in self)

    def central_moment(self, n):
        """Nth central moment."""
        return sum(self[x] * (x - self.mean) ** n for x in self)
