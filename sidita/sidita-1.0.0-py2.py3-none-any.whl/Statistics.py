####################################################################################################
#
# sidita - Simple Distributed Task Queue
# Copyright (C) 2018 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Implements statistical functions.

"""

####################################################################################################

__all__ = [
    'DataSetMoment',
    'WeightedDataSetMoment',
]

####################################################################################################

import math

####################################################################################################

class DataSetMoment:

    ##############################################

    def __init__(self, number_of_entries=0, sum_x=0, sum_x2=0, sum_x3=0, sum_x4=0):

        self._number_of_entries = number_of_entries
        self._sum_x = sum_x
        self._sum_x2 = sum_x2

        self._sum_x3 = sum_x3
        self._sum_x4 = sum_x4 # unused

    ##############################################

    def clone(self):

        return self.__class__(
            self._number_of_entries,
            self._sum_x,
            self._sum_x2,
            self._sum_x3,
            self._sum_x4,
        )

    ##############################################

    def to_json(self):

        return dict(
            number_of_entries=self._number_of_entries,
            sum_x=self._sum_x,
            sum_x2=self._sum_x2,
            sum_x3=self._sum_x3,
            sum_x4=self._sum_x4,
        )

    ##############################################

    @staticmethod
    def from_json(data):

        return DataSetMoment(**data)

    ##############################################

    def fill(self, x):

        self._number_of_entries += 1
        self._sum_x += x
        self._sum_x2 += x**2
        self._sum_x3 += x**3
        self._sum_x4 += x**4

    ##############################################

    def __iadd__(self, obj):

        self._number_of_entries += obj.number_of_entries
        self._sum_x += obj.sum_x
        self._sum_x2 += obj.sum_x2
        self._sum_x3 += obj.sum_x3
        self._sum_x4 += obj.sum_x4

        return self

    ##############################################

    def __bool__(self):
        return bool(self._number_of_entries)

    ##############################################

    @property
    def number_of_entries(self):
        return self._number_of_entries

    ##############################################

    @property
    def mean(self):
        return self._sum_x / self._number_of_entries

    ##############################################

    @property
    def biased_variance(self):
        return self._sum_x2 / self._number_of_entries - self.mean**2

    ##############################################

    @property
    def unbiased_variance(self):
        return self._number_of_entries / (self._number_of_entries -1) * self.biased_variance

    ##############################################

    @property
    def biased_standard_deviation(self):
        return math.sqrt(self.biased_variance)

    ##############################################

    @property
    def standard_deviation(self):
        return math.sqrt(self.unbiased_variance)

    ##############################################

    @property
    def skew(self):
        return ((self._sum_x3 / self._number_of_entries - 3*self.mean*self.biased_variance - self.mean**3)
                / (self.biased_variance*self.biased_standard_deviation))

    ##############################################

    @property
    def kurtosis(self):
        # Need an expansion in terms of sum_x**i
        return NotImplementedError

####################################################################################################

class WeightedDataSetMoment(object):

    ##############################################

    def __init__(self):

        self._sum_weight = 0
        self._sum_weight2 = 0
        self._sum_weight_x = 0
        self._sum_weight_x2 = 0
        self._sum_weight_x3 = 0
        self._sum_weight_x4 = 0

    ##############################################

    def fill(self, x, weight=1.):

        self._sum_weight += weight
        self._sum_weight2 += weight**2

        weight_x = weight * x
        self._sum_weight_x += weight_x
        self._sum_weight_x2 += weight_x**2
        self._sum_weight_x3 += weight_x**3
        self._sum_weight_x4 += weight_x**4

    ##############################################

    @property
    def number_of_effective_entries(self):
        return self._sum_weight**2 / self._sum_weight2

    ##############################################

    @property
    def mean(self):
        return self._sum_weight_x / self.number_of_effective_entries
