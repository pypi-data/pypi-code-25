"""Contains the base Variable class."""

from collections import Counter
from math import sqrt
from .exceptions import EmptyVariableError

class Variable:
    """A Variable represents an ordered sequence of measurements. It is `not`
    the same as a Python variable - it represents variables in the statistics
    sense of the word.

    A Variable is a container `and` an iterable of its values, and in many
    respects behaves like a ``list``.

    :param \*values: The values to go into the Variable. These will usually be\
    numerical, but can be any type. If you provide one value, which is iterable,\
    and which isn't a string, the values of that iterable will become the values\
    of the Variable.
    :param str name: The name of the Variable.
    :raises EmptyVariableError: if no values are given.
    :raises TypeError: if the name given isn't a string."""

    def __init__(self, *values, name=""):
        if len(values) == 0:
            raise EmptyVariableError("Cannot create Variable with no values")
        if len(values) == 1 and not isinstance(values[0], str):
            try:
                self._values = list(values[0])
                return
            except: pass
        self._values = list(values)
        if not isinstance(name, str):
            raise TypeError("name '{}' is not a str".format(name))
        self._name = name


    def __repr__(self):
        if self._name:
            return "<Variable '{}' {}>".format(self._name, tuple(self._values))
        return "<Variable {}>".format(tuple(self._values))


    def __len__(self):
        return len(self._values)


    def __contains__(self, member):
        return member in self._values


    def __iter__(self):
        return iter(self._values)


    def __getitem__(self, key):
        return self._values[key]


    def __setitem__(self, key, value):
        self._values[key] = value


    @property
    def values(self):
        """Returns the values in the Variable.

        :rtype: ``tuple``"""

        return tuple(self._values)


    def add(self, value):
        """Adds a value to the end of the Variable.

        :param value: The value to add."""

        self._values.append(value)


    def insert(self, index, value):
        """Inserts a value into the Variable.

        :param int index: The index to insert at.
        :param value: The value to insert."""

        self._values.insert(index, value)


    def remove(self, value):
        """Removes a value from the Variable.

        :param value: The value to remove.
        :raises EmptyVariableError: if you try to remove the only value."""

        if len(self._values) == 1:
            raise EmptyVariableError("Cannot remove last value from Variable")
        self._values.remove(value)


    def pop(self, index=-1):
        """Removes and returns the value at a given index - by default the last
        object in the Variable.

        :param int index: The index to remove at.
        :raises EmptyVariableError: if you try to pop the only value.
        :returns: the specified value."""

        if len(self._values) == 1:
            raise EmptyVariableError("Cannot pop last value from Variable")
        return self._values.pop(index)


    @property
    def name(self):
        """Returns the name of the Variable.

        :raises TypeError: if the name set is not a string."""

        return self._name


    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("name '{}' is not a str".format(name))
        self._name = name


    @property
    def length(self):
        """The length of the Variable - the number of values it has.

        :rtype: ``int``"""

        return len(self)


    @property
    def max(self):
        """Returns the largest value."""

        return max(self._values)


    @property
    def min(self):
        """Returns the smallest value."""

        return min(self._values)


    @property
    def sum(self):
        """Returns the sum of the values."""

        return sum(self._values)


    @property
    def mean(self):
        """Returns the mean of the values - their sum divided by the number of
        values."""

        return self.sum / self.length


    @property
    def median(self):
        """Returns the median value - the value that occurs midway through
        when the values are sorted. If there is an even number, the midpoint
        between the two median values will be returned."""

        values = sorted(self._values)
        if len(values) % 2:
            return values[int((len(values) - 1) / 2)]
        midway = int(self.length / 2)
        return (values[midway - 1] + values[midway]) / 2


    @property
    def frequencies(self):
        """Returns the frequencies of the values in the Variable.

        :rtype: ``Counter``"""

        return Counter(self._values)


    @property
    def mode(self):
        """Returns the mode value - the value that occurs the most often. If
        more than one value meets this criteria, ``None`` is returned."""

        values = self.frequencies
        highest_frequency = max(values.values())
        if len([v for v in values if values[v] == highest_frequency]) == 1:
            return values.most_common()[0][0]


    @property
    def range(self, error=False):
        """Returns the range of the values - the difference between the
        largest and smallest values."""

        return self.max - self.min


    def variance(self, population=False):
        """Returns the variance of the values - the mean square deviation of
        the values from the mean. The values really have to be numerical for
        this to be meaningful.

        You can elect to get the population variance if you wish, which uses `N`
        rather than `N - 1` as the denominator.

        :param bool population: If ``True``, the population variance will be\
        returned (default is ``False``).
        :rtype: ``float``"""

        return sum([
         (value - self.mean) ** 2 for value in self._values
        ]) / (self.length - (not population))


    def st_dev(self, population=False):
        """Returns the standard deviation of the values, the square root of
        the :py:meth:`.variance` and a measure of deviation from the mean.
        As with that metric, you need numerical data for this to be sensible.

        You can elect to get the population deviation if you wish, which uses
        `N` rather than `N - 1` as the denominator.

        :param bool population: If ``True``, the population deviation will be\
        returned (default is ``False``).
        :rtype: ``float``"""

        return sqrt(self.variance(population=population))


    def zscore(self, value, population=False):
        """The z-score of a value is how many standard deviations it is from
        the mean.

        :param value: The value who's z-score you want to know.
        :param bool population: If ``True``, the population deviation will be\
        used (default is ``False``)."""

        return (value - self.mean) / self.st_dev(population=population)


    def covariance_with(self, variable):
        """Returns the covariance between this Variable and another Variable.
        This is a measure of how the variance of the two series reflect each
        other, and is a measure of correlation.

        :param Variable variable: The other Variable. It must be the same\
        length as this one.
        :raises TypeError: if something other than a Variable is given.
        :raises ValueError: if Variables of different length are given."""

        if not isinstance(variable, Variable):
            raise TypeError("{} is not a Variable".format(str(variable)))
        if self.length != variable.length:
            raise ValueError(
             "length {} is not length {}".format(self.length, variable.length)
            )
        this_mean, other_mean = self.mean, variable.mean
        square_deviations = sum([(value - this_mean) * (other - other_mean)
         for value, other in zip(self._values, variable._values)])
        mean_square_deviation = square_deviations / (self.length - 1)
        return mean_square_deviation


    def correlation_with(self, variable):
        """Returns the correlation of one Variable with another. This differs
        from :py:meth:`covariance_with` in that it is normalised to be
        between -1 and 1, so the maginitude of the result is important, rather
        than just the sign as is the case with covariance.

        All the same requirements apply - the object given must be a Variable,
        and they must be the same length.

        :param Variable variable: The other Variable. It must be the same\
        length as this one."""

        covariance = self.covariance_with(variable)
        sd_product = self.st_dev() * variable.st_dev()
        return covariance / sd_product
